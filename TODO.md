
### Add Django integration usage
```
from django.conf import settings
debug = hasattr(settings, 'DEBUG', False)

preapproval = PreApproval(credentials=self.credentials, debug=debug)

```
