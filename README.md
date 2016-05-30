# Yet Another Python Paypal Adaptive 

A simple python wrapper of Paypal Adaptive APIs.


## Prerequisites

- Python >= 3.4
- requests >= 2.10.0

## Installation
```
python setup.py install
```

## Usage

### Example of credentials
```
credentials = {
    'PAYPAL_USER_ID': <User ID>,
    'PAYPAL_PASSWORD': <User Password>,
    'PAYPAL_SIGNATURE': <User Signature>,
    'PAYPAL_APP_ID': <Application ID>
}
```

### Example of request preapproval for future payments
```
from decimal import Decimal
from yappa.api import PreAproval

# debug=True will use sandbox
preapproval = PreApproval(credentials, debug=True)

resp = preapproval.request(
    startingDate='2016-05-28T00:33:00+08:0',
    endingDate='2016-06-28T00:33:00+08:0',
    currencyCode='USD',
    returnUrl='http://return.url',
    cancelUrl='http://cancel.url',
    maxAmountPerPayment=Decimal('50.00'),
    maxNumberOfPayments=20,
    maxTotalAmountOfAllPayments=Decimal('1500.00')
)

# Get preapproval key and authorization URL
preapproval_key = resp.preapprovalKey
auth_url = resp.nextUrl
```

### Example of capture payments
```
from decimal import Decimal
from yappa.api import Pay
from yappa.models import Receiver, ReceiverList

receivers = [
    Receiver(email='receiver1@gmail.com', amount=Decimal('10.00')),
    Receiver(email='receiver2@gmail.com', amount=Decimal('15.00'))
]
    
receiver_list = ReceiverList(receivers)

pay = Pay(self.credentials, debug=True)

resp = pay.request(
    currencyCode='USD',
    returnUrl='http://return.url',
    cancelUrl='http://cancel.url',
    senderEmail='sender@gmail.com',
    memo='some message',
    receiverList=receiver_list
)

# Get pay key and payment details
pay_key = resp.payKey
exec_status = resp.paymentExecStatus    # COMPLETED
sender = resp.sender    # {'accountId': 'XXXAAABBB'}
payment_info = resp.paymentInfoList
```