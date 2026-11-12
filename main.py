"""Точка входа: навигация между экранами приложения «Планировщик сессии»."""
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.utils import platform

from screens import register_screens
from theme import BG

Window.clearcolor = BG
if platform in ("android", "ios"):
    Window.softinput_mode = "below_target"  # клавиатура не перекрывает поле ввода
else:
    Window.size = (390, 844)  # размер телефона для запуска на компьютере


class PlannerApp(App):
    title = "Планировщик сессии"

    def build(self):
        self.history = []   # стек пройденных экранов: [(имя, контекст), ...]
        self._ctx = {}      # контекст текущего экрана (например, предмет)
        self.sm = ScreenManager(transition=SlideTransition())
        register_screens(self.sm)  # первый добавленный экран открывается первым
        self.sm.current_screen.refresh()
        Window.bind(on_keyboard=self._on_keyboard)
        return self.sm

    # --- навигация ---------------------------------------------------
    def open(self, name, **ctx):
        """Перейти на экран и запомнить текущий, чтобы можно было вернуться."""
        self.history.append((self.sm.current, dict(self._ctx)))
        self._show(name, ctx, "left")

    def open_root(self, name):
        """Переход по нижним вкладкам: история очищается."""
        self.history.clear()
        self._show(name, {}, "left")

    def back(self):
        """Назад на предыдущий экран. False, если возвращаться некуда."""
        if not self.history:
            return False
        name, ctx = self.history.pop()
        self._show(name, ctx, "right")
        return True

    def _show(self, name, ctx, direction):
        screen = self.sm.get_screen(name)
        screen.on_context(**ctx)
        self._ctx = ctx
        self.sm.transition.direction = direction
        self.sm.current = name

    def _on_keyboard(self, window, key, *args):
        # 27 = системная кнопка «Назад» на Android (и Esc на компьютере)
        if key == 27:
            return self.back()  # True — перехватили, False — закрыть приложение
        return False


if __name__ == "__main__":
    PlannerApp().run()
