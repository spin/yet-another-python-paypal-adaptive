import unittest
from decimal import Decimal

from yappa.models import Receiver, ReceiverList
from yappa.exceptions import InvalidReceiverException


class ModelTestCase(unittest.TestCase):
    def setUp(self):
        self.receiver_email = 'fake_receiver@gmail.com'

    def tearDown(self):
        pass

    def test_init_receiver_with_empty_email(self):
        with self.assertRaises(TypeError) as context:
            Receiver(amount=Decimal('12.5'))

    def test_init_receiver_with_empty_amount(self):
        with self.assertRaises(TypeError) as context:
            Receiver(email=self.receiver_email)

    def test_init_receiver_with_invalid_amount(self):
        with self.assertRaises(InvalidReceiverException) as context:
            Receiver(email=self.receiver_email, amount=22.2)

        self.assertEquals(context.exception.args[0], 'amount needs to be instance of Decimal')

    def test_init_receiver_with_invalid_primary_argument(self):
        with self.assertRaises(InvalidReceiverException) as context:
            Receiver(email=self.receiver_email, amount=Decimal('22.2'), primary='True')

        self.assertEquals(context.exception.args[0], 'primary argument needs to be Boolean type')

    def test_primary_receiver(self):
        receiver = Receiver(email=self.receiver_email, amount=Decimal('22.2'), primary=True)

        self. assertEquals(receiver.to_dict(), {
            'email': self.receiver_email,
            'amount': '22.2',
            'primary': 'true'
        })

    def test_not_primary_receiver(self):
        receiver = Receiver(email=self.receiver_email, amount=Decimal('22.2'), primary=False)

        self.assertEquals(receiver.to_dict(), {
            'email': self.receiver_email,
            'amount': '22.2',
            'primary': 'false'
        })

    def test_init_receiver_list_exceed_the_maximum(self):
        receivers = [Receiver(email='receiver{}@gmail.com'.format(i+1),
                              amount=Decimal('10.0')) for i in range(7)]

        with self.assertRaises(InvalidReceiverException) as context:
            ReceiverList(receivers)

        self.assertEquals(context.exception.args[0], 'each payment request has a maximum of 6 receivers')

    def test_append_receiver_that_exceed_the_maxium(self):
        receivers = [Receiver(email='receiver{}@gmail.com'.format(i + 1),
                              amount=Decimal('10.0')) for i in range(6)]

        receiver_list = ReceiverList(receivers)

        with self.assertRaises(InvalidReceiverException) as context:
            receiver_list.append(Receiver(email='boom@gmail.com', amount=Decimal('66.6')))

        self.assertEquals(context.exception.args[0], 'each payment request has a maximum of 6 receivers')

    def test_append_invalid_receiver(self):
        receiver_list = ReceiverList()

        with self.assertRaises(InvalidReceiverException) as context:
            receiver_list.append({})

        self.assertEquals(context.exception.args[0], 'receiver needs to be instance of yappa.models.Reciever')

    def test_init_receiver_list_successfully(self):
        receivers = [Receiver(email='receiver{}@gmail.com'.format(i + 1),
                              amount=Decimal(10+i*5)) for i in range(3)]

        receiver_list = ReceiverList(receivers)

        self.assertEquals(receiver_list.to_json(), [
            {'email': 'receiver1@gmail.com', 'amount': '10'},
            {'email': 'receiver2@gmail.com', 'amount': '15'},
            {'email': 'receiver3@gmail.com', 'amount': '20'},
        ])

    def test_append_receiver_successfully(self):
        receiver_list = ReceiverList([Receiver(email='first@gmail.com', amount=Decimal('11.1'))])

        self.assertEquals(receiver_list.to_json(), [{'email': 'first@gmail.com', 'amount': '11.1'}])

        receiver_list.append(Receiver(email='second@gmail.com', amount=Decimal('22.2')))

        self.assertEquals(receiver_list.to_json(), [
            {'email': 'first@gmail.com', 'amount': '11.1'},
            {'email': 'second@gmail.com', 'amount': '22.2'},
        ])
