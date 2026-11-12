from .forms import MarkFormScreen, NoteEditScreen, TaskFormScreen
from .subject import SubjectScreen
from .top import CalendarScreen, NotesScreen, SubjectsScreen

# имя экрана -> класс. Первый в списке открывается при запуске.
SCREENS = {
    "subjects": SubjectsScreen,
    "calendar": CalendarScreen,
    "notes": NotesScreen,
    "subject": SubjectScreen,
    "task_form": TaskFormScreen,
    "mark_form": MarkFormScreen,
    "note_edit": NoteEditScreen,
}


def register_screens(sm):
    for name, cls in SCREENS.items():
        sm.add_widget(cls(name=name))
