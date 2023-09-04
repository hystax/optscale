import logging
import os
from influxdb import InfluxDBClient


LOG = logging.getLogger(__name__)
INFLUXDB_HOST = os.environ.get("HX_INFLUXDB_HOST", "influxdb")
INFLUXDB_PORT = int(os.environ.get("HX_INFLUXDB_PORT", 80))
DAYS_TO_STORE = int(os.environ.get("HX_DAYS_TO_STORE", 90))
DATABASE = 'metrics'


class CleanInfluxDB:
    def __init__(self):
        self.client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, database=DATABASE)

    def clean(self):
        series_result_list = self.client.query('show series;').items()
        if not series_result_list:
            LOG.info('Nothing to clean, series is empty')
            return
        measurements = [m['key'] for m in series_result_list[0][1]]
        measurements_to_clean = [m.split(',')[0] for m in measurements]
        for measurement in measurements_to_clean:
            LOG.info('Cleaning %s measurement' % measurement)
            result = self.client.query('DELETE FROM \"%s\" WHERE time < now() - %dd;' %
                                       (measurement, DAYS_TO_STORE))
            LOG.info('Result of clean: %s' % result)
        LOG.info('Done')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cleaner = CleanInfluxDB()
    cleaner.clean()
