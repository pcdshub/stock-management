"""
Main entry point for the SLAC Inventory Management Application.

Initializes the Qt Application and launches the main application window.
"""

import asyncio
import sys

from PyQt5.QtWidgets import QApplication
from qasync import QEventLoop

from stock_manager import App
from stock_manager.cli import build_commands, entry_point


def main():
    """Start the Qt application and show the main window."""
    
    args = build_commands()
    
    if not entry_point(args):
        return
    
    # try:
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = App()
    window.run()
    window.show()
    
    with loop:
        loop.run_forever()


# except Exception as e:
# 	from stock_manager.utils.logger import Logger

# 	print(f'Fatal Error In Main(): {e}')
# 	Logger().error_log(f'Fatal Error In Main(): {e}')
# 	QMessageBox.critical(
# 			None,
# 			'Fatal Error',
# 			'Fatal Error Starting The Application'
# 	)
# 	raise SystemExit(1)


if __name__ == '__main__':
    main()
