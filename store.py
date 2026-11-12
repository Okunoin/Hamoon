"""Данные сессий и автоматическое сохранение в JSON; модуль не зависит от Kivy."""
from datetime import date

TODAY = date.today()
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
        self.sessions = [self._capture_session("Зимняя сессия 2027 (пример)")]
        self.session_id = self.sessions[0]["id"]

    @property
    def current_session(self):
        return next((s for s in self.sessions if s["id"] == self.session_id), None)

    def _capture_session(self, name):
        return {"id": self._next_id(), "name": name, "subjects": self.subjects,
                "tasks": self.tasks, "marks": self.marks, "notes": self.notes}

    def add_session(self, name):
        name = name.strip()
        if not name:
            raise ValueError("Введите название сессии")
        session = {"id": self._next_id(), "name": name, "subjects": [],
                   "tasks": [], "marks": [], "notes": []}
        self.sessions.append(session)
        return session

    def select_session(self, session_id):
        session = next(s for s in self.sessions if s["id"] == session_id)
        self.session_id = session_id
        for key in ("subjects", "tasks", "marks", "notes"):
            setattr(self, key, session[key])

    def add_subject(self, name, color, exam=None):
        name = name.strip()
        if not name:
            raise ValueError("Введите название предмета")
        if any(s["name"].casefold() == name.casefold() for s in self.subjects):
            raise ValueError("Такой предмет уже есть в этой сессии")
        subject = {"name": name, "color": color, "exam": exam}
        self.subjects.append(subject)
        return subject

    def delete_subject(self, name):
        subject = self.subject(name)
        self.subjects.remove(subject)
        self.tasks[:] = [t for t in self.tasks if t["subject"] != name]
        self.notes[:] = [n for n in self.notes if n["subject"] != name]

    def update_exam(self, subject, exam):
        self.subject(subject)["exam"] = exam

    def delete_mark(self, mark_id):
        self.marks.remove(self.mark(mark_id))

    def save(self):
        if not getattr(self, "path", None):
            return
        import json
        data = {"seq": self._seq, "session_id": self.session_id, "sessions": self.sessions}
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(data, ensure_ascii=False,
                            default=lambda d: {"__date__": d.isoformat()}), encoding="utf-8")
        temporary.replace(self.path)

    def load(self, path):
        import json
        from pathlib import Path
        self.path = Path(path)
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"),
                object_hook=lambda obj: date.fromisoformat(obj["__date__"]) if "__date__" in obj else obj)
            self._seq, self.sessions = data["seq"], data["sessions"]
            self.select_session(data["session_id"])

    def _next_id(self):
        self._seq += 1
        return self._seq

    # --- предметы ------------------------------------------------------
    def subject(self, name):
        return next(s for s in self.subjects if s["name"] == name)

    def exam_on(self, day):
        return next((s for s in self.subjects if s["exam"] == day), None)

    def days_to_first_exam(self):
        left = [(s["exam"] - TODAY).days for s in self.subjects if s["exam"] is not None and s["exam"] >= TODAY]
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


# Сохраняем каждое изменение, в том числе при работе на телефоне.
from functools import wraps

def _persist(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        self.save()
        return result
    return wrapped

for _name in ("add_session", "select_session", "add_subject", "delete_subject", "update_exam", "delete_mark",
              "add_task", "update_task", "set_done", "add_mark", "update_mark", "add_note", "update_note"):
    setattr(Store, _name, _persist(getattr(Store, _name)))

store = Store()
