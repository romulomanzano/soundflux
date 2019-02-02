from stat import ST_MTIME
import os
import logging
import config
import numpy as np

FORMATTER = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

def logged(class_):
    logger = logging.getLogger(class_.__name__)
    formatter = FORMATTER
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    class_.logger = logger
    return class_


def get_files_with_mtime(path,file_extension):
    # get all entries in the directory w/ stats
    entries = (os.path.join(path, file) for file in os.listdir(path))
    entries = ((os.stat(path), path) for path in entries)

    # leave only regular files, insert creation date
    entries = ((stat[ST_MTIME], path) for stat, path in entries if file_extension in path)
    return entries

def simple_mfcc_aggregation(mfccs):
    return np.mean(mfccs, axis=0)
