"""
Main entry point for the SLAC Inventory Management Application.

Initializes the Qt Application and launches the main application window.
"""

import sys

from PyQt6.QtWidgets import QApplication

from stock_manager import App


def main():
	"""Start the Qt application and show the main window."""
	# try:
	app = QApplication([])  # TODO: if command line arguments are used, swap [] for sys.argv
	window = App()
	window.run()
	window.show()
	sys.exit(app.exec())
	# except Exception as e:
	# 	from stock_manager.utils.logger import Logger
#
	# 	Logger().error_log(f"Fatal error in main(): {e}")
	# 	print(f"Fatal error in main(): {e}")
	# 	sys.exit(1)
# TODO: uncomment try except later


if __name__ == '__main__':
	main()
