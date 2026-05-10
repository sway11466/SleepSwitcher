import os
from datetime import date
from importlib.resources import files

_holidayjp = None
_csv_path = None
_csv_mtime = None


def is_holiday(d: date) -> bool:
    global _holidayjp, _csv_path, _csv_mtime
    if _csv_path is None:
        _csv_path = str(files('holiday_jp').joinpath('syukujitsu.csv'))
    mtime = os.path.getmtime(_csv_path)
    if _holidayjp is None or mtime != _csv_mtime:
        from holiday_jp import HolidayJP
        _holidayjp = HolidayJP()
        _csv_mtime = mtime
    return _holidayjp.is_holiday(d)
