from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from theme import AC, AC_SOFT, CARD, INK, LINE, MUTED
from widgets import Card, PillButton, Text

NAV_TABS = (("subjects", "Предметы"), ("calendar", "Календарь"), ("notes", "Заметки"))


def app():
    return App.get_running_app()


class BaseScreen(Screen):
    """Каркас: шапка (назад, подзаголовок, заголовок), тело, нижние вкладки.

    Экран перестраивается при каждом показе (refresh), поэтому всегда
    показывает актуальные данные из store.
    """

    title = ""
    subtitle = ""
    show_back = False
    show_nav = True
    active_tab = None   # какая вкладка подсвечена: subjects / calendar / notes

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical")

        self.head = BoxLayout(orientation="vertical", size_hint_y=None,
                              padding=[dp(20), dp(16), dp(20), dp(6)])
        if self.show_back:
            row = BoxLayout(size_hint_y=None, height=dp(44))
            back = PillButton(text="<", fg=INK, font_size="22sp", size_hint=(None, None),
                              size=(dp(44), dp(44)))
            back.bind(on_release=lambda *_: app().back())
            row.add_widget(back)
            row.add_widget(Widget())
            self.head.add_widget(row)
        self.subtitle_label = Text(fs=14, color=MUTED, bold=True, size_hint_y=None, height=dp(20))
        self.title_label = Text(fs=28, bold=True, size_hint_y=None, height=dp(40))
        self.head.add_widget(self.subtitle_label)
        self.head.add_widget(self.title_label)
        self.head.height = dp(22) + dp(60) + (dp(44) if self.show_back else 0)
        root.add_widget(self.head)

        self.body = BoxLayout(orientation="vertical", spacing=dp(10),
                              padding=[dp(16), dp(4), dp(16), dp(8)])
        root.add_widget(self.body)

        self.nav_buttons = {}
        if self.show_nav:
            root.add_widget(self._make_nav())
        self.add_widget(root)

    # --- что переопределять в экранах ---------------------------------
    def build_body(self):
        """Наполнить self.body."""

    def on_context(self, **ctx):
        """Получить данные перед показом (например, subject, tab)."""

    # --- жизненный цикл -------------------------------------------------
    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        self.title_label.text = self.title
        self.subtitle_label.text = self.subtitle
        self.body.clear_widgets()
        self.build_body()
        for name, btn in self.nav_buttons.items():
            on = name == self.active_tab
            btn.set_style(bg=AC_SOFT if on else None, fg=AC if on else MUTED)

    # --- помощники ----------------------------------------------------
    def scroll(self):
        """Прокручиваемая колонка внутри body; возвращает контейнер для виджетов."""
        sv = ScrollView(do_scroll_x=False, bar_width=0)
        grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None,
                          padding=[0, 0, 0, dp(12)])
        grid.bind(minimum_height=grid.setter("height"))
        sv.add_widget(grid)
        self.body.add_widget(sv)
        return grid

    def _make_nav(self):
        nav = Card(bg=CARD, radius=0, outline=None, padding=[dp(12), dp(14)], spacing=dp(8),
                   size_hint_y=None, height=dp(76))
        for name, label in NAV_TABS:
            b = PillButton(text=label, font_size="13sp")
            b.bind(on_release=lambda *_, n=name: app().open_root(n))
            nav.add_widget(b)
            self.nav_buttons[name] = b
        return nav
