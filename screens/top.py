"""Главные экраны с нижними вкладками: Предметы, Календарь, Заметки."""
from data import SUBJECTS
from .base import BaseScreen, app


class SubjectsScreen(BaseScreen):
    title = "Предметы"
    show_back = False
    show_nav = True

    def build_body(self):
        grid = self.scroll_list()
        for s in SUBJECTS:
            self.button(f'{s["name"]}  -  {s["progress"]}%',
                        self.go("subject", subject=s["name"]), parent=grid)


class CalendarScreen(BaseScreen):
    title = "Календарь"
    show_back = False
    show_nav = True

    def build_body(self):
        self.placeholder("Здесь будет календарь")
        self.button("+ Метка", self.go("mark_form"))


class NotesScreen(BaseScreen):
    title = "Заметки"
    show_back = False
    show_nav = True

    def build_body(self):
        grid = self.scroll_list()
        for s in SUBJECTS:  # папка на каждый предмет
            self.button(s["name"], self.go("subject_notes", subject=s["name"]), parent=grid)
