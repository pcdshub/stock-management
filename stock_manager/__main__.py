"""
Main entry point for the SLAC Inventory Management Application.

Initializes the Qt Application and launches the main application window.
"""

import asyncio
import logging
import sys

from PyQt5.QtWidgets import QApplication, QMessageBox
from qasync import QEventLoop

import stock_manager
from stock_manager import App
from stock_manager.cli import build_commands


def main() -> None:
    """
    Entry point for the stock management application.

    Parses command-line arguments and determines whether to launch the GUI
    or handle CLI-only commands.

    Handles unexpected exceptions during startup, logs critical errors to
    `app.log`, displays a fatal error dialog, and exits.

    If CLI mode completes successfully or doesn't require GUI, the Qt application is never run.
    If GUI mode is selected, initializes the Qt application and runs the main event loop.

    :raise SystemExit: If a fatal error occurs during GUI startup.
    """
    
    stock_manager.utils.Logger()
    
    args = build_commands()
    
    if not args:
        return
    
    if hasattr(args, 'func'):
        args.func(args)
        return
    
    try:
        app = QApplication(sys.argv)
        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)
        window = App()
        window.run()
        window.show()
        
        with loop:
            loop.run_forever()
    except Exception as e:
        logging.getLogger().error(f'Fatal Error In Main(): {e}')
        QMessageBox.critical(
                None,
                'Fatal Error',
                'Fatal Error Starting The Application'
        )
        raise SystemExit(1)


if __name__ == '__main__':
    main()
