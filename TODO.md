
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