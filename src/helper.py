import sys
import time
from datetime import timedelta

from dotenv import dotenv_values
from unidecode import unidecode


def get_query_id(query):
    q = unidecode(query.lower())
    if "petrobras" in q:
        return 0
    if "brumadinho" in q:
        return 1
    if "renner" in q:
        return 2
    if "pandemia" in q:
        return 3
    if "mariana" in q:
        return 4


def update_progress(start, text, progress):
    bar_length = 30
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(bar_length * progress))
    end = time.time()
    total = end - start
    total_progress = progress * 100
    total_progress = total_progress if total_progress > 0 else 1
    perspective = total * 100 / total_progress
    total = timedelta(seconds=total)
    perspective = timedelta(seconds=perspective)
    text = "\r{5}: [{0}] {1}% {2} {3} {4};".format("#" * block + "-" * (bar_length - block),
                                                   total_progress,
                                                   status, total, perspective, text)
    sys.stdout.write(text)
    sys.stdout.flush()
    return progress


def load_config():
    while True:
        path = "./"
        config = dotenv_values(path + ".env")
        if len(config.keys()) == 0:
            path += "../"
        else:
            return config
