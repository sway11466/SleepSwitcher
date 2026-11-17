import ctypes
import subprocess
import winreg
from datetime import datetime

_NO_WINDOW = subprocess.CREATE_NO_WINDOW

# このキーは BUILTIN\Users に SetValue が許可されており、管理者権限なしで書き込める
_SETTINGS_KEY = r'SOFTWARE\Microsoft\WindowsUpdate\UX\Settings'
_REBOOT_KEY = (
    r'SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired'
)

WINDOW_HOURS = 18       # Windows が許すアクティブ時間の最大幅
SHIFT_MARGIN_MIN = 60   # 終了までの残りがこれ以下になったら窓をずらす


def next_active_hours(start: int, end: int, now: datetime) -> tuple[int, int] | None:
    """窓をずらす必要があれば新しい (start, end) を、不要なら None を返す。

    現在時刻が窓の外、または終了まで SHIFT_MARGIN_MIN 分以内のときだけ、
    開始を「現在の時（過ぎた正時）」に置き直す。
    """
    span = ((end - start) % 24) * 60
    elapsed = (now.hour * 60 + now.minute - start * 60) % 1440
    if elapsed < span and span - elapsed > SHIFT_MARGIN_MIN:
        return None
    return now.hour, (now.hour + WINDOW_HOURS) % 24


def read_active_hours() -> tuple[int, int]:
    with winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE, _SETTINGS_KEY, 0,
        winreg.KEY_QUERY_VALUE | winreg.KEY_WOW64_64KEY,
    ) as k:
        start, _ = winreg.QueryValueEx(k, 'ActiveHoursStart')
        end, _   = winreg.QueryValueEx(k, 'ActiveHoursEnd')
    return start, end


def write_active_hours(start: int, end: int) -> None:
    with winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE, _SETTINGS_KEY, 0,
        winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY,
    ) as k:
        winreg.SetValueEx(k, 'ActiveHoursStart', 0, winreg.REG_DWORD, start)
        winreg.SetValueEx(k, 'ActiveHoursEnd',   0, winreg.REG_DWORD, end)


def keep_active(now: datetime) -> None:
    """現在時刻が常にアクティブ時間内に収まるよう、必要なときだけ窓をずらす"""
    new = next_active_hours(*read_active_hours(), now)
    if new:
        write_active_hours(*new)


def is_reboot_pending() -> bool:
    try:
        winreg.CloseKey(winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, _REBOOT_KEY, 0,
            winreg.KEY_QUERY_VALUE | winreg.KEY_WOW64_64KEY,
        ))
        return True
    except OSError:
        return False


class _LASTINPUTINFO(ctypes.Structure):
    _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]


def seconds_since_last_input() -> float:
    """最後のキーボード・マウス入力からの経過秒"""
    info = _LASTINPUTINFO()
    info.cbSize = ctypes.sizeof(info)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info))
    # GetTickCount は 32bit で一周するため差分も 32bit で取る
    tick = ctypes.windll.kernel32.GetTickCount() & 0xFFFFFFFF
    return ((tick - info.dwTime) & 0xFFFFFFFF) / 1000


def restart() -> None:
    subprocess.run(['shutdown', '/r', '/t', '0'], check=True, creationflags=_NO_WINDOW)
