import os
import sys
from datetime import date

_holidayjp = None
_csv_path_cached = None
_csv_mtime = None


def _resolve_csv_path() -> str:
    appdata = os.path.join(os.environ['APPDATA'], 'SleepSwitcher', 'syukujitsu.csv')
    if os.path.exists(appdata):
        return appdata
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), 'syukujitsu.csv')
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(repo_root, 'assets', 'syukujitsu.csv')


def is_holiday(d: date) -> bool:
    global _holidayjp, _csv_path_cached, _csv_mtime
    path = _resolve_csv_path()
    mtime = os.path.getmtime(path)
    if _holidayjp is None or path != _csv_path_cached or mtime != _csv_mtime:
        from holiday_jp import HolidayJP
        _holidayjp = HolidayJP(csv_path=path, unsupported_date_behavior='ignore')
        _csv_path_cached = path
        _csv_mtime = mtime
    return _holidayjp.is_holiday(d)
