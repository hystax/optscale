import csv
import io

from tools.optscale_exceptions.http_exc import OptHTTPError
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.controllers.pool import PoolAsyncController
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.handlers.v2.pools import validate_dates
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.utils import (
    run_task, object_to_xlsx)


def _csv_safe(value):
    _formula_prefixes = ('=', '+', '-', '@', '\t', '\r')
    if isinstance(value, str) and value.startswith(_formula_prefixes):
        return "'" + value
    return value


class PoolExpensesReportAsyncHandler(BaseAsyncItemHandler,
                                     BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return PoolAsyncController

    async def prepare(self):
        await super().prepare()

    async def get(self, organization_id, **kwargs):
        """
        ---
        description: |
            Returns pool expenses report for the organization in CSV or XLSX.
            Required permission: INFO_ORGANIZATION
        tags: [pool_expenses_report]
        summary: Get pool expenses report
        parameters:
        -   name: organization_id
            in: path
            description: Organization ID
            required: true
            type: string
        -   name: start_date
            in: query
            description: Start of the reporting period (UTC timestamp, inclusive)
            required: true
            type: integer
        -   name: end_date
            in: query
            description: End of the reporting period (UTC timestamp, inclusive)
            required: true
            type: integer
        -   name: format
            in: query
            description: Export format
            required: true
            type: string
            enum: [csv, xlsx]
        produces:
        - text/csv
        - application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
        responses:
            200:
                description: |
                    Pool expenses report file.
                    For CSV: text/csv with UTF-8 encoding.
                    For XLSX: spreadsheet with numeric expense cells.
                    Attribution uses the resource's current Pool assignment.
                headers:
                    Content-Disposition:
                        type: string
                        description: >
                            attachment;
                            filename="pool_expenses_report_{organization_id}.{format}"
                    Content-Type:
                        type: string
                        description: >
                            text/csv; charset="utf-8"  (format=csv)
                            or application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
                            (format=xlsx)
                schema:
                    type: object
                    description: >
                        Each row represents one pool in DFS order
                        (root first, children sorted alphabetically).
                        Columns present in every row:
                    properties:
                        Period start:
                            type: string
                            description: Start date of the reporting period (YYYY-MM-DD)
                            example: "2026-06-01"
                        Period end:
                            type: string
                            description: End date of the reporting period (YYYY-MM-DD)
                            example: "2026-06-30"
                        Currency:
                            type: string
                            description: Organization currency code
                            example: USD
                        Pool ID:
                            type: string
                            description: >
                                Pool UUID, or "(not set)" for unassigned
                                resources not belonging to any pool
                        Pool purpose:
                            type: string
                            description: Pool purpose (e.g. business_unit, team, project)
                        Default owner:
                            type: string
                            description: Full name of the pool's default owner employee
                        Level 1...Level N:
                            type: string
                            description: >
                                Breadcrumb path from root to the current pool.
                                Level 1 is always the root pool name.
                                Level N is the pool name itself.
                                Columns deeper than the pool's own level are empty.
                                N equals the maximum hierarchy depth across all pools
                                in the organization (dynamic per request).
                        Direct expense:
                            type: number
                            description: >
                                Cost of resources assigned directly to this pool,
                                excluding descendants
                        Subtree expense:
                            type: number
                            description: >
                                Cost of resources assigned to this pool and all
                                its descendants (roll-up)
            400:
                description: |
                    Wrong arguments:
                    - OE0216: argument is not provided
                    - OE0224: argument is out of range
                    - OE0446: end_date should be greater than start_date
                    - OE0473: format is not allowed
                    - OE0574: date range must not exceed 3 months
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', organization_id)

        start_date = self.get_arg('start_date', int, None)
        end_date = self.get_arg('end_date', int, None)
        exp_format = self.get_arg('format', str, None)
        validate_dates(start_date, end_date, required=True)

        if exp_format is None:
            raise OptHTTPError(400, Err.OE0216, ['format'])
        if exp_format not in ('csv', 'xlsx'):
            raise OptHTTPError(400, Err.OE0473, [exp_format])

        rows = await run_task(
            self.controller.get_pool_expenses_report,
            organization_id, start_date, end_date)

        filename = 'pool_expenses_report_%s' % organization_id

        if exp_format == 'csv':
            self.set_header('Content-Type', 'text/csv; charset="utf-8"')
            self.set_header('Content-Disposition',
                            'attachment; filename="%s.csv"' % filename)
            if rows:
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(
                    {k: _csv_safe(v) for k, v in row.items()}
                    for row in rows)
                self.write(output.getvalue())
            else:
                self.write('')
        else:
            self.set_content_type(
                'application/vnd.openxmlformats-officedocument.'
                'spreadsheetml.sheet')
            self.set_header('Content-Disposition',
                            'attachment; filename="%s.xlsx"' % filename)
            fields = list(rows[0].keys()) if rows else None
            self.write(object_to_xlsx(rows, fields=fields))

    def delete(self, *args, **kwargs):
        self.raise405()

    def patch(self, *args, **kwargs):
        self.raise405()
