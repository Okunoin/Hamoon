"""Формы: дело, метка, заметка. Сохраняют в store и возвращают назад."""
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex as hx

from dates import fmt_input, parse_date, parse_time
from store import MARK_COLORS, PRIORITIES, TODAY, store
from theme import AC, CARD, ERROR, INK, MUTED, PRIORITY, WHITE
from widgets import Card, PillButton, Segmented, Text, Toggle, center, make_field
from .base import BaseScreen, app


class FormScreen(BaseScreen):
    """Общее: прокручиваемые поля, строка ошибки и кнопка «Сохранить»."""

    show_back = True
    show_nav = False
    save_label = "Сохранить"

    def build_body(self):
        g = self.scroll()
        g.spacing = dp(14)
        self.build_fields(g)
        self.error = Text("", fs=13, color=ERROR, size_hint_y=None, height=dp(20))
        self.body.add_widget(self.error)
        btn = PillButton(text=self.save_label, bg=AC, fg=WHITE, size_hint_y=None, height=dp(52),
                         font_size="16sp")
        btn.bind(on_release=lambda *_: self.save())
        self.body.add_widget(btn)

    def build_fields(self, g):
        """Добавить поля в контейнер g."""

    def save(self):
        """Проверить поля, записать в store и вызвать app().back()."""

    def fail(self, message):
        self.error.text = message


class TaskFormScreen(FormScreen):
    def on_context(self, subject="", task_id=None, **ctx):
        self.task = store.task(task_id) if task_id else None
        self.subject = self.task["subject"] if self.task else subject
        self.title = "Изменить дело" if self.task else "Новое дело"
        self.subtitle = self.subject
        self.priority = self.task["priority"] if self.task else "Средний"

    def build_fields(self, g):
        t = self.task or {}
        box, self.f_title = make_field("Название", t.get("title", ""))
        g.add_widget(box)
        box, self.f_due = make_field("Дедлайн", fmt_input(t.get("due", TODAY)), "ДД.ММ.ГГГГ")
        g.add_widget(box)

        g.add_widget(Text("Приоритет", fs=13, bold=True, color=MUTED, size_hint_y=None, height=dp(18)))
        self.seg = Segmented(PRIORITIES, self.priority, self._set_priority,
                             fg_map={p: PRIORITY[p][1] for p in PRIORITIES})
        g.add_widget(self.seg)

        row = Card(padding=[dp(16), dp(10), dp(14), dp(10)], size_hint_y=None, height=dp(56))
        row.add_widget(Text("Показывать в календаре", fs=16, bold=True))
        self.in_cal = Toggle(active=t.get("in_calendar", True))
        row.add_widget(center(self.in_cal))
        g.add_widget(row)

    def _set_priority(self, name):
        self.priority = name
        self.seg.set_active(name)

    def save(self):
        title = self.f_title.text.strip()
        due = parse_date(self.f_due.text)
        if not title:
            return self.fail("Введите название")
        if due is None:
            return self.fail("Дедлайн: дата в формате ДД.ММ.ГГГГ")
        fields = dict(title=title, due=due, priority=self.priority, in_calendar=self.in_cal.active)
        if self.task:
            store.update_task(self.task["id"], **fields)
        else:
            store.add_task(self.subject, **fields)
        app().back()


class MarkFormScreen(FormScreen):
    save_label = "Сохранить метку"

    def on_context(self, mark_id=None, day=None, **ctx):
        self.mark = store.mark(mark_id) if mark_id else None
        self.day = self.mark["due"] if self.mark else (day or TODAY)
        self.color = self.mark["color"] if self.mark else MARK_COLORS[0]
        self.title = "Изменить метку" if self.mark else "Новая метка"
        self.subtitle = "Дедлайн можно менять в любой момент"

    def build_fields(self, g):
        m = self.mark or {}
        box, self.f_title = make_field("Название", m.get("title", ""))
        g.add_widget(box)
        box, self.f_due = make_field("Дедлайн", fmt_input(self.day), "ДД.ММ.ГГГГ")
        g.add_widget(box)
        box, self.f_time = make_field("Время дедлайна (необязательно)", m.get("time", ""), "ЧЧ:ММ")
        g.add_widget(box)
        box, self.f_comment = make_field("Комментарий", m.get("comment", ""),
                                         multiline=True, height=dp(96))
        g.add_widget(box)

        g.add_widget(Text("Цвет метки", fs=13, bold=True, color=MUTED, size_hint_y=None, height=dp(18)))
        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(12))
        self.swatches = {}
        for c in MARK_COLORS:
            b = PillButton(bg=hx(c), size_hint=(None, None), size=(dp(44), dp(44)), radius=dp(12))
            b.bind(on_release=lambda *_, col=c: self._set_color(col))
            row.add_widget(b)
            self.swatches[c] = b
        g.add_widget(row)
        self._set_color(self.color)
        if self.mark:
            delete = PillButton(text="Удалить метку", fg=ERROR, outline=ERROR,
                                size_hint_y=None, height=dp(48))
            delete.bind(on_release=lambda *_: self.confirm_delete())
            g.add_widget(delete)

    def confirm_delete(self):
        from kivy.uix.popup import Popup
        box = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(12))
        box.add_widget(Text("Удалить эту метку из календаря?", fs=15))
        row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(48))
        cancel = PillButton(text="Отмена", fg=AC)
        delete = PillButton(text="Удалить", fg=ERROR, outline=ERROR)
        row.add_widget(cancel)
        row.add_widget(delete)
        box.add_widget(row)
        popup = Popup(title="Удаление метки", content=box, size_hint=(0.92, None), height=dp(220))
        cancel.bind(on_release=lambda *_: popup.dismiss())
        def remove(*_):
            store.delete_mark(self.mark["id"])
            popup.dismiss()
            app().back()
        delete.bind(on_release=remove)
        popup.open()

    def _set_color(self, color):
        self.color = color
        for c, b in self.swatches.items():
            b.set_style(bg=hx(c), outline=INK if c == color else None)

    def save(self):
        title = self.f_title.text.strip()
        due = parse_date(self.f_due.text)
        time = parse_time(self.f_time.text)
        if not title:
            return self.fail("Введите название")
        if due is None:
            return self.fail("Дедлайн: дата в формате ДД.ММ.ГГГГ")
        if time is None:
            return self.fail("Время в формате ЧЧ:ММ, например 15:00")
        fields = dict(title=title, due=due, time=time, comment=self.f_comment.text.strip(),
                      color=self.color)
        if self.mark:
            store.update_mark(self.mark["id"], **fields)
        else:
            store.add_mark(**fields)
        app().back()


class NoteEditScreen(FormScreen):
    def on_context(self, subject="", note_id=None, **ctx):
        self.note = store.note(note_id) if note_id else None
        self.subject = self.note["subject"] if self.note else subject
        self.title = "Заметка"
        self.subtitle = self.subject

    def build_fields(self, g):
        n = self.note or {}
        box, self.f_title = make_field("Заголовок", n.get("title", ""))
        g.add_widget(box)
        box, self.f_body = make_field("Текст", n.get("body", ""), multiline=True, height=dp(280))
        g.add_widget(box)

    def save(self):
        title = self.f_title.text.strip()
        if not title:
            return self.fail("Введите заголовок")
        if self.note:
            store.update_note(self.note["id"], title=title, body=self.f_body.text)
        else:
            store.add_note(self.subject, title, self.f_body.text)
        app().back()


class SessionFormScreen(FormScreen):
    title = "Новая сессия"
    subtitle = "Например: Летняя сессия 2027"

    def build_fields(self, g):
        box, self.f_name = make_field("Название сессии", "")
        g.add_widget(box)

    def save(self):
        try:
            session = store.add_session(self.f_name.text)
        except ValueError as exc:
            return self.fail(str(exc))
        store.select_session(session["id"])
        app().open_root("subjects")


class SubjectFormScreen(FormScreen):
    def on_context(self, subject="", **ctx):
        self.subject = subject
        self.title = "Дата экзамена" if subject else "Новый предмет"
        self.subtitle = subject or "Добавьте свой предмет"

    def build_fields(self, g):
        if not self.subject:
            box, self.f_name = make_field("Название предмета", "")
            g.add_widget(box)
        exam = store.subject(self.subject)["exam"] if self.subject else None
        box, self.f_exam = make_field("Дата экзамена (необязательно)",
                                     fmt_input(exam) if exam else "", "ДД.ММ.ГГГГ")
        g.add_widget(box)
        clear = PillButton(text="Убрать дату экзамена", fg=AC, outline=AC,
                           size_hint_y=None, height=dp(48))
        clear.bind(on_release=lambda *_: setattr(self.f_exam, "text", ""))
        g.add_widget(clear)
        g.add_widget(Text("Без даты экзамен не отображается в календаре.",
                          fs=13, color=MUTED, size_hint_y=None, height=dp(48)))

    def save(self):
        raw = self.f_exam.text.strip()
        exam = parse_date(raw) if raw else None
        if raw and exam is None:
            return self.fail("Введите дату ДД.ММ.ГГГГ или оставьте поле пустым")
        try:
            if self.subject:
                store.update_exam(self.subject, exam)
            else:
                store.add_subject(self.f_name.text, MARK_COLORS[len(store.subjects) % len(MARK_COLORS)], exam)
        except ValueError as exc:
            return self.fail(str(exc))
        app().back()
