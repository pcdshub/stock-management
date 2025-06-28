import sys

from PyQt6.QtWidgets import QApplication

from stock_manager.app import App


def main():
	app = QApplication([])
	# app = QApplication(sys.argv)
	window = App()
	window.run()
	window.show()
	sys.exit(app.exec())


if __name__ == '__main__':
	main()
