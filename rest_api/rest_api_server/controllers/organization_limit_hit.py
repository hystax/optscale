import logging
from sqlalchemy.sql import and_, exists
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.base import BaseController
from rest_api.rest_api_server.controllers.organization_constraint import (
    ConstraintRunValidationMixin)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.models import (
    Organization, OrganizationConstraint, OrganizationLimitHit)
from tools.optscale_exceptions.common_exc import (ConflictException,
                                                  NotFoundException)

LOG = logging.getLogger(__name__)


class OrganizationLimitHitController(BaseController,
                                     ConstraintRunValidationMixin):
    def __init__(self, db_session, config=None, token=None, engine=None):
        super().__init__(db_session, config, token, engine)
        self._organization_ctrl = None

    def _get_model_type(self):
        return OrganizationLimitHit

    def _get_entity(self, entity_type, entity_id):
        entity = self.session.query(entity_type).filter(
            entity_type.id == entity_id,
            entity_type.deleted.is_(False)
        ).one_or_none()
        if not entity:
            raise NotFoundException(Err.OE0002, [entity_type.__name__,
                                                 entity_id])
        return entity

    def _validate(self, item, is_new=True, **kwargs):
        if is_new:
            self.check_organization(item.organization_id)
            self.get_constraint(item.constraint_id, item.organization_id)
            self.check_limit_hit_exists(item.organization_id, item.constraint_id,
                                        item.created_at)
        if 'run_result' in kwargs:
            constraint = self.get_constraint(item.constraint_id,
                                             item.organization_id)
            self._check_run_result(
                'run_result', constraint.type, kwargs.get('run_result'))

    def check_organization(self, organization_id):
        self._get_entity(Organization, organization_id)

    def get_constraint(self, constraint_id, organization_id):
        constraint = self._get_entity(OrganizationConstraint, constraint_id)
        if constraint.organization_id != organization_id:
            raise NotFoundException(Err.OE0002, [
                OrganizationConstraint.__name__, constraint.id])
        return constraint

    def check_limit_hit_exists(self, organization_id, constraint_id, created_at):
        hit_exist = self.session.query(
            exists().where(and_(
                OrganizationLimitHit.organization_id == organization_id,
                OrganizationLimitHit.constraint_id == constraint_id,
                OrganizationLimitHit.created_at == created_at,
                OrganizationLimitHit.deleted.is_(False)
            ))
        ).scalar()
        if hit_exist:
            raise ConflictException(Err.OE0516, [constraint_id,
                                                 organization_id])

    def list(self, **kwargs):
        result = []
        organization_id = kwargs['organization_id']
        self.check_organization(organization_id)
        constraint_id = kwargs.get('constraint_id')
        if constraint_id:
            self.get_constraint(constraint_id, organization_id)
        hits = super().list(**kwargs)
        for hit in hits:
            result.append(hit.to_dict())
        return result


class OrganizationLimitHitAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return OrganizationLimitHitController
