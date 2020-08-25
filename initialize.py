import gmsh
import logging
import sys

# Filters messages of severity less than argument
class LessThanFilter(logging.Filter):
    def __init__(self, exclusive_maximum, name=""):
        super(LessThanFilter, self).__init__(name)
        self.max_level = exclusive_maximum

    def filter(self, record):
        #non-zero return means we log this message
        return 1 if record.levelno < self.max_level else 0

# Logging formatter to add colors to messages using ANSI
class CustomFormatter(logging.Formatter):

    def __init__(self, option=None):
        self.option = option

        purple = "\x1b[35;10m"
        green = "\x1b[32;10m"
        default = "\x1b[39;10m"
        yellow = "\x1b[33;10m"
        red = "\x1b[31;10m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"
                                                                                             
        fmt =      "%(asctime)s %(levelname)-10s: %(name)s - %(message)s"
        debugFmt = "%(asctime)s %(levelname)-10s: %(name)s - (line: %(lineno)d) %(message)s"

        if option == 'debug':
            theFormat = debugFmt
        else:
            theFormat = fmt

        self.FORMATS = {
            logging.DEBUG:    green    + theFormat + reset,
            logging.INFO:     default  + theFormat + reset,
            logging.WARNING:  purple   + theFormat + reset,
            logging.ERROR:    bold_red + theFormat + reset,
            logging.CRITICAL: bold_red + theFormat + reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%H:%M:%S')
        return formatter.format(record)

# Initialize mocmg logger and gmsh with desired level of output.
# The levels are as follows:
#   silent  : For gmsh only. Don't output anything from gmsh
#   error   : Display error messages only
#   warning : Display error and warning messages
#   info    : Display error, warning, and info messages
#   debug   : Display error, warning, info, and debug messages
#
# Inputs:
#   mocmgOption: One of the levels above. String
#   gmshOption: One of the leves above. String
#   color: Option to color the output of log messages from mocmg. True or False
def initialize(Option=None, color=True):
    # mocmg
    if Option == 'debug':
        Verbosity = logging.DEBUG
    elif Option == 'warning':
        Verbosity = logging.WARNING
    elif Option == 'error':
        Verbosity = logging.ERROR
    elif Option == 'silent':
        Verbosity = 99
    else:
        Verbosity = logging.INFO

    # Get the root logger
    logger = logging.getLogger()
    # Have to set the root logger level, it defaults to logging.WARNING
    logger.setLevel(logging.NOTSET)
    # Format stdout and stderr based upon color and debug mode
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-10s: %(name)s - %(message)s', 
            datefmt='%H:%M:%S')
    debugFormatter = logging.Formatter(fmt='%(asctime)s %(levelname)-10s: %(name)s - (line: %(lineno)d) %(message)s', 
            datefmt='%H:%M:%S')

    # Stdout
    logging_handler_out = logging.StreamHandler(sys.stdout)
    logging_handler_out.setLevel(Verbosity)
    logging_handler_out.addFilter(LessThanFilter(logging.WARNING))

    # If stdout is terminal, color if desired. Otherwise, don't color.
    if color and sys.stdout.isatty():
        if Option == 'debug':
            logging_handler_out.setFormatter(CustomFormatter(option='debug'))
        else:
            logging_handler_out.setFormatter(CustomFormatter())
    else:
        if Option == 'debug':
            logging_handler_out.setFormatter(debugFormatter)
        else:
            logging_handler_out.setFormatter(formatter)
    logger.addHandler(logging_handler_out)

    # Stderr
    logging_handler_err = logging.StreamHandler(sys.stderr)
    lvl = max(logging.WARNING, Verbosity)
    logging_handler_err.setLevel(lvl)

    # If stderr is terminal, color if desired. Otherwise, don't color.
    if color and sys.stderr.isatty():
        if Option == 'debug':
            logging_handler_err.setFormatter(CustomFormatter(option='debug'))
        else:
            logging_handler_err.setFormatter(CustomFormatter())
    else:
        if Option == 'debug':
            logging_handler_err.setFormatter(debugFormatter)
        else:
            logging_handler_err.setFormatter(formatter)
    logger.addHandler(logging_handler_err)
