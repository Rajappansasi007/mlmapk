import os
import urllib.parse
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.core.window import Window

from db_helper import init_db, get_all_songs, get_song_by_id, load_user_state, save_user_state
from core_engine import format_chords, convert_from_db_format, calculate_semitones, CHORDS_SHARP

CURRENT_USER = "admin"
user_favs, user_sched, user_prefs = [], [], {}

class SearchScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        
        # Header / Nav
        nav = BoxLayout(size_hint_y=0.08, spacing=5)
        btn_sched = Button(text="Schedule", background_color=(0.2, 0.6, 0.8, 1))
        btn_sched.bind(on_press=lambda x: self.switch_screen("schedule"))
        nav.add_widget(btn_sched)
        layout.add_widget(nav)

        # Search Bar
        self.search_input = TextInput(hint_text="Search Title or Song No...", multiline=False, size_hint_y=0.08)
        self.search_input.bind(text=self.filter_songs)
        layout.add_widget(self.search_input)

        # Song List Scroll
        self.scroll = ScrollView(size_hint_y=0.84)
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)

        self.add_widget(layout)

    def on_pre_enter(self):
        self.filter_songs(None, self.search_input.text)

    def filter_songs(self, instance, text):
        self.grid.clear_widgets()
        songs = get_all_songs(text)
        for s in songs:
            s_id, t1, t2, vv, key, cho, sig = s
            display_title = f"{t1 or ''} / {t2 or ''}"
            subtext = f"No: {vv or '-'} | Key: {key or '-'} | Sig: {sig or '-'}"
            
            btn = Button(
                text=f"{display_title}\n{subtext}",
                size_hint_y=None,
                height=70,
                halign="left",
                valign="middle"
            )
            btn.bind(size=btn.setter('text_size'))
            btn.bind(on_press=lambda inst, sid=s_id: self.open_song(sid))
            self.grid.add_widget(btn)

    def open_song(self, song_id):
        self.manager.get_screen("viewer").load_song(song_id)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "viewer"

    def switch_screen(self, screen_name):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = screen_name


class ViewerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.song_data = None
        self.current_key = "C"

        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        
        # Action Bar
        top_bar = BoxLayout(size_hint_y=0.08, spacing=5)
        btn_back = Button(text="< Back", size_hint_x=0.25)
        btn_back.bind(on_press=self.go_back)
        self.title_lbl = Label(text="", bold=True, size_hint_x=0.55)
        self.btn_present = Button(text="Project", size_hint_x=0.2, background_color=(0.9, 0.5, 0.1, 1))
        self.btn_present.bind(on_press=self.go_presenter)
        top_bar.add_widget(btn_back)
        top_bar.add_widget(self.title_lbl)
        top_bar.add_widget(self.btn_present)
        self.layout.add_widget(top_bar)

        # Transposer Bar
        self.tr_bar = BoxLayout(size_hint_y=0.08, spacing=5)
        self.tr_bar.add_widget(Label(text="Key:", size_hint_x=0.2))
        self.key_spinner = Spinner(text="C", values=CHORDS_SHARP, size_hint_x=0.5)
        self.key_spinner.bind(text=self.on_key_change)
        self.tr_bar.add_widget(self.key_spinner)
        
        self.btn_sched_toggle = Button(text="+ Schedule", size_hint_x=0.3)
        self.btn_sched_toggle.bind(on_press=self.toggle_schedule)
        self.tr_bar.add_widget(self.btn_sched_toggle)
        self.layout.add_widget(self.tr_bar)

        # Text View Area
        self.scroll = ScrollView(size_hint_y=0.84)
        self.content_lbl = Label(
            text="", 
            size_hint_y=None, 
            font_size='16sp', 
            halign='left', 
            valign='top'
        )
        self.content_lbl.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        self.content_lbl.bind(texture_size=lambda s, h: s.setter('height')(s, h[1]))
        self.scroll.add_widget(self.content_lbl)
        self.layout.add_widget(self.scroll)

        self.add_widget(self.layout)

    def load_song(self, song_id):
        self.song_data = get_song_by_id(song_id)
        # 1: title1, 2: lyrics, 4: title2, 6: key, 15: chords
        t1, t2, base_key = self.song_data[1], self.song_data[4], self.song_data[6] or "C"
        self.title_lbl.text = f"{t1 or ''}"
        self.current_key = base_key
        self.key_spinner.text = base_key
        self.render_text()

    def on_key_change(self, spinner, text):
        self.current_key = text
        self.render_text()

    def render_text(self):
        if not self.song_data:
            return
        orig_key = self.song_data[6] or "C"
        raw_chords = self.song_data[15]
        if raw_chords:
            semis = calculate_semitones(orig_key, self.current_key)
            clean = raw_chords.replace('<BR>', '\n').replace('<slide>', '\n\n')
            self.content_lbl.text = format_chords(clean, semis)
        else:
            raw_lyrics = self.song_data[2] or self.song_data[3] or ""
            self.content_lbl.text = convert_from_db_format(raw_lyrics)

    def toggle_schedule(self, instance):
        comb_title = f"{self.song_data[1]} / {self.song_data[4]}"
        if comb_title not in user_sched:
            user_sched.append(comb_title)
            save_user_state(CURRENT_USER, user_favs, user_sched, user_prefs)
            self.btn_sched_toggle.text = "In Sched"

    def go_presenter(self, instance):
        self.manager.get_screen("presenter").load_slides(self.song_data)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "presenter"

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "search"


class ScheduleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        
        # Header
        nav = BoxLayout(size_hint_y=0.08, spacing=5)
        btn_back = Button(text="< Catalog", size_hint_x=0.3)
        btn_back.bind(on_press=self.go_back)
        btn_share = Button(text="WhatsApp Share", size_hint_x=0.7, background_color=(0.1, 0.7, 0.3, 1))
        btn_share.bind(on_press=self.share_whatsapp)
        nav.add_widget(btn_back)
        nav.add_widget(btn_share)
        self.layout.add_widget(nav)

        self.scroll = ScrollView(size_hint_y=0.92)
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        self.layout.add_widget(self.scroll)

        self.add_widget(self.layout)

    def on_pre_enter(self):
        self.refresh_list()

    def refresh_list(self):
        self.grid.clear_widgets()
        for idx, song in enumerate(user_sched):
            row = BoxLayout(size_hint_y=None, height=50, spacing=5)
            row.add_widget(Label(text=f"{idx+1}. {song}", halign='left', size_hint_x=0.8))
            btn_del = Button(text="X", size_hint_x=0.2, background_color=(0.9, 0.2, 0.2, 1))
            btn_del.bind(on_press=lambda inst, i=idx: self.remove_item(i))
            row.add_widget(btn_del)
            self.grid.add_widget(row)

    def remove_item(self, idx):
        user_sched.pop(idx)
        save_user_state(CURRENT_USER, user_favs, user_sched, user_prefs)
        self.refresh_list()

    def share_whatsapp(self, instance):
        if not user_sched:
            return
        lines = ["*Service Setlist*"]
        for idx, song in enumerate(user_sched):
            lines.append(f"{idx+1}. {song}")
        text = urllib.parse.quote("\n".join(lines))
        url = f"https://wa.me/?text={text}"
        
        # Launch Android Native Intent if on mobile, else webbrowser fallback
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
            PythonActivity.mActivity.startActivity(intent)
        except Exception:
            import webbrowser
            webbrowser.open(url)

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "search"


class PresenterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.slides = []
        self.current_idx = 0

        layout = BoxLayout(orientation='vertical')
        
        # Top Exit Fullscreen bar
        top_bar = BoxLayout(size_hint_y=0.08)
        btn_exit = Button(text="Exit Projection", size_hint_x=0.3)
        btn_exit.bind(on_press=self.exit_presentation)
        self.lbl_status = Label(text="Slide 0 of 0", size_hint_x=0.7)
        top_bar.add_widget(btn_exit)
        top_bar.add_widget(self.lbl_status)
        layout.add_widget(top_bar)

        # Full Slide View Area
        self.slide_lbl = Label(text="", font_size='26sp', bold=True, halign='center', valign='middle')
        self.slide_lbl.bind(size=self.slide_lbl.setter('text_size'))
        layout.add_widget(self.slide_lbl)

        # Bottom Navigator
        controls = BoxLayout(size_hint_y=0.1, spacing=10, padding=5)
        btn_prev = Button(text="<< Prev")
        btn_prev.bind(on_press=self.prev_slide)
        btn_next = Button(text="Next >>")
        btn_next.bind(on_press=self.next_slide)
        controls.add_widget(btn_prev)
        controls.add_widget(btn_next)
        layout.add_widget(controls)

        self.add_widget(layout)

    def load_slides(self, song_data):
        raw_orig = song_data[2] or ""
        self.slides = [s.strip().replace('<BR>', '\n') for s in raw_orig.split('<slide>') if s.strip()]
        self.current_idx = 0
        self.update_slide()

    def update_slide(self):
        if not self.slides:
            self.slide_lbl.text = "No slides available."
            self.lbl_status.text = "Slide 0 of 0"
            return
        self.slide_lbl.text = self.slides[self.current_idx]
        self.lbl_status.text = f"Slide {self.current_idx + 1} of {len(self.slides)}"

    def next_slide(self, instance):
        if self.current_idx < len(self.slides) - 1:
            self.current_idx += 1
            self.update_slide()

    def prev_slide(self, instance):
        if self.current_idx > 0:
            self.current_idx -= 1
            self.update_slide()

    def exit_presentation(self, instance):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "viewer"


class SongApp(App):
    def build(self):
        global user_favs, user_sched, user_prefs
        init_db("preloaded_data.sql")
        user_favs, user_sched, user_prefs = load_user_state(CURRENT_USER)

        sm = ScreenManager()
        sm.add_widget(SearchScreen(name="search"))
        sm.add_widget(ViewerScreen(name="viewer"))
        sm.add_widget(ScheduleScreen(name="schedule"))
        sm.add_widget(PresenterScreen(name="presenter"))
        return sm

if __name__ == "__main__":
    SongApp().run()
