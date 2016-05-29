
class Settings(object):
    def __init__(self, debug=False):

        if debug:
            self.PAYPAL_ENDPOINT = 'https://svcs.sandbox.paypal.com/AdaptivePayments'
            self.PAYPAL_AUTH_URL = 'https://www.sandbox.paypal.com/cgi-bin/webscr'
            self.PAYAPL_APP_ID = 'APP-80W284485P519543T'

        else:
            self.PAYPAL_ENDPOINT = 'https://svcs.paypal.com/AdaptivePayments'
            self.PAYPAL_AUTH_URL = 'https://www.paypal.com/webscr'
            self.PAYAPL_APP_ID = None
