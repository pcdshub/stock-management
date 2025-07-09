"""
Main entry point for the SLAC Inventory Management Application.

Initializes the Qt Application and launches the main application window.
"""

import asyncio

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop

from stock_manager import App


def main():
	"""Start the Qt application and show the main window."""
	
	# try:
	app = QApplication([])  # TODO: if command line arguments are used, swap [] for sys.argv
	loop = QEventLoop(app)
	asyncio.set_event_loop(loop)
	window = App()
	window.show()
	
	QTimer.singleShot(0, lambda: asyncio.create_task(window.run()))
	
	with loop:
		loop.run_forever()
	# except Exception as e:
	# 	from stock_manager.utils.logger import Logger
#
	# 	Logger().error_log(f"Fatal error in main(): {e}")
	# 	print(f"Fatal error in main(): {e}")
	# 	sys.exit(1)
# TODO: uncomment try except later


if __name__ == '__main__':
	main()
