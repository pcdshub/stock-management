import logging

logging.basicConfig(
        filename='assets/test.log',
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
)
logging.info("App started")
logging.warning("Low stock for item ID=5")
logging.error("Failed to connect to database")
