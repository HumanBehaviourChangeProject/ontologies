import logging


class CustomFormatter(logging.Formatter):

    bold = "\033[1m"
    normal = "\033[22m"
    lightblue = "\x1b[36;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = f"[ %(asctime)s ] [ {bold}%(levelname)s{normal} ][ %(name)s:%(funcName)s ] %(message)s"

    FORMATS = {
        logging.DEBUG: lightblue + format + reset,
        logging.INFO: lightblue + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def setup_logging():
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(CustomFormatter())

    logging.basicConfig(format='[%(asctime)s][%(levelname)s][%(name)s - %(funcName)s] %(message)s', level=logging.DEBUG,
                        handlers=[
                            ch])

