import string
import random

STORAGE_BASE_UNIT = 1000.0


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < STORAGE_BASE_UNIT:
            return f"{num:3.1f}{unit}{suffix}"
        num /= STORAGE_BASE_UNIT
    return f"{num:.1f}Yi{suffix}"


def str_to_set(input_str):
    result = {s.strip() for s in input_str.split(",")}
    result = {s for s in result if s}
    return result


def random_string(charset=string.ascii_uppercase + string.digits, n=10):
    return "".join(random.choice(charset) for _ in range(n))
