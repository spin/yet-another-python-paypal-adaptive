

class Receiver(object):

    def __init__(self, *, email, amount, primary=None):  # Only keyword arguments accepted
        self.email = email,
        self.amount = amount,
        self.primary = primary

    def to_dict(self):
        dict = {
            'email': self.email,
            'amount': self.amount
        }

        if self.primary is not None:
            dict['primary'] = self.primary

        return dict

    def __unicode__(self):
        return self.email


class ReceiverList(object):
    MAX_RECEIVER_AMOUNT = 6

    def __init__(self):
        pass
