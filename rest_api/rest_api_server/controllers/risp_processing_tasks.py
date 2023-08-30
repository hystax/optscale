from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.traffic_processing_task import TrafficProcessingTaskController
from rest_api.rest_api_server.models.models import RispProcessingTask


class RispProcessingTaskController(TrafficProcessingTaskController):
    def _get_model_type(self):
        return RispProcessingTask

    @staticmethod
    def task_type():
        return 'Risp'


class RispProcessingTaskAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return RispProcessingTaskController
