import logging
import sys

def initialize_logging(logger, debug, filename):
    log_name = f"./logs/{filename}.log"

    console = logging.StreamHandler()
    file = logging.FileHandler(log_name)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s")

    if debug:
        console.setLevel(logging.DEBUG)
        file.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        console.setLevel(logging.INFO)
        file.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)

    console.setFormatter(formatter)
    file.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file)
