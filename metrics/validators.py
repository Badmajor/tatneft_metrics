import time

from django.core.exceptions import ValidationError


def validate_unix_timestamp(value: int) -> None:
    """
    Валидирует Unix timestamp в секундах.
    Больше 1 января 2020 года, но не больше текущего момента
    """
    if value <= 0:
        raise ValidationError("Timestamp должен быть положительным числом")

    # 01-01-2020
    min_ts = 1577836800
    now_ts = int(time.time())

    if not (min_ts <= value <= now_ts):
        raise ValidationError(
            "Timestamp выходит за допустимый диапазон дат. Больше 1 января 2020 года, но не больше текущего момента"
        )
