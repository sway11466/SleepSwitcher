import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from core.state_manager import StateManager
from ui.tray_app import TrayApp


def main():
    manager = StateManager()
    app = TrayApp(manager)
    manager.set_state_change_callback(app._refresh)
    app.run()


if __name__ == '__main__':
    main()
