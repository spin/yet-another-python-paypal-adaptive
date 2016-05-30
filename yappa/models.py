from decimal import Decimal

from yappa.exceptions import InvalidReceiverException


class Receiver(object):

    def __init__(self, *, email, amount, primary=None):  # Only keyword arguments accepted
        if not isinstance(amount, Decimal):
            raise InvalidReceiverException('amount needs to be instance of Decimal')
        elif primary is not None and not isinstance(primary, bool):
            raise InvalidReceiverException('primary argument needs to be Boolean type')

        self.email = email
        self.amount = amount
        self.primary = primary

    def to_dict(self):
        result = {
            'email': self.email,
            'amount': str(self.amount)
        }

        if self.primary is not None:
            result['primary'] = str(self.primary).lower()

        return result

    def __unicode__(self):
        return self.email


class ReceiverList(object):
    MAX_RECEIVER_AMOUNT = 6

    def __init__(self):
        pass
