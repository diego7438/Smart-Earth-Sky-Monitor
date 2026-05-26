import logging
import os

def setup_logger():
    # Create logs folder if it doesn't exist
    os.makedirs("logs", exist_ok = True)

    logging.basicConfig(
        level = logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            # Write to file permanently
            logging.FileHandler("logs/monitor.log"),
            # Also print to terminal
            logging.StreamHandler()
        ]
    )

    return logging.getLogger(__name__)

logger = setup_logger()