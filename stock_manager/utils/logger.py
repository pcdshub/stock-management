"""
Logger utility for Stock Management Application.

Provides static methods for logging messages to a file with different severity levels.
"""

import logging as log


class Logger:
	"""
	Logger utility for writing informational, warning, and error logs to a file.
	"""
	
	def __init__(self):
		"""
		Configures the logging module to write logs to 'app.log' with timestamps and severity levels.
		"""
		log.basicConfig(
				filename='app.log',
				level=log.INFO,
				format='%(asctime)s [%(levelname)s] %(message)s',
				datefmt='%Y-%m-%d %H:%M:%S'
		)
	
	@staticmethod
	def info_log(msg: str) -> None:
		"""
		Logs an informational message to the app log.
		
		:param msg: Message to be logged.
		"""
		log.info(msg)
	
	@staticmethod
	def warning_log(msg: str) -> None:
		"""
		Logs a warning message to the app log.
		
		:param msg: Message to be logged.
		"""
		log.warning(msg)
	
	@staticmethod
	def error_log(msg: str) -> None:
		"""
		Logs an error message to the app log.
		
		:param msg: Message to be logged.
		"""
		log.error(msg)
