from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

BTN_H = dp(56)
NAV_TABS = (("subjects", "Предметы"), ("calendar", "Календарь"), ("notes", "Заметки"))


def app():
    return App.get_running_app()


class BaseScreen(Screen):
    """Общий каркас: верхняя панель (назад + заголовок), тело, нижние вкладки."""

    title = ""
    show_back = True   # кнопка «< Назад»
    show_nav = False   # нижние вкладки (только у главных экранов)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        bar = BoxLayout(size_hint_y=None, height=BTN_H, spacing=dp(8))
        if self.show_back:
            back = Button(text="< Назад", size_hint_x=None, width=dp(110))
            back.bind(on_release=lambda *_: app().back())
            bar.add_widget(back)
        self.title_label = Label(text=self.title, font_size="20sp")
        bar.add_widget(self.title_label)
        root.add_widget(bar)

        self.body = BoxLayout(orientation="vertical", spacing=dp(8))
        root.add_widget(self.body)

        if self.show_nav:
            root.add_widget(self._make_nav())
        self.add_widget(root)
        self.build_body()

    # --- что переопределять в экранах ---------------------------------
    def build_body(self):
        """Наполнить self.body кнопками и виджетами."""

    def on_context(self, **ctx):
        """Вызывается перед показом экрана, получает данные (например, subject)."""

    # --- помощники ----------------------------------------------------
    def set_title(self, text):
        self.title_label.text = text

    def button(self, text, on_release, parent=None):
        btn = Button(text=text, size_hint_y=None, height=BTN_H)
        btn.bind(on_release=lambda *_: on_release())
        (parent or self.body).add_widget(btn)
        return btn

    def placeholder(self, text):
        self.body.add_widget(Label(text=text))

    def spacer(self):
        self.body.add_widget(Widget())

    def go(self, name, **ctx):
        return lambda: app().open(name, **ctx)

    def scroll_list(self):
        grid = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        sv = ScrollView()
        sv.add_widget(grid)
        self.body.add_widget(sv)
        return grid

    def _make_nav(self):
        nav = BoxLayout(size_hint_y=None, height=BTN_H, spacing=dp(8))
        for name, label in NAV_TABS:
            b = Button(text=label)
            b.bind(on_release=lambda *_, n=name: app().open_root(n))
            nav.add_widget(b)
        return nav


class SubjectBoundScreen(BaseScreen):
    """Экран, относящийся к одному предмету (получает subject через контекст)."""

    title_fmt = "{subject}"

    def __init__(self, **kwargs):
        self.subject = ""
        super().__init__(**kwargs)

    def on_context(self, subject="", **ctx):
        self.subject = subject
        self.set_title(self.title_fmt.format(subject=subject))
