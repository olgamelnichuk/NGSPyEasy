#!/usr/bin/env python

import logging
import os.path
from settings import VERSION, RUNDATE


CURRENT_STEP = ["ngspyeasy"]

def init_logger(logdir, tsv_name, verbose):
    logfile = os.path.join(logdir, "ngspyeasy." + VERSION + "." + tsv_name + "." + RUNDATE)

    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s : %(message)s')

    file_handler = logging.FileHandler(logfile, mode='w')
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


def get_logger():
    return logging.getLogger()


def log_error(msg, *args):
    get_logger().error(with_step(msg), args)


def log_debug(msg, *args):
    get_logger().debug(with_step(msg), args)


def log_info(msg, *args):
    get_logger().info(with_step(msg), args)


def log_warn(msg, *args):
    get_logger().warn(with_step(msg), args)


def log_set_current_step(step):
    CURRENT_STEP[0] = step


def with_step(msg):
    return "[" + CURRENT_STEP[0] + "]:" + msg