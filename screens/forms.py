"""Формы: новое дело, новая метка, редактор заметки."""
from .base import BaseScreen, SubjectBoundScreen, app


class TaskFormScreen(SubjectBoundScreen):
    title_fmt = "Новое дело: {subject}"

    def build_body(self):
        self.placeholder("Название, дедлайн, приоритет")
        self.button("Сохранить", lambda: app().back())  # TODO: сохранять дело


class MarkFormScreen(BaseScreen):
    title = "Новая метка"

    def build_body(self):
        self.placeholder("Название, дедлайн, время, комментарий, цвет")
        self.button("Сохранить", lambda: app().back())  # TODO: сохранять метку


class NoteEditScreen(SubjectBoundScreen):
    title_fmt = "Заметка: {subject}"

    def build_body(self):
        self.placeholder("Здесь будет редактор заметки")
        self.button("Сохранить", lambda: app().back())  # TODO: сохранять заметку
