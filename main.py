from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from database import init_db, fetch_songs, add_song
from transliteration import transliterate_malayalam_to_english

class SongListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Search Bar
        self.search_input = TextInput(hint_text="Search title, tags, or lyrics...", size_hint_y=None, height=50)
        self.search_input.bind(text=self.on_search)
        layout.add_widget(self.search_input)

        # Results Display
        self.results_layout = BoxLayout(orientation='vertical', spacing=5)
        layout.add_widget(self.results_layout)

        self.add_widget(layout)
        self.refresh_list()

    def refresh_list(self, query=""):
        self.results_layout.clear_widgets()
        songs = fetch_songs(query)
        for song in songs[:10]: # Top 10 results
            title = song.get('title1') or song.get('title2') or 'Untitled'
            btn = Button(text=title, size_hint_y=None, height=45)
            btn.bind(on_release=lambda x, s=song: self.open_song(s))
            self.results_layout.add_widget(btn)

    def on_search(self, instance, value):
        self.refresh_list(value)

    def open_song(self, song):
        detail_screen = self.manager.get_screen('detail')
        detail_screen.load_song(song)
        self.manager.current = 'detail'

class SongDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.title_label = Label(text="", size_hint_y=None, height=40, font_size='18sp')
        self.lyrics_display = TextInput(text="", readonly=True, multiline=True)
        
        back_btn = Button(text="< Back", size_hint_y=None, height=45)
        back_btn.bind(on_release=self.go_back)

        self.layout.add_widget(self.title_label)
        self.layout.add_widget(self.lyrics_display)
        self.layout.add_widget(back_btn)
        self.add_widget(self.layout)

    def load_song(self, song):
        self.title_label.text = song.get('title1') or "Lyrics"
        lyrics = song.get('lyrics') or ""
        transliterated = transliterate_malayalam_to_english(lyrics)
        self.lyrics_display.text = f"{lyrics}\n\n--- Manglish ---\n\n{transliterated}"

    def go_back(self, *args):
        self.manager.current = 'song_list'

class LyricsApp(App):
    def build(self):
        init_db()
        sm = ScreenManager()
        sm.add_widget(SongListScreen(name='song_list'))
        sm.add_widget(SongDetailScreen(name='detail'))
        return sm

if __name__ == "__main__":
    LyricsApp().run()
