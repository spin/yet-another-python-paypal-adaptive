
## Django integration

### Preapproval with Django form
```
from django.conf import settings
debug = hasattr(settings, 'DEBUG', False)

paypal_credentials = 

preapproval = PreApproval(credentials=paypal_credentials, debug=debug)

data = form.cleaned_data
preapproval.request(**data)

```

## Questions

- In `Pay` operation, is the `ClientDetails` field necessary?

- Need to support other payment operations? (Chained, Delayed Chained)

## TODO

- Need to check there should be only one primary receiver