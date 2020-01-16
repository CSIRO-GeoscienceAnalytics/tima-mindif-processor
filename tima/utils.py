from loguru import logger


create_thumbnail = False


def log_variable(name, value):
    logger.debug("{}: {}", name, value)


def log_message(message):
    logger.debug(message)


def get_percent_text(value):
    if value < 0.01:
        return "<0.01"
    return "{:4.2f}".format(value)
