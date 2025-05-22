from bot_create import PL

logger = PL.new_logger("utils", "yellow")


def get_logger(name, color=None) -> PL.logger:
    return PL.new_child(logger, name, color)
