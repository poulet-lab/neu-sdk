from logging import Formatter, Logger, getLogger

from rich.console import Console
from rich.logging import RichHandler

from neu_sdk.config import settings


def setup_logging(
    logger: Logger,
    terminal_width: int | None = None,
    show_time: bool = False,
    show_path: bool = True,
    markup: bool = True,
    rich_tracebacks: bool = True,
    tracebacks_extra_lines: int = 3,
    tracebacks_word_wrap: bool = True,
    tracebacks_show_locals: bool = True,
    level: int | str = settings.log_level.upper(),
) -> None:

    console = Console(width=terminal_width) if terminal_width else None
    rich_handler = RichHandler(
        show_time=show_time,
        rich_tracebacks=rich_tracebacks,
        tracebacks_show_locals=tracebacks_show_locals,
        tracebacks_word_wrap=tracebacks_word_wrap,
        tracebacks_extra_lines=tracebacks_extra_lines,
        markup=markup,
        show_path=show_path,
        console=console,
    )
    rich_handler.setFormatter(Formatter("%(message)s"))
    logger.addHandler(rich_handler)

    logger.setLevel(level)
    logger.propagate = False


LOGGER = getLogger(settings.neu.service.name)
setup_logging(logger=LOGGER, level=settings.log_level.upper())
