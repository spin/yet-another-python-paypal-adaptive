import unittest
from decimal import Decimal

from yappa.models import Receiver
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
