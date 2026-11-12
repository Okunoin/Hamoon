"""Папка предмета: вкладки «Дела» (с тумблерами) и «Заметки»."""
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.utils import escape_markup, get_color_from_hex as hx

from dates import fmt_long, fmt_short
from store import store
from theme import AC, CARD, ERROR, MUTED
from widgets import CardButton, Chip, PillButton, ProgressLine, Segmented, Text, Toggle, center
from .base import BaseScreen, app


class SubjectScreen(BaseScreen):
    show_back = True

    def __init__(self, **kwargs):
        self.subject, self.tab = "", "tasks"
        super().__init__(**kwargs)

    def on_context(self, subject="", tab="tasks", **ctx):
        self.subject, self.tab = subject, tab
        self.title = subject
        exam = store.subject(subject)["exam"]
        self.subtitle = "Экзамен " + fmt_long(exam) if exam else "Дата экзамена не задана"
        self.active_tab = "subjects"

    def build_body(self):
        if not self.subject:
            return
        self.on_context(subject=self.subject, tab=self.tab)
        self.subtitle_label.text = self.subtitle
        actions = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(44))
        edit = PillButton(text="Дата", fg=AC, outline=AC, size_hint=(1, 1))
        edit.bind(on_release=lambda *_: app().open("subject_form", subject=self.subject))
        delete = PillButton(text="Удалить предмет", fg=ERROR, outline=ERROR,
                            font_size="14sp", size_hint=(1, 1))
        delete.bind(on_release=lambda *_: self.confirm_delete())
        actions.add_widget(edit)
        actions.add_widget(delete)
        self.body.add_widget(actions)
        color = hx(store.subject(self.subject)["color"])
        done, total = store.counts(self.subject)
        p = store.progress(self.subject)

        info = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(40), spacing=dp(6),
                         padding=[dp(4), 0])
        row = BoxLayout(size_hint_y=None, height=dp(20))
        row.add_widget(Text(f"{done} из {total} дел выполнено", fs=13, color=MUTED))
        row.add_widget(Text(f"{p}%", fs=13, bold=True, halign="right", size_hint_x=None, width=dp(48)))
        info.add_widget(row)
        info.add_widget(ProgressLine(value=p, color=color, height=dp(10)))
        self.body.add_widget(info)

        self.body.add_widget(Segmented(("Дела", "Заметки"), "Заметки" if self.tab == "notes" else "Дела",
                                       self._switch))
        g = self.scroll()
        if self.tab == "notes":
            self._fill_notes(g)
            label, target = "+ Заметка", lambda: app().open("note_edit", subject=self.subject)
        else:
            self._fill_tasks(g, color)
            label, target = "+ Добавить дело", lambda: app().open("task_form", subject=self.subject)
        add = PillButton(text=label, bg=CARD, fg=AC, outline=AC, size_hint_y=None, height=dp(48))
        add.bind(on_release=lambda *_: target())
        self.body.add_widget(add)

    def confirm_delete(self):
        from kivy.uix.popup import Popup
        subject = self.subject
        box = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(12))
        box.add_widget(Text(f'Удалить предмет «{subject}»?\nЕго дела и заметки тоже будут удалены.', fs=15))
        buttons = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(44))
        cancel = PillButton(text="Отмена", fg=AC)
        delete = PillButton(text="Удалить", fg=ERROR, outline=ERROR)
        buttons.add_widget(cancel)
        buttons.add_widget(delete)
        box.add_widget(buttons)
        popup = Popup(title="Удаление предмета", content=box,
                      size_hint=(0.92, None), height=dp(250))
        cancel.bind(on_release=lambda *_: popup.dismiss())
        def remove(*_):
            store.delete_subject(subject)
            popup.dismiss()
            app().open_root("subjects")
        delete.bind(on_release=remove)
        popup.open()

    def _switch(self, name):
        self.tab = "notes" if name == "Заметки" else "tasks"
        self.active_tab = "subjects"
        self.refresh()

    # --- дела -------------------------------------------------------------
    def _fill_tasks(self, g, color):
        tasks = store.tasks_for(self.subject)
        if not tasks:
            g.add_widget(Text("Дел пока нет. Добавьте первое.", fs=14, color=MUTED,
                              size_hint_y=None, height=dp(40)))
        for t in tasks:
            g.add_widget(self._task_row(t, color))

    def _task_row(self, t, color):
        c = CardButton(padding=[dp(16), dp(10), dp(14), dp(10)], spacing=dp(12),
                       size_hint_y=None, height=dp(76))
        col = BoxLayout(orientation="vertical", spacing=dp(6))
        if t["done"]:
            col.add_widget(Text(f"[s]{escape_markup(t['title'])}[/s]", fs=16, color=MUTED,
                                markup=True, shorten=True, size_hint_y=None, height=dp(24)))
        else:
            col.add_widget(Text(t["title"], fs=16, bold=True, shorten=True,
                                size_hint_y=None, height=dp(24)))
        meta = BoxLayout(size_hint_y=None, height=dp(22), spacing=dp(8))
        meta.add_widget(Text(f"до {fmt_short(t['due'])}", fs=13, color=MUTED,
                             size_hint_x=None, width=dp(74)))
        meta.add_widget(Chip(t["priority"]))
        meta.add_widget(Widget())
        col.add_widget(meta)
        c.add_widget(col)
        toggle = Toggle(active=t["done"], color=color)
        toggle.bind(active=lambda inst, val, i=t["id"]: self._on_toggle(i, val))
        c.add_widget(center(toggle))
        c.bind(on_release=lambda *_, i=t["id"]: app().open("task_form", task_id=i))
        return c

    def _on_toggle(self, task_id, value):
        store.set_done(task_id, value)
        Clock.schedule_once(lambda dt: self.refresh(), 0)

    # --- заметки ----------------------------------------------------------
    def _fill_notes(self, g):
        notes = store.notes_for(self.subject)
        if not notes:
            g.add_widget(Text("Заметок пока нет.", fs=14, color=MUTED, size_hint_y=None, height=dp(40)))
        for n in notes:
            c = CardButton(orientation="vertical", padding=[dp(16), dp(10)], spacing=dp(4),
                           size_hint_y=None, height=dp(62))
            c.add_widget(Text(n["title"], fs=16, bold=True, shorten=True))
            c.add_widget(Text(fmt_short(n["created"]), fs=13, color=MUTED))
            c.bind(on_release=lambda *_, i=n["id"]: app().open("note_edit", note_id=i))
            g.add_widget(c)
