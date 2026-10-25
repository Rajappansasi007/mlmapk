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
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.core.window import Window

from db_helper import (
    init_db, get_current_user, set_current_user, authenticate_user,
    create_user, load_user_data, save_user_data, get_all_songs_catalog,
    get_song_detail, update_song_meta_db, insert_song_submission,
    get_pending_submissions, resolve_submission_db
)
from core_engine import (
    clean_time_signature, transliterate_malayalam_to_english,
    convert_to_db_format, convert_from_db_format, get_keys_for_base,
    calculate_semitones, format_chords, CHORDS_SHARP
)

def make_combined_title(t1, t2):
    t1 = "" if not t1 or str(t1).lower() == 'nan' else str(t1).strip()
    t2 = "" if not t2 or str(t2).lower() == 'nan' else str(t2).strip()
    if t1 and t2:
        return f"{t1} / {t2}"
    return t1 or t2 or "Unknown Title"

# =============================================================================
# 1. NAVIGATION DRAWER / HEADER BAR
# =============================================================================
class TopBar(BoxLayout):
    def __init__(self, current_screen_name, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 55
        self.spacing = 4
        self.padding = [4, 4, 4, 4]

        btn_search = Button(text="Search", font_size='12sp')
        btn_search.bind(on_press=lambda x: self.navigate("search"))
        self.add_widget(btn_search)

        btn_fav = Button(text="Favs", font_size='12sp')
        btn_fav.bind(on_press=lambda x: self.navigate("favourites"))
        self.add_widget(btn_fav)

        btn_sched = Button(text="Schedule", font_size='12sp')
        btn_sched.bind(on_press=lambda x: self.navigate("schedule"))
        self.add_widget(btn_sched)

        btn_submit = Button(text="Submit", font_size='12sp')
        btn_submit.bind(on_press=lambda x: self.navigate("submit"))
        self.add_widget(btn_submit)

        app = App.get_running_app()
        if app.user_role == "admin":
            btn_admin = Button(text="Admin", font_size='12sp', background_color=(0.8, 0.4, 0.1, 1))
            btn_admin.bind(on_press=lambda x: self.navigate("admin"))
            self.add_widget(btn_admin)

        btn_logout = Button(text="Out", size_hint_x=0.6, font_size='12sp', background_color=(0.8, 0.2, 0.2, 1))
        btn_logout.bind(on_press=self.logout)
        self.add_widget(btn_logout)

    def navigate(self, target_name):
        app = App.get_running_app()
        app.sm.transition = SlideTransition(direction="left")
        app.sm.current = target_name

    def logout(self, instance):
        set_current_user(None)
        app = App.get_running_app()
        app.current_user = None
        app.user_role = "user"
        app.sm.transition = SlideTransition(direction="right")
        app.sm.current = "auth"

# =============================================================================
# 2. AUTHENTICATION SCREEN (LOGIN / REGISTER)
# =============================================================================
class AuthScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=25, spacing=15)

        self.layout.add_widget(Label(text="Song Lyrics Manager", font_size='24sp', bold=True, size_hint_y=0.2))
        
        self.mode_spinner = Spinner(text="Login", values=["Login", "Sign Up"], size_hint_y=0.1)
        self.layout.add_widget(self.mode_spinner)

        self.uname_input = TextInput(hint_text="Username", multiline=False, size_hint_y=0.12)
        self.layout.add_widget(self.uname_input)

        self.email_input = TextInput(hint_text="Email (Sign Up only)", multiline=False, size_hint_y=0.12)
        self.layout.add_widget(self.email_input)

        self.pwd_input = TextInput(hint_text="Password", password=True, multiline=False, size_hint_y=0.12)
        self.layout.add_widget(self.pwd_input)

        self.btn_submit = Button(text="Log In", size_hint_y=0.14, background_color=(0.2, 0.6, 0.8, 1))
        self.btn_submit.bind(on_press=self.handle_auth)
        self.layout.add_widget(self.btn_submit)

        self.lbl_msg = Label(text="", color=(1, 0.3, 0.3, 1), size_hint_y=0.1)
        self.layout.add_widget(self.lbl_msg)

        self.add_widget(self.layout)

    def handle_auth(self, instance):
        mode = self.mode_spinner.text
        uname = self.uname_input.text.strip()
        pwd = self.pwd_input.text.strip()
        email = self.email_input.text.strip()

        if not uname or not pwd:
            self.lbl_msg.text = "Please enter username and password."
            return

        if mode == "Login":
            user_record = authenticate_user(uname, pwd)
            if user_record:
                if user_record["status"] == "suspended":
                    self.lbl_msg.text = "Account is suspended by administrator."
                    return
                set_current_user(user_record["username"])
                app = App.get_running_app()
                app.set_logged_in_user(user_record["username"], user_record["role"])
            else:
                self.lbl_msg.text = "Invalid username or password."
        else:
            if not email:
                self.lbl_msg.text = "Please enter email for Sign Up."
                return
            ok, msg = create_user(uname, email, pwd)
            self.lbl_msg.text = msg
            if ok:
                self.mode_spinner.text = "Login"

# =============================================================================
# 3. SEARCH SCREEN (TITLE / KEY & SIGNATURE / TAGS)
# =============================================================================
class SearchScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active_tag = None

    def on_pre_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical')
        root.add_widget(TopBar("search"))

        # Sub-tab selector
        subtab_bar = BoxLayout(size_hint_y=None, height=45, spacing=4, padding=4)
        btn_t1 = Button(text="Title", font_size='13sp')
        btn_t1.bind(on_press=lambda x: self.set_subtab("Title"))
        btn_t2 = Button(text="Key/Sig", font_size='13sp')
        btn_t2.bind(on_press=lambda x: self.set_subtab("Key/Sig"))
        btn_t3 = Button(text="Tags", font_size='13sp')
        btn_t3.bind(on_press=lambda x: self.set_subtab("Tags"))
        subtab_bar.add_widget(btn_t1)
        subtab_bar.add_widget(btn_t2)
        subtab_bar.add_widget(btn_t3)
        root.add_widget(subtab_bar)

        self.content_area = BoxLayout(orientation='vertical')
        root.add_widget(self.content_area)
        self.add_widget(root)

        self.set_subtab("Title")

    def set_subtab(self, subtab_name):
        self.content_area.clear_widgets()
        catalog = get_all_songs_catalog()

        if subtab_name == "Title":
            # Song No and Title search inputs
            box_in = BoxLayout(size_hint_y=None, height=48, spacing=5, padding=4)
            inp_no = TextInput(hint_text="No", size_hint_x=0.25, multiline=False)
            inp_title = TextInput(hint_text="Search Title...", size_hint_x=0.75, multiline=False)
            box_in.add_widget(inp_no)
            box_in.add_widget(inp_title)
            self.content_area.add_widget(box_in)

            scroll = ScrollView()
            grid = GridLayout(cols=1, spacing=4, size_hint_y=None)
            grid.bind(minimum_height=grid.setter('height'))
            scroll.add_widget(grid)
            self.content_area.add_widget(scroll)

            def update_list(*args):
                grid.clear_widgets()
                q_no = inp_no.text.strip()
                q_txt = inp_title.text.strip().lower()

                for item in catalog:
                    s_id, t1, t2, vv, key, cho, sig, mm, tags = item
                    comb = make_combined_title(t1, t2)
                    vv_str = str(vv or '').replace('.0', '').strip()

                    if q_no and vv_str != q_no:
                        continue
                    if q_txt and q_txt not in comb.lower():
                        continue

                    btn = Button(
                        text=f"{comb}\nNo: {vv_str or '-'} | Key: {key or '-'} | Sig: {clean_time_signature(sig) or '-'}",
                        size_hint_y=None, height=65, halign="left"
                    )
                    btn.bind(size=btn.setter('text_size'))
                    btn.bind(on_press=lambda inst, sid=s_id: self.open_song(sid))
                    grid.add_widget(btn)

            inp_no.bind(text=update_list)
            inp_title.bind(text=update_list)
            update_list()

        elif subtab_name == "Key/Sig":
            keys = sorted(list({str(c[4]).strip() for c in catalog if c[4] and str(c[4]).lower() != 'nan'}))
            sigs = sorted(list({clean_time_signature(c[6]) for c in catalog if clean_time_signature(c[6])}))

            ctrl = BoxLayout(size_hint_y=None, height=48, spacing=5, padding=4)
            sp_key = Spinner(text="Any Key", values=["Any Key"] + keys, size_hint_x=0.5)
            sp_sig = Spinner(text="Any Sig", values=["Any Sig"] + sigs, size_hint_x=0.5)
            ctrl.add_widget(sp_key)
            ctrl.add_widget(sp_sig)
            self.content_area.add_widget(ctrl)

            scroll = ScrollView()
            grid = GridLayout(cols=1, spacing=4, size_hint_y=None)
            grid.bind(minimum_height=grid.setter('height'))
            scroll.add_widget(grid)
            self.content_area.add_widget(scroll)

            def filter_key_sig(*args):
                grid.clear_widgets()
                k_sel = sp_key.text
                s_sel = sp_sig.text
                for item in catalog:
                    s_id, t1, t2, vv, key, cho, sig, mm, tags = item
                    c_sig = clean_time_signature(sig)
                    if k_sel != "Any Key" and str(key).strip().lower() != k_sel.lower():
                        continue
                    if s_sel != "Any Sig" and c_sig.lower() != s_sel.lower():
                        continue
                    comb = make_combined_title(t1, t2)
                    btn = Button(text=f"{comb}\nKey: {key or '-'} | Sig: {c_sig or '-'}", size_hint_y=None, height=60, halign="left")
                    btn.bind(size=btn.setter('text_size'))
                    btn.bind(on_press=lambda inst, sid=s_id: self.open_song(sid))
                    grid.add_widget(btn)

            sp_key.bind(text=filter_key_sig)
            sp_sig.bind(text=filter_key_sig)
            filter_key_sig()

        elif subtab_name == "Tags":
            all_tags = set()
            for c in catalog:
                if c[8]:
                    for t in str(c[8]).split(','):
                        clean_t = t.strip()
                        if clean_t and clean_t.lower() != 'nan':
                            all_tags.add(clean_t)
            sorted_tags = sorted(list(all_tags))

            scroll = ScrollView()
            grid = GridLayout(cols=2, spacing=5, size_hint_y=None, padding=5)
            grid.bind(minimum_height=grid.setter('height'))
            scroll.add_widget(grid)
            self.content_area.add_widget(scroll)

            for tag in sorted_tags:
                btn = Button(text=f"🏷️ {tag}", size_hint_y=None, height=48)
                btn.bind(on_press=lambda inst, t=tag: self.view_tag_songs(t, catalog))
                grid.add_widget(btn)

    def view_tag_songs(self, tag, catalog):
        self.content_area.clear_widgets()
        hdr = BoxLayout(size_hint_y=None, height=45, spacing=5, padding=4)
        btn_back = Button(text="< All Tags", size_hint_x=0.3)
        btn_back.bind(on_press=lambda x: self.set_subtab("Tags"))
        lbl = Label(text=f"Tag: {tag}", bold=True, size_hint_x=0.7)
        hdr.add_widget(btn_back)
        hdr.add_widget(lbl)
        self.content_area.add_widget(hdr)

        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=4, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        scroll.add_widget(grid)
        self.content_area.add_widget(scroll)

        for item in catalog:
            s_id, t1, t2, vv, key, cho, sig, mm, tags = item
            if tags and tag.lower() in str(tags).lower():
                comb = make_combined_title(t1, t2)
                btn = Button(text=f"{comb}", size_hint_y=None, height=55, halign="left")
                btn.bind(size=btn.setter('text_size'))
                btn.bind(on_press=lambda inst, sid=s_id: self.open_song(sid))
                grid.add_widget(btn)

    def open_song(self, song_id):
        app = App.get_running_app()
        app.sm.get_screen("viewer").load_song(song_id)
        app.sm.transition = SlideTransition(direction="left")
        app.sm.current = "viewer"

# =============================================================================
# 4. UNIVERSAL SONG VIEWER SCREEN (LYRICS / CHORDS / TRANSPOSER / EDIT META)
# =============================================================================
class ViewerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.song_id = None
        self.song_record = None
        self.lyrics_choice = "Original"
        self.current_transposed_key = "C"

    def load_song(self, song_id):
        self.song_id = song_id
        self.song_record = get_song_detail(song_id)
        self.lyrics_choice = "Original"
        orig_key = self.song_record[6] or "C"
        self.current_transposed_key = orig_key
        self.render_screen()

    def render_screen(self):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical')
        root.add_widget(TopBar("viewer"))

        r = self.song_record
        # Columns: 0:id, 1:title1, 2:lyrics, 3:lyricseng, 4:title2, 5:choavbl, 6:key, 7:min_maj, 8:auth, 9:bpm, 10:rhythm, 11:timesig, 12:tags, 13:ytlink, 14:vvsongno, 15:chords, 16:pref_chord
        comb_title = make_combined_title(r[1], r[4])

        # Header Title bar with Projector & Fav & Sched
        hdr = BoxLayout(size_hint_y=None, height=50, spacing=5, padding=4)
        btn_back = Button(text="<", size_hint_x=0.15)
        btn_back.bind(on_press=lambda x: self.go_back())
        title_lbl = Label(text=comb_title, bold=True, size_hint_x=0.55, halign="center")
        title_lbl.bind(size=title_lbl.setter('text_size'))

        btn_proj = Button(text="📺", size_hint_x=0.15, background_color=(0.9, 0.5, 0.1, 1))
        btn_proj.bind(on_press=lambda x: self.open_presenter())

        app = App.get_running_app()
        is_fav = comb_title in app.user_favs
        btn_fav = Button(text="❤️" if is_fav else "🤍", size_hint_x=0.15)
        btn_fav.bind(on_press=lambda x: self.toggle_fav(comb_title, btn_fav))

        hdr.add_widget(btn_back)
        hdr.add_widget(title_lbl)
        hdr.add_widget(btn_proj)
        hdr.add_widget(btn_fav)
        root.add_widget(hdr)

        # Toolbar: Toggle Original/English Lyrics, Chords, and Transpose Spinner
        tool_bar = BoxLayout(size_hint_y=None, height=45, spacing=5, padding=4)
        btn_lang = Button(text=f"Lang: {self.lyrics_choice}", size_hint_x=0.35)
        btn_lang.bind(on_press=lambda x: self.toggle_language(btn_lang))
        tool_bar.add_widget(btn_lang)

        has_chords = bool(r[5] == 1 and r[15])
        if has_chords:
            orig_key = r[6] or "C"
            keys_opts, def_idx = get_keys_for_base(orig_key)
            sp_key = Spinner(text=self.current_transposed_key, values=keys_opts, size_hint_x=0.35)
            sp_key.bind(text=self.on_transpose)
            tool_bar.add_widget(sp_key)

        btn_add_sched = Button(text="📅 Sched", size_hint_x=0.3)
        btn_add_sched.bind(on_press=lambda x: self.add_to_schedule(comb_title))
        tool_bar.add_widget(btn_add_sched)
        root.add_widget(tool_bar)

        # Lyrics / Chords Display Scroll View
        scroll = ScrollView(size_hint_y=0.7)
        self.txt_display = Label(
            text="", font_size='16sp', size_hint_y=None, halign='left', valign='top', padding=[10, 10]
        )
        self.txt_display.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        self.txt_display.bind(texture_size=lambda s, h: s.setter('height')(s, h[1]))
        scroll.add_widget(self.txt_display)
        root.add_widget(scroll)

        # Metadata Summary footer
        meta_parts = []
        if r[14]: meta_parts.append(f"No: {r[14]}")
        if r[6]: meta_parts.append(f"Key: {r[6]}")
        if r[9]: meta_parts.append(f"BPM: {r[9]}")
        if r[11]: meta_parts.append(f"Sig: {clean_time_signature(r[11])}")
        pref = app.user_prefs.get(comb_title, r[16] or "")
        if pref: meta_parts.append(f"Pref: {pref}")

        meta_box = BoxLayout(size_hint_y=None, height=45, padding=4, spacing=5)
        meta_box.add_widget(Label(text=" | ".join(meta_parts), font_size='12sp', size_hint_x=0.85))
        btn_edit_meta = Button(text="✏️", size_hint_x=0.15)
        btn_edit_meta.bind(on_press=lambda x: self.show_meta_popup(comb_title))
        meta_box.add_widget(btn_edit_meta)
        root.add_widget(meta_box)

        self.add_widget(root)
        self.update_content_text()

    def toggle_language(self, btn):
        self.lyrics_choice = "English" if self.lyrics_choice == "Original" else "Original"
        btn.text = f"Lang: {self.lyrics_choice}"
        self.update_content_text()

    def on_transpose(self, spinner, text):
        self.current_transposed_key = text
        self.update_content_text()

    def update_content_text(self):
        r = self.song_record
        if r[5] == 1 and r[15]:
            orig_key = r[6] or "C"
            semitones = calculate_semitones(orig_key, self.current_transposed_key)
            clean_chords = convert_from_db_format(r[15])
            self.txt_display.text = format_chords(clean_chords, semitones)
        else:
            raw_lyr = r[3] if self.lyrics_choice == "English" else r[2]
            self.txt_display.text = convert_from_db_format(raw_lyr)

    def toggle_fav(self, comb_title, btn):
        app = App.get_running_app()
        if comb_title in app.user_favs:
            app.user_favs.remove(comb_title)
            btn.text = "🤍"
        else:
            app.user_favs.append(comb_title)
            btn.text = "❤️"
        save_user_data(app.current_user, app.user_favs, app.user_sched, app.user_prefs)

    def add_to_schedule(self, comb_title):
        app = App.get_running_app()
        if comb_title not in app.user_sched:
            app.user_sched.append(comb_title)
            save_user_data(app.current_user, app.user_favs, app.user_sched, app.user_prefs)

    def open_presenter(self):
        app = App.get_running_app()
        app.sm.get_screen("presenter").load_song_slides(self.song_record)
        app.sm.transition = SlideTransition(direction="left")
        app.sm.current = "presenter"

    def show_meta_popup(self, comb_title):
        app = App.get_running_app()
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        pref_input = TextInput(hint_text="Personal Preferred Chord (e.g. Em)", text=app.user_prefs.get(comb_title, ""), multiline=False)
        content.add_widget(pref_input)

        if app.user_role == "admin":
            r = self.song_record
            key_in = TextInput(hint_text="Key", text=str(r[6] or ""), multiline=False)
            bpm_in = TextInput(hint_text="BPM", text=str(r[9] or ""), multiline=False)
            sig_in = TextInput(hint_text="Time Signature", text=clean_time_signature(r[11]), multiline=False)
            content.add_widget(key_in)
            content.add_widget(bpm_in)
            content.add_widget(sig_in)

        btn_save = Button(text="Save Metadata", size_hint_y=None, height=45)
        content.add_widget(btn_save)

        popup = Popup(title="Edit Metadata", content=content, size_hint=(0.9, 0.6))

        def save_meta(instance):
            if pref_input.text.strip():
                app.user_prefs[comb_title] = pref_input.text.strip()
                save_user_data(app.current_user, app.user_favs, app.user_sched, app.user_prefs)
            if app.user_role == "admin":
                update_song_meta_db(self.song_id, key_in.text.strip(), bpm_in.text.strip(), None, sig_in.text.strip(), None, None)
                self.song_record = get_song_detail(self.song_id)
            popup.dismiss()
            self.render_screen()

        btn_save.bind(on_press=save_meta)
        popup.open()

    def go_back(self):
        app = App.get_running_app()
        app.sm.transition = SlideTransition(direction="right")
        app.sm.current = "search"

# =============================================================================
# 5. FAVOURITES SCREEN
# =============================================================================
class FavouritesScreen(Screen):
    def on_pre_enter(self):
        self.render_ui()

    def render_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical')
        root.add_widget(TopBar("favourites"))

        app = App.get_running_app()
        hdr = BoxLayout(size_hint_y=None, height=45, padding=4)
        hdr.add_widget(Label(text=f"❤️ {len(app.user_favs)} Favourite Song(s)", bold=True, size_hint_x=0.7))
        btn_clear = Button(text="Clear All", size_hint_x=0.3, background_color=(0.8, 0.2, 0.2, 1))
        btn_clear.bind(on_press=self.clear_all)
        hdr.add_widget(btn_clear)
        root.add_widget(hdr)

        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=4, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        scroll.add_widget(grid)
        root.add_widget(scroll)

        catalog = get_all_songs_catalog()
        song_map = {make_combined_title(c[1], c[2]): c[0] for c in catalog}

        for song in app.user_favs:
            row = BoxLayout(size_hint_y=None, height=50, spacing=4, padding=2)
            btn_title = Button(text=song, halign="left", size_hint_x=0.8)
            btn_title.bind(size=btn_title.setter('text_size'))
            if song in song_map:
                btn_title.bind(on_press=lambda inst, sid=song_map[song]: self.open_song(sid))
            btn_del = Button(text="❌", size_hint_x=0.2, background_color=(0.8, 0.2, 0.2, 1))
            btn_del.bind(on_press=lambda inst, s=song: self.remove_fav(s))
            row.add_widget(btn_title)
            row.add_widget(btn_del)
            grid.add_widget(row)

        self.add_widget(root)

    def remove_fav(self, song):
        app = App.get_running_app()
        if song in app.user_favs:
            app.user_favs.remove(song)
            save_user_data(app.current_user, app.user_favs, app.user_sched, app.user_prefs)
            self.render_ui()

    def clear_all(self, instance):
        app = App.get_running_app()
        app.user_favs = []
        save_user_data(app.current_user, app.user_favs, app.user_sched, app.user_prefs)
        self.render_ui()

    def open_song(self, song_id):
        app = App.get_running_app()
        app.sm.get_screen("viewer").load_song(song_id)
        app.sm.transition = SlideTransition(direction="left")
        app.sm.current = "viewer"

# =============================================================================
# 6. SCHEDULE BUILDER & WHATSAPP SHARING
# =============================================================================
class ScheduleScreen(Screen):
    def on_pre_enter(self):
        self.render_ui()

    def render_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical')
        root.add_widget(TopBar("schedule"))

        app = App.get_running_app()
        ctrl = BoxLayout(size_hint_y=None, height=48, padding=4, spacing=4)
        btn_share = Button(text="💬 Share via WhatsApp", background_color=(0.1, 0.7, 0.3, 1), size_hint_x=0.7)
        btn_share.bind(on_press=self.share_whatsapp)
        btn_clear = Button(text="🗑️ Clear", size_hint_x=0.3, background_color=(0.8, 0.2, 0.2, 1))
        btn_clear.bind(on_press=self.clear_sched)
        ctrl.add_widget(btn_share)
        ctrl.add_widget(btn_clear)
        root.add_widget(ctrl)

        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=5)
        grid.bind(minimum_height=grid.setter('height'))
        scroll.add_widget(grid)
        root.add_widget(scroll)

        for i, song in enumerate(app.user_sched):
            row = BoxLayout(size_hint_y=None, height=52, spacing=4)
            btn_up = Button(text="▲", size_hint_x=0.1, disabled=(i == 0))
            btn_up.bind(on_press=lambda inst, idx=i: self.move_item(idx, -1))
            btn_down = Button(text="▼", size_hint_x=0.1, disabled=(i == len(app.user_sched) - 1))
            btn_down.bind(on_press=lambda inst, idx=i: self.move_item(idx, 1))

            lbl = Label(text=f"{i+1}. {song}", halign="left", size_hint_x=0.55)
            lbl.bind(size=lbl.setter('text_size'))

            pref_txt = TextInput(hint_text="Chord", text=app.user_prefs.get(song, ""), size_hint_x=0.15, multiline=False)
            def on_chord_edit(inst, s=song):
                app.user_prefs[s] = inst.text.strip()
                save_user_data(app.current_user, app.user_favs, app.user_sched, app.user_prefs)
            pref_txt.bind(text=on_chord_edit)

            btn_rem = Button(text="❌", size_hint_x=0.1, background_color=(0.8, 0.2, 0.2, 1))
            btn_rem.bind(on_press=lambda inst, idx=i: self.remove_item(idx))

            row.add_widget(btn_up)
            row.add_widget(btn_down)
            row.add_widget(lbl)
            row.add_widget(pref_txt)
            row.add_widget(btn_rem)
            grid.add_widget(row)

        self.add_widget(root)

    def move_item(self, idx, offset):
        app = App.get_running_app()
        new_idx = idx + offset
        app.user_sched[idx], app.user_sched[new_idx] = app.user_sched[new_idx], app.user_sched[idx]
        save_user_data(app.current_user, app.user_favs, app.user_sched, app.user_prefs)
        self.render_ui()

    def remove_item(self, idx):
        app = App.get_running_app()
        app.user_sched.pop(idx)
        save_user_data(app.current_user, app.user_favs, app.user_sched, app.user_prefs)
        self.render_ui()

    def clear_sched(self, instance):
        app = App.get_running_app()
        app.user_sched = []
        save_user_data(app.current_user, app.user_favs, app.user_sched, app.user_prefs)
        self.render_ui()

    def share_whatsapp(self, instance):
        app = App.get_running_app()
        if not app.user_sched:
            return
        lines = [f"*{app.current_user}'s Service Schedule*"]
        catalog = get_all_songs_catalog()
        cat_map = {make_combined_title(c[1], c[2]): c for c in catalog}

        for i, song in enumerate(app.user_sched):
            meta_details = []
            if song in cat_map:
                c = cat_map[song]
                if c[3]: meta_details.append(f"No: {c[3]}")
                if c[6]: meta_details.append(f"Sig: {clean_time_signature(c[6])}")
            pref = app.user_prefs.get(song, "")
            if pref: meta_details.append(f"Chord: {pref}")
            meta_str = f" ({', '.join(meta_details)})" if meta_details else ""
            lines.append(f"{i+1}. {song}{meta_str}")

        text = urllib.parse.quote("\n".join(lines))
        url = f"https://wa.me/?text={text}"
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

# =============================================================================
# 7. PRESENTER PROJECTION SCREEN
# =============================================================================
class PresenterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.slides = []
        self.cur_idx = 0

        layout = BoxLayout(orientation='vertical')
        top = BoxLayout(size_hint_y=None, height=45)
        btn_exit = Button(text="Exit Projection", size_hint_x=0.35)
        btn_exit.bind(on_press=self.exit_presenter)
        self.lbl_status = Label(text="Slide 0 of 0", size_hint_x=0.65)
        top.add_widget(btn_exit)
        top.add_widget(self.lbl_status)
        layout.add_widget(top)

        self.slide_text = Label(text="", font_size='28sp', bold=True, halign='center', valign='middle')
        self.slide_text.bind(size=self.slide_text.setter('text_size'))
        layout.add_widget(self.slide_text)

        ctrl = BoxLayout(size_hint_y=None, height=55, spacing=10, padding=5)
        btn_prev = Button(text="<< Prev")
        btn_prev.bind(on_press=self.prev_slide)
        btn_next = Button(text="Next >>")
        btn_next.bind(on_press=self.next_slide)
        ctrl.add_widget(btn_prev)
        ctrl.add_widget(btn_next)
        layout.add_widget(ctrl)

        self.add_widget(layout)

    def load_song_slides(self, song_record):
        raw_orig = song_record[2] or ""
        self.slides = [s.strip().replace('<BR>', '\n') for s in raw_orig.split('<slide>') if s.strip()]
        self.cur_idx = 0
        self.update_slide()

    def update_slide(self):
        if not self.slides:
            self.slide_text.text = "No slides available."
            self.lbl_status.text = "Slide 0 of 0"
            return
        self.slide_text.text = self.slides[self.cur_idx]
        self.lbl_status.text = f"Slide {self.cur_idx + 1} of {len(self.slides)}"

    def next_slide(self, instance):
        if self.cur_idx < len(self.slides) - 1:
            self.cur_idx += 1
            self.update_slide()

    def prev_slide(self, instance):
        if self.cur_idx > 0:
            self.cur_idx -= 1
            self.update_slide()

    def exit_presenter(self, instance):
        app = App.get_running_app()
        app.sm.transition = SlideTransition(direction="right")
        app.sm.current = "viewer"

# =============================================================================
# 8. SUBMIT SONG / CHORDS SCREEN
# =============================================================================
class SubmitScreen(Screen):
    def on_pre_enter(self):
        self.render_ui()

    def render_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical')
        root.add_widget(TopBar("submit"))

        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8, padding=10)
        layout.bind(minimum_height=layout.setter('height'))

        layout.add_widget(Label(text="📝 Submit New Lyrics / Chords", bold=True, font_size='18sp', size_hint_y=None, height=35))
        
        t1_in = TextInput(hint_text="Malayalam Title *", multiline=False, size_hint_y=None, height=45)
        t2_in = TextInput(hint_text="English Title", multiline=False, size_hint_y=None, height=45)
        lyr_in = TextInput(hint_text="Type Malayalam lyrics here (leave blank lines between stanzas)...", size_hint_y=None, height=140)
        chords_in = TextInput(hint_text="Insert Chords with brackets [Am]...", size_hint_y=None, height=140)
        
        key_in = TextInput(hint_text="Key (e.g. Am)", multiline=False, size_hint_y=None, height=45)
        sig_in = TextInput(hint_text="Time Signature (e.g. 4/4)", multiline=False, size_hint_y=None, height=45)
        bpm_in = TextInput(hint_text="BPM (e.g. 100)", multiline=False, size_hint_y=None, height=45)
        auth_in = TextInput(hint_text="Author", multiline=False, size_hint_y=None, height=45)

        layout.add_widget(t1_in)
        layout.add_widget(t2_in)
        layout.add_widget(lyr_in)
        layout.add_widget(chords_in)
        layout.add_widget(key_in)
        layout.add_widget(sig_in)
        layout.add_widget(bpm_in)
        layout.add_widget(auth_in)

        btn_send = Button(text="Submit for Admin Approval", size_hint_y=None, height=50, background_color=(0.2, 0.6, 0.8, 1))
        layout.add_widget(btn_send)

        lbl_res = Label(text="", size_hint_y=None, height=30)
        layout.add_widget(lbl_res)

        def submit_payload(instance):
            if not t1_in.text.strip() or not lyr_in.text.strip():
                lbl_res.text = "Please fill in title and lyrics."
                return
            app = App.get_running_app()
            payload = {
                "submission_type": "new_song",
                "submitted_by": app.current_user,
                "title1": t1_in.text.strip(),
                "title2": t2_in.text.strip() or transliterate_malayalam_to_english(t1_in.text.strip()),
                "raw_lyrics": lyr_in.text.strip(),
                "raw_chords": chords_in.text.strip(),
                "meta_key": key_in.text.strip(),
                "meta_sig": sig_in.text.strip(),
                "meta_bpm": bpm_in.text.strip(),
                "meta_auth": auth_in.text.strip(),
                "admin_comments": ""
            }
            insert_song_submission(payload)
            lbl_res.text = "Submission queued for administrator review!"

        btn_send.bind(on_press=submit_payload)
        scroll.add_widget(layout)
        root.add_widget(scroll)
        self.add_widget(root)

# =============================================================================
# 9. ADMIN PANEL SCREEN
# =============================================================================
class AdminScreen(Screen):
    def on_pre_enter(self):
        self.render_ui()

    def render_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical')
        root.add_widget(TopBar("admin"))

        root.add_widget(Label(text="🛡️ Admin Approval Queue", bold=True, font_size='18sp', size_hint_y=None, height=40))

        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=6, size_hint_y=None, padding=8)
        grid.bind(minimum_height=grid.setter('height'))
        scroll.add_widget(grid)
        root.add_widget(scroll)

        subs = get_pending_submissions()
        if not subs:
            grid.add_widget(Label(text="No pending submissions to review.", size_hint_y=None, height=50))
        else:
            for s in subs:
                s_id, s_type, s_user, t1, t2, s_title, raw_lyr, raw_cho = s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7]
                box = BoxLayout(orientation='vertical', size_hint_y=None, height=110, padding=5)
                box.add_widget(Label(text=f"New Song: {t1} ({t2}) — by {s_user}", bold=True))
                
                btns = BoxLayout(spacing=10)
                btn_appr = Button(text="✅ Approve", background_color=(0.1, 0.7, 0.3, 1))
                btn_appr.bind(on_press=lambda inst, sid=s_id: self.resolve(sid, "approved"))
                btn_rej = Button(text="❌ Reject", background_color=(0.8, 0.2, 0.2, 1))
                btn_rej.bind(on_press=lambda inst, sid=s_id: self.resolve(sid, "rejected"))
                btns.add_widget(btn_appr)
                btns.add_widget(btn_rej)
                box.add_widget(btns)
                grid.add_widget(box)

        self.add_widget(root)

    def resolve(self, sub_id, status_val):
        resolve_submission_db(sub_id, status_val)
        self.render_ui()

# =============================================================================
# APPLICATION CONTROLLER
# =============================================================================
class SongApp(App):
    def build(self):
        init_db("preloaded_data.sql")
        self.current_user = get_current_user()
        self.user_favs = []
        self.user_sched = []
        self.user_prefs = {}
        self.user_role = "user"

        self.sm = ScreenManager()
        self.sm.add_widget(AuthScreen(name="auth"))
        self.sm.add_widget(SearchScreen(name="search"))
        self.sm.add_widget(ViewerScreen(name="viewer"))
        self.sm.add_widget(FavouritesScreen(name="favourites"))
        self.sm.add_widget(ScheduleScreen(name="schedule"))
        self.sm.add_widget(PresenterScreen(name="presenter"))
        self.sm.add_widget(SubmitScreen(name="submit"))
        self.sm.add_widget(AdminScreen(name="admin"))

        if self.current_user:
            favs, sched, prefs, role = load_user_data(self.current_user)
            self.user_favs = favs
            self.user_sched = sched
            self.user_prefs = prefs
            self.user_role = role
            self.sm.current = "search"
        else:
            self.sm.current = "auth"

        return self.sm

    def set_logged_in_user(self, username, role):
        self.current_user = username
        self.user_role = role
        favs, sched, prefs, _ = load_user_data(username)
        self.user_favs = favs
        self.user_sched = sched
        self.user_prefs = prefs
        self.sm.transition = SlideTransition(direction="left")
        self.sm.current = "search"

if __name__ == "__main__":
    SongApp().run()
