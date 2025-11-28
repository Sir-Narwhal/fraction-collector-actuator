class CollectorLogicError(Exception):
    """Will trigger an error with the collection logic

    Args:
        Exception (_type_): _description_
    """

    pass


class NoFlowrateError(CollectorLogicError):
    """Will be raised when there are no flow rates

    Args:
        CollectorLogicError (_type_): _description_
    """

    pass
