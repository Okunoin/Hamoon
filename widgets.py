"""Свои виджеты по макету: карточки, кнопки-«таблетки», шкала, тумблер, ячейка дня."""
from kivy.graphics import Color, Ellipse, Line, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.properties import BooleanProperty, ListProperty, NumericProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from theme import AC, CARD, INK, MUTED, OFF, PRIORITY, TRACK, WHITE


class Text(Label):
    """Подпись с выравниванием внутри своего размера."""

    def __init__(self, text="", fs=15, bold=False, color=INK, halign="left", valign="middle", **kw):
        super().__init__(text=text, font_size=sp(fs), bold=bold, color=color,
                         halign=halign, valign=valign, **kw)
        self.bind(size=self._sync)
        self._sync()

    def _sync(self, *_):
        self.text_size = self.size


class Card(BoxLayout):
    """Контейнер со скруглённым фоном (и необязательной рамкой)."""

    def __init__(self, bg=CARD, radius=None, outline=None, **kw):
        super().__init__(**kw)
        self._bg = bg
        self._radius = radius if radius is not None else dp(16)
        self._outline = outline
        self.bind(pos=self._draw, size=self._draw)
        self._draw()

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            if self._bg:
                Color(*self._bg)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[self._radius])
            if self._outline:
                Color(*self._outline)
                Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self._radius),
                     width=dp(1.5))


class CardButton(ButtonBehavior, Card):
    """Нажимаемая карточка."""


class PillButton(ButtonBehavior, Label):
    """Кнопка: заливка, рамка или без фона."""

    def __init__(self, bg=None, fg=INK, outline=None, radius=None, **kw):
        kw.setdefault("bold", True)
        kw.setdefault("font_size", sp(15))
        super().__init__(color=fg, **kw)
        self._bg, self._outline, self._radius = bg, outline, radius
        self.bind(pos=self._draw, size=self._draw)
        self._draw()

    def set_style(self, bg=None, fg=INK, outline=None):
        self._bg, self._outline = bg, outline
        self.color = fg
        self._draw()

    def on_state(self, *_):
        self.opacity = 0.75 if self.state == "down" else 1

    def _draw(self, *_):
        self.canvas.before.clear()
        r = self._radius if self._radius is not None else self.height / 2
        with self.canvas.before:
            if self._bg:
                Color(*self._bg)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[r])
            if self._outline:
                Color(*self._outline)
                Line(rounded_rectangle=(self.x, self.y, self.width, self.height, r),
                     width=dp(1.5))


class ProgressLine(Widget):
    """Шкала прогресса 0..100."""

    value = NumericProperty(0)
    color = ListProperty(AC)
    track = ListProperty(TRACK)

    def __init__(self, value=0, color=AC, track=TRACK, **kw):
        kw.setdefault("size_hint_y", None)
        kw.setdefault("height", dp(8))
        super().__init__(**kw)
        self.value, self.color, self.track = value, color, track
        self.bind(pos=self._draw, size=self._draw, value=self._draw,
                  color=self._draw, track=self._draw)
        self._draw()

    def _draw(self, *_):
        self.canvas.clear()
        r = self.height / 2
        with self.canvas:
            Color(*self.track)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[r])
            Color(*self.color)
            RoundedRectangle(pos=self.pos, size=(self.width * max(0, min(100, self.value)) / 100,
                                                 self.height), radius=[r])


class Toggle(ButtonBehavior, Widget):
    """Тумблер вкл/выкл. Следить за изменением: toggle.bind(active=callback)."""

    active = BooleanProperty(False)
    color = ListProperty(AC)

    def __init__(self, active=False, color=AC, **kw):
        kw.setdefault("size_hint", (None, None))
        kw.setdefault("size", (dp(52), dp(32)))
        super().__init__(**kw)
        self.active, self.color = active, color
        self.bind(pos=self._draw, size=self._draw, active=self._draw, color=self._draw)
        self._draw()

    def on_release(self):
        self.active = not self.active

    def _draw(self, *_):
        self.canvas.clear()
        knob = self.height - dp(6)
        with self.canvas:
            Color(*(self.color if self.active else OFF))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.height / 2])
            Color(*WHITE)
            x = self.right - dp(3) - knob if self.active else self.x + dp(3)
            Ellipse(pos=(x, self.y + dp(3)), size=(knob, knob))


class Marker(Widget):
    """Цветная точка (дело/предмет) или квадратик (метка)."""

    def __init__(self, color=AC, shape="dot", d=None, **kw):
        d = d or dp(10)
        super().__init__(size_hint=(None, None), size=(d, d), **kw)
        self._color, self._shape = color, shape
        self.bind(pos=self._draw, size=self._draw)
        self._draw()

    def _draw(self, *_):
        self.canvas.clear()
        with self.canvas:
            Color(*self._color)
            if self._shape == "dot":
                Ellipse(pos=self.pos, size=self.size)
            else:
                RoundedRectangle(pos=self.pos, size=self.size, radius=[self.width * 0.2])


class Chip(Label):
    """Чип приоритета: слово + цвет."""

    def __init__(self, priority, **kw):
        bg, fg = PRIORITY[priority]
        super().__init__(text=priority, color=fg, bold=True, font_size=sp(12),
                         size_hint=(None, None), height=dp(22), **kw)
        self._bg = bg
        self.bind(texture_size=self._fit, pos=self._draw, size=self._draw)
        self._fit()

    def _fit(self, *_):
        self.width = self.texture_size[0] + dp(16)

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._bg)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])


class Segmented(Card):
    """Переключатель из нескольких вариантов (Дела | Заметки, приоритет)."""

    def __init__(self, options, active, on_select, fg_map=None, **kw):
        super().__init__(bg=TRACK, radius=dp(14), padding=dp(4), size_hint_y=None,
                         height=dp(48), **kw)
        self._fg_map = fg_map or {}
        self.buttons = {}
        for name in options:
            b = PillButton(text=name, radius=dp(10))
            b.bind(on_release=lambda *_, n=name: on_select(n))
            self.add_widget(b)
            self.buttons[name] = b
        self.set_active(active)

    def set_active(self, name):
        for n, b in self.buttons.items():
            on = n == name
            b.set_style(bg=CARD if on else None,
                        fg=self._fg_map.get(n, INK) if on else MUTED)


class DayCell(ButtonBehavior, Label):
    """Ячейка дня в календаре: фон (экзамен/сегодня), рамка выбора, точки событий."""

    def __init__(self, day, fill=None, soft=None, ring=False, dots=(), **kw):
        color = WHITE if fill else (AC if soft else INK)
        super().__init__(text=str(day), color=color, bold=bool(fill or soft or ring),
                         font_size=sp(15), **kw)
        self._fill, self._soft, self._ring, self._dots = fill, soft, ring, dots
        self.bind(pos=self._draw, size=self._draw)
        self._draw()

    def _draw(self, *_):
        self.canvas.before.clear()
        self.canvas.after.clear()
        r = dp(12)
        with self.canvas.before:
            bg = self._fill or self._soft
            if bg:
                Color(*bg)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[r])
        with self.canvas.after:
            if self._ring:
                Color(*INK if self._fill else AC)
                Line(rounded_rectangle=(self.x, self.y, self.width, self.height, r), width=dp(1.5))
            if self._dots and not self._fill:
                d, gap = dp(6), dp(3)
                total = len(self._dots) * d + (len(self._dots) - 1) * gap
                x = self.center_x - total / 2
                for shape, color in self._dots:
                    Color(*color)
                    if shape == "task":
                        Ellipse(pos=(x, self.y + dp(4)), size=(d, d))
                    else:
                        RoundedRectangle(pos=(x, self.y + dp(4)), size=(d, d), radius=[dp(1.5)])
                    x += d + gap


def center(widget):
    """Выровнять виджет фиксированного размера по центру строки."""
    box = AnchorLayout(anchor_x="center", anchor_y="center", size_hint_x=None, width=widget.width)
    box.add_widget(widget)
    widget.bind(width=lambda *_: setattr(box, "width", widget.width))  # чип растёт после отрисовки текста
    return box


def make_field(label, text="", hint="", multiline=False, height=None):
    """Поле ввода с подписью. Возвращает (контейнер, TextInput)."""
    height = height or dp(48)
    box = BoxLayout(orientation="vertical", size_hint_y=None, height=height + dp(24), spacing=dp(6))
    box.add_widget(Text(label, fs=13, bold=True, color=MUTED, size_hint_y=None, height=dp(18)))
    card = Card(bg=CARD, outline=OFF, radius=dp(12), padding=dp(2), size_hint_y=None, height=height)
    ti = TextInput(text=text, hint_text=hint, multiline=multiline,
                   background_normal="", background_active="", background_color=(0, 0, 0, 0),
                   foreground_color=INK, hint_text_color=(*MUTED[:3], 0.7), cursor_color=AC,
                   padding=[dp(12), dp(11) if not multiline else dp(12)], font_size=sp(16))
    card.add_widget(ti)
    box.add_widget(card)
    return box, ti
