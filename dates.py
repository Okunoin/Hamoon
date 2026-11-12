"""Работа с датами: форматы для экрана и разбор того, что вводит пользователь."""
from datetime import datetime

MONTHS = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август",
          "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
MONTHS_GEN = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа",
              "сентября", "октября", "ноября", "декабря"]
MONTHS_SHORT = ["янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]
WEEKDAYS = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]


def fmt_short(d):
    return f"{d.day} {MONTHS_SHORT[d.month - 1]}"


def fmt_long(d):
    return f"{d.day} {MONTHS_GEN[d.month - 1]}"


def fmt_input(d):
    return d.strftime("%d.%m.%Y")


def parse_date(text):
    """'ДД.ММ.ГГГГ' -> date, иначе None."""
    try:
        return datetime.strptime(text.strip(), "%d.%m.%Y").date()
    except ValueError:
        return None


def parse_time(text):
    """'' -> '' (время не задано), 'ЧЧ:ММ' -> 'ЧЧ:ММ', ошибка -> None."""
    text = text.strip()
    if not text:
        return ""
    try:
        return datetime.strptime(text, "%H:%M").strftime("%H:%M")
    except ValueError:
        return None
