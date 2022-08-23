from herald_server.controllers.base import BaseController
from herald_server.models.models import Reaction
from herald_server.models.types import ReactionTypes
from herald_server.processors.factory import ProcessorFactory
from herald_server.exceptions import Err

from optscale_exceptions.common_exc import WrongArgumentsException
from optscale_types.utils import check_string_attribute, is_valid_meta


class ReactionController(BaseController):
    def _get_model_type(self):
        return Reaction

    def _validate_creation(self, **kwargs):
        self.check_create_restrictions(**kwargs)
        self._validate_reaction(**kwargs)

    @staticmethod
    def _validate_reaction(**reaction):
        name = reaction.get('name')
        if name is not None:
            check_string_attribute('name', name)
        reaction_type = reaction.get('type')

        if reaction_type is None:
            raise WrongArgumentsException(Err.G0015, [])
        check_string_attribute('type', reaction_type)
        try:
            reaction_type = ReactionTypes[reaction_type]
        except KeyError:
            raise WrongArgumentsException(Err.G0023, [reaction_type])
        payload = reaction.get('payload')
        check_string_attribute('payload', payload)
        if not is_valid_meta(payload):
            raise WrongArgumentsException(Err.G0016, [])
        processor = ProcessorFactory.get(reaction_type)
        processor.validate_payload(payload)

    def create(self, **kwargs):
        self._validate_creation(**kwargs)
        reaction = Reaction(**kwargs)
        return reaction
