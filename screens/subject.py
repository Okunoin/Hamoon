"""Экраны внутри предмета: папка, дела, заметки."""
from .base import SubjectBoundScreen, app


class SubjectScreen(SubjectBoundScreen):
    def build_body(self):
        self.button("Дела", lambda: app().open("tasks", subject=self.subject))
        self.button("Заметки", lambda: app().open("subject_notes", subject=self.subject))
        self.spacer()


class TasksScreen(SubjectBoundScreen):
    title_fmt = "Дела: {subject}"

    def build_body(self):
        self.placeholder("Здесь будет список дел с тумблерами")
        self.button("+ Добавить дело", lambda: app().open("task_form", subject=self.subject))


class SubjectNotesScreen(SubjectBoundScreen):
    title_fmt = "Заметки: {subject}"

    def build_body(self):
        self.placeholder("Здесь будут заметки папки")
        self.button("+ Заметка", lambda: app().open("note_edit", subject=self.subject))
