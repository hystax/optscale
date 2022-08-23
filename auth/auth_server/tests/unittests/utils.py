from pymacaroons import Macaroon


def extract_caveats(token):
    macaroon = Macaroon.deserialize(token)
    return dict(
        map(
            lambda x: (
                x.to_dict()['cid'].split(':')[0], x.to_dict(
                )['cid'].split(':')[1]), macaroon.caveats))
