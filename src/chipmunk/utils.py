import logging
import unicodedata
import re
import sys


def sanitize_name(name):
    name = unicodedata.normalize("NFKD", name).encode("ASCII", "ignore").decode("ASCII")
    name = re.sub(r"[^\w\-_. ]", "", name)
    name = name.strip().replace(" ", "_")
    if not name:
        name = "unnamed"
    return name


def setup_logger(log_path=None):
    logger = logging.getLogger("chipmunk")
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("%(asctime)s  %(levelname)-8s %(message)s", datefmt="%H:%M:%S")

    if not logger.handlers:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(fmt)
        logger.addHandler(ch)

        if log_path:
            fh = logging.FileHandler(log_path, encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(fmt)
            logger.addHandler(fh)

    return logger
