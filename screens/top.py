"""Главные экраны с нижними вкладками: Предметы, Календарь, Заметки."""
import calendar
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex as hx

from dates import MONTHS, WEEKDAYS, fmt_long, fmt_short
from store import TODAY, store
from theme import AC, AC_SOFT, CARD, MUTED, TRACK, WHITE
from widgets import (Card, CardButton, Chip, DayCell, Marker, PillButton, ProgressLine,
                     Text, center)
from .base import BaseScreen, app


class SubjectsScreen(BaseScreen):
    title = "Предметы"
    subtitle = "Зимняя сессия 2027"
    active_tab = "subjects"

    def refresh(self):
        self.subtitle = store.current_session["name"]
        super().refresh()

    def build_body(self):
        g = self.scroll()
        switch = PillButton(text="< Выбрать сессию", fg=AC, outline=AC,
                            size_hint_y=None, height=dp(44))
        switch.bind(on_release=lambda *_: app().open_root("sessions"))
        g.add_widget(switch)
        g.add_widget(self._overall())
        add = PillButton(text="+ Добавить предмет", bg=AC, fg=WHITE,
                         size_hint_y=None, height=dp(48))
        add.bind(on_release=lambda *_: app().open("subject_form"))
        g.add_widget(add)
        if not store.subjects:
            g.add_widget(Text("Предметов пока нет", fs=15, color=MUTED,
                              size_hint_y=None, height=dp(40)))
        for s in store.subjects:
            g.add_widget(self._subject_card(s))

    def _overall(self):
        p = store.overall_progress()
        days = store.days_to_first_exam()
        card = Card(bg=AC, orientation="vertical", padding=[dp(18), dp(14)], spacing=dp(8),
                    size_hint_y=None, height=dp(112))
        row = BoxLayout(size_hint_y=None, height=dp(34))
        row.add_widget(Text("Общая подготовка", fs=14, bold=True, color=WHITE))
        row.add_widget(Text(f"{p}%", fs=26, bold=True, color=WHITE, halign="right",
                            size_hint_x=None, width=dp(90)))
        card.add_widget(row)
        card.add_widget(ProgressLine(value=p, color=WHITE, track=(1, 1, 1, 0.28)))
        if days is not None:
            card.add_widget(Text(f"До первого экзамена {days} дн.", fs=13, color=WHITE,
                                 size_hint_y=None, height=dp(20)))
        return card

    def _subject_card(self, s):
        color = hx(s["color"])
        p = store.progress(s["name"])
        c = CardButton(orientation="vertical", padding=[dp(16), dp(12)], spacing=dp(10),
                       size_hint_y=None, height=dp(72))
        row = BoxLayout(size_hint_y=None, height=dp(26), spacing=dp(10))
        row.add_widget(center(Marker(color)))
        row.add_widget(Text(s["name"], fs=16, bold=True, shorten=True))
        row.add_widget(Text((f"Экзамен {fmt_short(s['exam'])}" if s["exam"] else "Без даты"), fs=12, color=MUTED, halign="right",
                            size_hint_x=None, width=dp(96)))
        row.add_widget(Text(f"{p}%", fs=15, bold=True, halign="right",
                            size_hint_x=None, width=dp(44)))
        c.add_widget(row)
        c.add_widget(ProgressLine(value=p, color=color))
        c.bind(on_release=lambda *_, n=s["name"]: app().open("subject", subject=n))
        return c


class CalendarScreen(BaseScreen):
    title = "Календарь"
    subtitle = "Сессия"
    active_tab = "calendar"

    def __init__(self, **kwargs):
        self.year, self.month, self.sel = TODAY.year, TODAY.month, TODAY
        super().__init__(**kwargs)

    def shift(self, delta):
        m = self.month - 1 + delta
        self.year += m // 12
        self.month = m % 12 + 1
        self.refresh()

    def pick(self, day):
        self.sel = day
        self.refresh()

    def build_body(self):
        g = self.scroll()
        g.add_widget(self._month_card())
        g.add_widget(self._legend())
        g.add_widget(self._day_header())
        items = self._day_items()
        if not items:
            g.add_widget(Text("На этот день ничего нет", fs=14, color=MUTED,
                              size_hint_y=None, height=dp(40)))
        for w in items:
            g.add_widget(w)

    # --- сетка месяца ---------------------------------------------------
    def _month_card(self):
        weeks = calendar.Calendar(0).monthdayscalendar(self.year, self.month)
        card = Card(orientation="vertical", padding=[dp(8), dp(8)], spacing=dp(2),
                    size_hint_y=None, height=dp(88) + len(weeks) * dp(44))
        head = BoxLayout(size_hint_y=None, height=dp(40))
        for text, delta in (("<", -1), (">", 1)):
            b = PillButton(text=text, bg=AC_SOFT, fg=AC, size_hint=(None, None),
                           size=(dp(40), dp(36)), radius=dp(12))
            b.bind(on_release=lambda *_, d=delta: self.shift(d))
            if delta < 0:
                head.add_widget(b)
                head.add_widget(Text(f"{MONTHS[self.month - 1]} {self.year}", fs=17, bold=True,
                                     halign="center"))
            else:
                head.add_widget(b)
        card.add_widget(head)
        wd = GridLayout(cols=7, size_hint_y=None, height=dp(24))
        for w in WEEKDAYS:
            wd.add_widget(Text(w, fs=12, bold=True, color=MUTED, halign="center"))
        card.add_widget(wd)
        grid = GridLayout(cols=7, size_hint_y=None, height=len(weeks) * dp(44), row_default_height=dp(44))
        for week in weeks:
            for n in week:
                grid.add_widget(self._cell(n) if n else Widget())
        card.add_widget(grid)
        return card

    def _cell(self, n):
        d = TODAY.replace(year=self.year, month=self.month, day=n)
        exam = store.exam_on(d)
        dots = [("task", hx(store.subject(t["subject"])["color"])) for t in store.tasks_on(d)]
        dots += [("mark", hx(m["color"])) for m in store.marks_on(d)]
        cell = DayCell(n, fill=hx(exam["color"]) if exam else None,
                       soft=AC_SOFT if d == TODAY else None, ring=d == self.sel, dots=dots[:3])
        cell.bind(on_release=lambda *_, day=d: self.pick(day))
        return cell

    def _legend(self):
        row = BoxLayout(size_hint_y=None, height=dp(22), spacing=dp(6), padding=[dp(4), 0])
        row.add_widget(Text("Заливка: экзамен", fs=12, color=MUTED, size_hint_x=None, width=dp(104)))
        row.add_widget(center(Marker(AC, "dot", dp(6))))
        row.add_widget(Text("дело", fs=12, color=MUTED, size_hint_x=None, width=dp(34)))
        row.add_widget(center(Marker(MUTED, "square", dp(6))))
        row.add_widget(Text("метка (по дедлайну)", fs=12, color=MUTED))
        return row

    # --- список выбранного дня -----------------------------------------
    def _day_header(self):
        row = BoxLayout(size_hint_y=None, height=dp(44))
        row.add_widget(Text(fmt_long(self.sel), fs=17, bold=True))
        add = PillButton(text="+ Метка", fg=AC, outline=AC, size_hint=(None, None),
                         size=(dp(100), dp(40)))
        add.bind(on_release=lambda *_: app().open("mark_form", day=self.sel))
        row.add_widget(add)
        return row

    def _day_items(self):
        items = []
        exam = store.exam_on(self.sel)
        if exam:
            c = Card(bg=hx(exam["color"]), padding=[dp(16), dp(10)], size_hint_y=None, height=dp(52))
            c.add_widget(Text(f"Экзамен: {exam['name']}", fs=15, bold=True, color=WHITE))
            items.append(c)
        for t in store.tasks_on(self.sel):
            items.append(self._task_item(t))
        for m in store.marks_on(self.sel):
            items.append(self._mark_item(m))
        return items

    def _task_item(self, t):
        sub = store.subject(t["subject"])
        c = CardButton(padding=[dp(14), dp(10)], spacing=dp(12), size_hint_y=None, height=dp(60))
        c.add_widget(center(Marker(hx(sub["color"]))))
        col = BoxLayout(orientation="vertical", spacing=dp(2))
        col.add_widget(Text(t["title"], fs=15, bold=True, shorten=True))
        col.add_widget(Text(t["subject"], fs=13, color=MUTED))
        c.add_widget(col)
        c.add_widget(center(Chip(t["priority"])))
        c.bind(on_release=lambda *_, i=t["id"]: app().open("task_form", task_id=i))
        return c

    def _mark_item(self, m):
        c = Card(padding=[dp(14), dp(8), dp(8), dp(8)], spacing=dp(10), size_hint_y=None, height=dp(64))
        c.add_widget(center(Marker(hx(m["color"]), "square")))
        col = BoxLayout(orientation="vertical", spacing=dp(2))
        col.add_widget(Text(m["title"], fs=15, bold=True, shorten=True))
        col.add_widget(Text(m["comment"], fs=13, color=MUTED, shorten=True))
        c.add_widget(col)
        due = BoxLayout(orientation="vertical", size_hint_x=None, width=dp(64))
        due.add_widget(Text("Дедлайн", fs=11, color=MUTED, halign="right"))
        due.add_widget(Text(m["time"] or "весь день", fs=13, bold=True, halign="right"))
        c.add_widget(due)
        edit = PillButton(text="Изм.", bg=AC_SOFT, fg=AC, font_size="13sp",
                          size_hint=(None, None), size=(dp(48), dp(44)), radius=dp(22))
        edit.bind(on_release=lambda *_, i=m["id"]: app().open("mark_form", mark_id=i))
        c.add_widget(center(edit))
        return c


class NotesScreen(BaseScreen):
    title = "Заметки"
    subtitle = "Папки по предметам"
    active_tab = "notes"

    def build_body(self):
        g = self.scroll()
        for s in store.subjects:
            n = len(store.notes_for(s["name"]))
            c = CardButton(padding=[dp(16), dp(10)], spacing=dp(12), size_hint_y=None, height=dp(60))
            c.add_widget(center(Marker(hx(s["color"]), "dot", dp(12))))
            c.add_widget(Text(s["name"], fs=16, bold=True))
            c.add_widget(Text(str(n), fs=13, color=MUTED, halign="right",
                              size_hint_x=None, width=dp(40)))
            c.bind(on_release=lambda *_, name=s["name"]: app().open("subject", subject=name, tab="notes"))
            g.add_widget(c)


class SessionsScreen(BaseScreen):
    title = "Мои сессии"
    subtitle = "Выберите сессию или создайте новую"
    show_nav = False

    def build_body(self):
        g = self.scroll()
        add = PillButton(text="+ Создать сессию", bg=AC, fg=WHITE,
                         size_hint_y=None, height=dp(52))
        add.bind(on_release=lambda *_: app().open("session_form"))
        g.add_widget(add)
        for session in store.sessions:
            card = CardButton(orientation="vertical", padding=dp(16),
                              size_hint_y=None, height=dp(88))
            card.add_widget(Text(session["name"], fs=18, bold=True))
            card.add_widget(Text(f"Предметов: {len(session['subjects'])}", fs=14, color=MUTED))
            card.bind(on_release=lambda *_, i=session["id"]: self.choose(i))
            g.add_widget(card)

    def choose(self, session_id):
        store.select_session(session_id)
        app().open_root("subjects")
