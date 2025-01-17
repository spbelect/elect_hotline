import logging
import loguru
import inspect


class ToLoguru(logging.Handler):
    """
    This Handler redirects all stdlib logging to loguru.

    Usage:

    >> import logging
    >> logging.basicConfig(handlers=[ToLoguru()], level=0, force=True)

    """

    def emit(self, record: logging.LogRecord) -> None:

        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = loguru.logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        loguru.logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
