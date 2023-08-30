import datetime
import os
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from tools.optscale_exceptions.http_exc import OptHTTPError
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.controllers.pool_expenses_export import PoolExpensesExportAsyncController
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.utils import run_task


class PoolExpensesExportDataAsyncItemHandler(BaseAsyncItemHandler,
                                             BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return PoolExpensesExportAsyncController

    def _convert_dates(self, **dates):
        if (dates.get('start_date') is None and
                dates.get('end_date') is not None):
            raise WrongArgumentsException(Err.OE0216, ['start_date'])
        for date_type, v in dates.items():
            if not isinstance(v, str) and v is not None:
                raise WrongArgumentsException(Err.OE0468, [date_type])
            if v is not None:
                try:
                    if date_type == 'end_date':
                        dates[date_type] = int(self._str_to_date(v).replace(
                            hour=23, minute=59, second=59).timestamp())
                    elif date_type == 'start_date':
                            dates[date_type] = int(self._str_to_date(v).timestamp())
                except ValueError:
                    raise WrongArgumentsException(Err.OE0468, [date_type])
        return dates

    @staticmethod
    def _str_to_date(date):
        return datetime.datetime.strptime(date, '%Y%m%d').replace(
            hour=0, minute=0, second=0)

    def prepare(self):
        self.set_content_type()

    async def get(self, export_id, **kwargs):
        """
        ---
        description: |
            Returns pool expenses data for specified dates in CSV format.
            Required permission: No
        tags: [expense_exports]
        summary: Get pool expenses data in CSV format
        parameters:
        -   name: export_id
            in: path
            description: id of pool expense export
            required: true
            type: string
        -   name: start_date
            in: query
            description: start date (string in format YYYYMMDD)
            required: false
            type: string
        -   name: end_date
            in: query
            description: end date (string in format YYYYMMDD)
            required: false
            type: string
        responses:
            200:
                description: Expenses data in CSV format
            400:
                description: |
                    Wrong arguments
                    - OE0216: start_date is not provided
                    - OE0446: end_date should be greater than start_date
                    - OE0468: start_date/end_date should be a date in format YYYYMMDD
            404:
                description: |
                    Not found:
                    - OE0002: Export/Pool not found
        """
        start_date = self.get_arg('start_date', str, None)
        end_date = self.get_arg('end_date', str, None)
        try:
            converted_dates = self._convert_dates(
                start_date=start_date, end_date=end_date)
            if start_date and end_date and start_date > end_date:
                raise WrongArgumentsException(Err.OE0446, ['end_date', 'start_date'])
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)
        export = await run_task(self.controller.get_export, export_id)
        exp = await run_task(self.controller.get_expenses_data, export_id,
                             converted_dates['start_date'],
                             converted_dates['end_date'])
        result = ''
        if start_date is None and end_date is None:
            result_list = [exp['expenses']['total']]
        else:
            exp_list = list(exp['expenses']['breakdown'].items())
            exp_list.sort(key=lambda x: int(x[0]))
            result_list = []
            for _, exp_value in exp_list:
                result_list.append(sum(x['expense'] for x in exp_value))
        for i in result_list:
            result += str(i) + os.linesep
        result = result.rsplit(os.linesep, 1)[0]
        if not result:
            result = str(0.0)
        filename = export.id
        if start_date:
            filename = '{0}_{1}'.format(filename, start_date)
        if end_date:
            filename = '{0}_{1}'.format(filename, end_date)
        filename = '{0}{1}'.format(filename, '.csv')
        self.set_header('Content-Type', 'text/csv')
        self.set_header('Content-Disposition',
                        'attachment; filename="{}"'.format(filename))
        self.write(result)
