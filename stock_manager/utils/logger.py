import logging as log


class Logger:
	def __init__(self):
		log.basicConfig(
				filename='app.log',
				level=log.INFO,
				format='%(asctime)s [%(levelname)s] %(message)s',
				datefmt='%Y-%m-%d %H:%M:%S'
		)
	
	@staticmethod
	def info_log(msg: str):
		"""
		Logs a specified message in ../app.log.
		Prepends message with timestamp and [INFO]
		:param msg: message to be logged
		"""
		log.info(msg)
	
	@staticmethod
	def warning_log(msg: str):
		"""
		Logs a specified message in ../app.log.
		Prepends message with timestamp and [WARNING]
		:param msg: message to be logged
		"""
		log.warning(msg)
	
	@staticmethod
	def error_log(msg: str):
		"""
		Logs a specified message in ../app.log.
		Prepends message with timestamp and [ERROR]
		:param msg: message to be logged
		"""
		log.error(msg)
