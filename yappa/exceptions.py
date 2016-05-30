
class AdaptiveApiException(Exception):
    pass


class PayException(AdaptiveApiException):
    pass


class PreApprovalException(AdaptiveApiException):
    pass


class InvalidReceiverException(AdaptiveApiException):
    pass
