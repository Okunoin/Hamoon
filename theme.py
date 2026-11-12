"""Цвета макета."""
from kivy.utils import get_color_from_hex as hx

BG = hx("#F5F4EF")
CARD = hx("#FFFFFF")
INK = hx("#1C2030")
MUTED = hx("#5F6577")
AC = hx("#3B4CCA")
AC_SOFT = hx("#E8EAFA")
TRACK = hx("#E4E2DA")
OFF = hx("#8A8F9E")
LINE = hx("#EEECE5")
ERROR = hx("#BE3455")
WHITE = (1, 1, 1, 1)

# приоритет -> (фон чипа, цвет текста)
PRIORITY = {
    "Высокий": (hx("#FBE4E9"), hx("#9F1F3F")),
    "Средний": (hx("#FDF0DC"), hx("#8A4A06")),
    "Низкий": (hx("#E6EEF0"), hx("#3D5560")),
}
