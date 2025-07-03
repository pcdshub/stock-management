from pathlib import Path

from PyQt6.QtWidgets import QWidget
from PyQt6.uic import loadUi

from .abstract_controller import AbstractController


class Finish(QWidget, AbstractController):
	def __init__(self, app):
		super(Finish, self).__init__()
		
		try:
			ui_path = Path(__file__).resolve().parent.parent.parent / 'ui' / 'finish.ui'
			loadUi(str(ui_path), self)
		except Exception as e:
			app.log.error_log(f"Failed to load scanner UI file: {e}")
			raise
		
		self.handle_side_ui(self.view_btn, self.qr_btn, self.edit_btn, self.remove_btn, self.exit_btn, app.screens)
		
		self.pushButton.clicked.connect(lambda: app.screens.setCurrentIndex(0))

	def set_text(self, title_txt):
		self.label.setText(title_txt)
