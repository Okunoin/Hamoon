from .forms import MarkFormScreen, NoteEditScreen, TaskFormScreen, SessionFormScreen, SubjectFormScreen
from .subject import SubjectScreen
from .top import CalendarScreen, NotesScreen, SubjectsScreen, SessionsScreen

# имя экрана -> класс. Первый в списке открывается при запуске.
SCREENS = {
    "sessions": SessionsScreen,
    "session_form": SessionFormScreen,
    "subject_form": SubjectFormScreen,
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
