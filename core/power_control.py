import re
import subprocess

_NO_WINDOW = subprocess.CREATE_NO_WINDOW

# powercfg /change の friendly name キーと dict キーのマッピング
_PARAMS = {
    'standby_ac':   'standby-timeout-ac',
    'standby_dc':   'standby-timeout-dc',
    'hibernate_ac': 'hibernate-timeout-ac',
    'hibernate_dc': 'hibernate-timeout-dc',
}

# powercfg /query で使うスリープサブグループと各設定の GUID
_SLEEP_SUBGROUP = '238c9fa8-0aad-41ed-83f4-97be242c8f20'
_STANDBY_SETTING   = '29f6c1db-86da-48c5-9fdb-f2b67b1f44da'
_HIBERNATE_SETTING = '9d7815a6-7ee4-497e-8888-515a05f02364'


def read_all_timeouts() -> dict:
    """Windows の現在の電源設定から4値を読み込む（単位：分）"""
    standby_ac, standby_dc     = _query_setting(_STANDBY_SETTING)
    hibernate_ac, hibernate_dc = _query_setting(_HIBERNATE_SETTING)
    return {
        'standby_ac':   standby_ac,
        'standby_dc':   standby_dc,
        'hibernate_ac': hibernate_ac,
        'hibernate_dc': hibernate_dc,
    }


def write_all_timeouts(values: dict) -> None:
    """4値を Windows に書き込む（単位：分）"""
    for key, param in _PARAMS.items():
        _run_powercfg('/change', param, str(values[key]))


def disable_all() -> None:
    """スリープ・休止状態をすべて無効化（4値を 0 に設定）"""
    for param in _PARAMS.values():
        _run_powercfg('/change', param, '0')


def _query_setting(setting_guid: str) -> tuple[int, int]:
    """指定設定の (AC分, DC分) を返す"""
    result = subprocess.run(
        ['powercfg', '/query', 'SCHEME_CURRENT', _SLEEP_SUBGROUP, setting_guid],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        creationflags=_NO_WINDOW,
    )
    ac = dc = 0
    for line in result.stdout.splitlines():
        if '0x' not in line:
            continue
        match = re.search(r'0x([0-9a-fA-F]+)', line)
        if not match:
            continue
        seconds = int(match.group(1), 16)
        if ' AC ' in line:
            ac = seconds // 60
        elif ' DC ' in line:
            dc = seconds // 60
    return ac, dc


def _run_powercfg(*args: str) -> None:
    subprocess.run(['powercfg'] + list(args), check=True, creationflags=_NO_WINDOW)
