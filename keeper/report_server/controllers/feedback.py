import logging
import json
from mongoengine.queryset.visitor import Q
from datetime import datetime
from mongoengine.errors import ValidationError

from keeper.report_server.exceptions import Err
from keeper.report_server.model import Feedback
from keeper.report_server.controllers.base_async import BaseAsyncControllerWrapper
from keeper.report_server.controllers.event_base import EventBaseController

from tools.optscale_exceptions.common_exc import WrongArgumentsException


LOG = logging.getLogger(__name__)


def is_valid_meta(metadata):
    try:
        meta = json.loads(metadata)
        if not isinstance(meta, dict):
            return False
    except Exception:
        return False
    return True


def _check_filter_json(objects, type):
    if objects and not is_valid_meta(objects):
        raise WrongArgumentsException(Err.OK0032, [type])


class FeedbackController(EventBaseController):
    def check_immutables(self, kwargs):
        for immutable in ["time", "user_id"]:
            if immutable in kwargs:
                raise WrongArgumentsException(Err.OK0041, [immutable])

    def submit(self, **kwargs):
        self.check_immutables(kwargs)
        token = kwargs.pop("token")
        if token:
            user_id = self.get_user_id_by_token(token)
            kwargs.update({"user_id": user_id})
        kwargs["time"] = int(datetime.utcnow().timestamp())
        metadata = kwargs.get("metadata")
        if metadata:
            _check_filter_json(metadata, "metadata")
        feedback = Feedback(**kwargs)
        try:
            feedback.save()
        except ValidationError as exc:
            self.raise_from_validation_error(exc)
        return feedback.to_dict()

    def list(self, **kwargs):
        time_start = kwargs.get("time_start")
        time_end = kwargs.get("time_end")
        user_id = kwargs.get("user_id")
        email = kwargs.get("email")
        url = kwargs.get("url")
        limit = kwargs.get("limit")
        # pylint: disable=no-member
        feedbacks = Feedback.objects().order_by("-time")
        if time_start:
            feedbacks = feedbacks(Q(time__gte=time_start))
        if time_end:
            feedbacks = feedbacks(Q(time__lt=time_end))
        if user_id:
            feedbacks = feedbacks(Q(user_id=user_id))
        if email:
            feedbacks = feedbacks(Q(email=email))
        if url:
            feedbacks = feedbacks(Q(url=url))
        if limit:
            feedbacks = feedbacks[:limit]
        return list(map(lambda x: x.to_dict(), feedbacks))


class FeedbackAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return FeedbackController
