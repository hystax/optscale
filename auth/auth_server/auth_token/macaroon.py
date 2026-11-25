import time
import logging
from pymacaroons import Macaroon, Verifier

LOG = logging.getLogger(__name__)
MFA_NONE = 'none'


class MacaroonToken(object):

    def __init__(self, secret, ident, location=''):
        self._secret = secret
        self._ident = ident
        self._location = location

    def create(self, register, provider, mfa=MFA_NONE):
        macaroon = Macaroon(
            location=self._location,
            identifier=self._ident,
            key=self._secret
        )
        macaroon.add_first_party_caveat(f'created:{time.time()}')
        macaroon.add_first_party_caveat(f'register:{register}')
        macaroon.add_first_party_caveat(f'provider:{provider}')
        macaroon.add_first_party_caveat(f'mfa:{mfa}')
        return macaroon.serialize()

    def verify(self, token):
        try:
            macaroon = Macaroon.deserialize(token)
            verifier = Verifier()
            verifier.satisfy_general(lambda x: True)
            return verifier.verify(macaroon, self._secret)
        except Exception as exc:
            LOG.warning('Cannot verify token %s, exception %s', token,
                        str(exc))
            return False
