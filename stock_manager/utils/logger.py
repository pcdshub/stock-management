"""
Logger utility for Stock Management Application.

Initializes static logger for logging messages to a file with different severity levels.

Logger can be used by referencing `logging.getLogger()` after `Logger()` is run.
"""

import logging
import sys


class Logger:
    """
    Logger utility for writing informational, warning, and error logs to a file and the console.
    """
    
    def __init__(self):
        """
        Configures the logging module to write logs to 'app.log' with timestamps and severity levels.
        
        Also prints messages to the console with severity levels.
        """
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
        
        logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                handlers=[
                    logging.FileHandler('app.log'),
                    handler
                ]
        )
