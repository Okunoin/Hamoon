"""Данные приложения (пока только в памяти, без сохранения на диск).

Здесь нет Kivy: цвета хранятся строками "#RRGGBB". Позже этот модуль можно
заменить хранилищем на SQLite/JSON, не трогая экраны.
"""
from datetime import date

TODAY = date(2027, 1, 11)          # «сегодня» для примера; потом заменить на date.today()
PRIORITIES = ("Низкий", "Средний", "Высокий")
MARK_COLORS = ("#1C2030", "#3B4CCA", "#0F766E", "#B45309", "#BE3455")


def _d(day):
    return date(2027, 1, day)


# предмет -> [(дело, день января, приоритет, выполнено)]
_SEED_TASKS = {
    "Матанализ": [
        ("Конспект лекций 1–5", 5, "Средний", True),
        ("Решить типовой расчёт", 7, "Высокий", True),
        ("Выучить таблицу интегралов", 8, "Средний", True),
        ("Разобрать билеты 1–10", 9, "Высокий", True),
        ("Разобрать билеты 11–20", 11, "Высокий", False),
        ("Решить прошлогодний вариант", 12, "Средний", False),
        ("Консультация перед экзаменом", 13, "Низкий", False),
    ],
    "Физика": [
        ("Конспект по оптике", 6, "Средний", True),
        ("Лабораторные 1–3", 9, "Высокий", True),
        ("Разобрать билеты", 12, "Высокий", False),
        ("Задачи по оптике", 19, "Средний", False),
    ],
    "История": [
        ("Таймлайн XIX века", 8, "Средний", True),
        ("Выучить даты", 10, "Низкий", True),
        ("Повторить реформы XIX века", 11, "Средний", False),
    ],
    "Программирование": [
        ("Лабораторная 4", 17, "Высокий", False),
        ("Курсовой проект", 20, "Высокий", False),
        ("Повторить алгоритмы", 22, "Средний", False),
    ],
    "Английский": [
        ("Эссе", 16, "Средний", True),
        ("Лексика Unit 5–6", 23, "Низкий", False),
    ],
}


class Store:
    def __init__(self):
        self._seq = 0
        self.subjects = [
            {"name": "Матанализ", "color": "#3B4CCA", "exam": _d(14)},
            {"name": "Физика", "color": "#0F766E", "exam": _d(18)},
            {"name": "История", "color": "#B45309", "exam": _d(21)},
            {"name": "Программирование", "color": "#BE3455", "exam": _d(25)},
            {"name": "Английский", "color": "#5B4B8A", "exam": _d(28)},
        ]
        self.tasks, self.marks, self.notes = [], [], []
        for subject, rows in _SEED_TASKS.items():
            for title, day, prio, done in rows:
                self.add_task(subject, title, _d(day), prio, done=done)
        self.add_mark("Консультация у куратора", _d(11), "15:00",
                      "Взять зачётку и список вопросов", MARK_COLORS[0])
        self.add_mark("Сдать справку в деканат", _d(16), "", "", MARK_COLORS[3])
        self.add_note("Матанализ", "Формулы интегрирования", "Таблица основных интегралов...")
        self.add_note("Матанализ", "Вопросы к экзамену", "")

    def _next_id(self):
        self._seq += 1
        return self._seq

    # --- предметы ------------------------------------------------------
    def subject(self, name):
        return next(s for s in self.subjects if s["name"] == name)

    def exam_on(self, day):
        return next((s for s in self.subjects if s["exam"] == day), None)

    def days_to_first_exam(self):
        left = [(s["exam"] - TODAY).days for s in self.subjects if s["exam"] >= TODAY]
        return min(left) if left else None

    # --- дела ----------------------------------------------------------
    def add_task(self, subject, title, due, priority, in_calendar=True, done=False):
        task = {"id": self._next_id(), "subject": subject, "title": title, "due": due,
                "priority": priority, "in_calendar": in_calendar, "done": done}
        self.tasks.append(task)
        return task

    def task(self, task_id):
        return next(t for t in self.tasks if t["id"] == task_id)

    def update_task(self, task_id, **fields):
        self.task(task_id).update(fields)

    def set_done(self, task_id, done):
        self.task(task_id)["done"] = done

    def tasks_for(self, subject):
        return sorted((t for t in self.tasks if t["subject"] == subject),
                      key=lambda t: (t["due"], t["id"]))

    def tasks_on(self, day):
        return [t for t in self.tasks if t["in_calendar"] and t["due"] == day]

    def counts(self, subject):
        items = [t for t in self.tasks if t["subject"] == subject]
        return sum(t["done"] for t in items), len(items)

    def progress(self, subject):
        done, total = self.counts(subject)
        return round(100 * done / total) if total else 0

    def overall_progress(self):
        done = sum(t["done"] for t in self.tasks)
        return round(100 * done / len(self.tasks)) if self.tasks else 0

    # --- метки ---------------------------------------------------------
    def add_mark(self, title, due, time, comment, color):
        mark = {"id": self._next_id(), "title": title, "due": due, "time": time,
                "comment": comment, "color": color}
        self.marks.append(mark)
        return mark

    def mark(self, mark_id):
        return next(m for m in self.marks if m["id"] == mark_id)

    def update_mark(self, mark_id, **fields):
        self.mark(mark_id).update(fields)

    def marks_on(self, day):
        return sorted((m for m in self.marks if m["due"] == day), key=lambda m: m["time"])

    # --- заметки -------------------------------------------------------
    def add_note(self, subject, title, body):
        note = {"id": self._next_id(), "subject": subject, "title": title,
                "body": body, "created": TODAY}
        self.notes.append(note)
        return note

    def note(self, note_id):
        return next(n for n in self.notes if n["id"] == note_id)

    def update_note(self, note_id, **fields):
        self.note(note_id).update(fields)

    def notes_for(self, subject):
        return sorted((n for n in self.notes if n["subject"] == subject),
                      key=lambda n: -n["id"])


store = Store()
