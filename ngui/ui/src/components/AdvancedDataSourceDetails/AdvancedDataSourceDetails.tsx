import { useMemo } from "react";
import CancelIcon from "@mui/icons-material/Cancel";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import { Grid } from "@mui/material";
import { FormattedMessage } from "react-intl";
import IconStatus from "components/IconStatus";
import KeyValueLabelsList from "components/KeyValueLabelsList";
import SlicedText from "components/SlicedText";
import SubTitle from "components/SubTitle";
import SummaryList from "components/SummaryList";
import Table from "components/Table";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { discoveryStatus, lastTimeLocal, resourceType } from "utils/columns";
import { DISCOVERY_STATUS } from "utils/columns/discoveryStatus";
import { BILLING_IMPORT_STATUS, getBillingImportStatus } from "utils/dataSources";
import { getTimeDistance } from "utils/datetime";

const Discovery = ({ discoveryInfos }) => {
  const columns = useMemo(
    () => [
      resourceType({
        style: {
          minWidth: "150px"
        }
      }),
      lastTimeLocal({
        headerDataTestId: "lbl_last_discovery_at",
        messageId: "lastDiscoveryAt",
        accessorKey: "last_discovery_at",
        style: {
          minWidth: "170px"
        }
      }),
      discoveryStatus()
    ],
    []
  );

  const tableData = useMemo(() => {
    const getStatus = (lastDiscoveryAt, lastErrorAt) => {
      if (lastDiscoveryAt === 0 && lastErrorAt === 0) {
        return DISCOVERY_STATUS.UNKNOWN;
      }

      return lastDiscoveryAt > lastErrorAt ? DISCOVERY_STATUS.SUCCESS : DISCOVERY_STATUS.ERROR;
    };

    return discoveryInfos.map((info) => ({
      ...info,
      status: getStatus(info.last_discovery_at, info.last_error_at)
    }));
  }, [discoveryInfos]);

  return (
    <>
      <SubTitle>
        <FormattedMessage id="discovery" />
      </SubTitle>
      <Table data={tableData} columns={columns} />
    </>
  );
};

const Status = ({ timestamp, attemptTimestamp, error }) => {
  const status = getBillingImportStatus({
    timestamp,
    attemptTimestamp,
    error
  });

  if (status === BILLING_IMPORT_STATUS.SUCCESS) {
    return <IconStatus icon={CheckCircleIcon} color="success" labelMessageId="completed" />;
  }
  if (status === BILLING_IMPORT_STATUS.ERROR) {
    return <IconStatus icon={CancelIcon} color="error" labelMessageId="failed" />;
  }

  return "-";
};

const AdvancedDataSourceDetails = ({
  lastImportAttemptAt,
  lastImportAt,
  lastImportAttemptError,
  lastMetricsRetrieval,
  lastMetricsRetrievalAttempt,
  lastGettingMetricAttemptError,
  discoveryInfos
}) => (
  <>
    <Grid container spacing={4}>
      <Grid item xs={12} sm={4}>
        <SummaryList
          titleMessage={<FormattedMessage id="billingImport" />}
          items={
            <KeyValueLabelsList
              items={[
                {
                  itemKey: "lastImportAt",
                  messageId: "lastBillingReportProcessed",
                  value: (
                    <FormattedMessage
                      id={!lastImportAt ? "never" : "valueAgo"}
                      values={{
                        value: lastImportAt ? getTimeDistance(lastImportAt) : null
                      }}
                    />
                  ),
                  dataTestIds: { key: "p_last_billing_report_processed", value: "value_last_billing_report_processed" }
                },
                {
                  itemKey: "lastImportAttemptAt",
                  messageId: "lastBillingReportAttempt",
                  value: (
                    <FormattedMessage
                      id={!lastImportAttemptAt ? "never" : "valueAgo"}
                      values={{
                        value: lastImportAttemptAt ? getTimeDistance(lastImportAttemptAt) : null
                      }}
                    />
                  ),
                  dataTestIds: { key: "p_last_billing_report_attempt", value: "value_last_billing_report_attempt" }
                },
                {
                  itemKey: "status",
                  messageId: "status",
                  value: (
                    <Status timestamp={lastImportAt} attemptTimestamp={lastImportAttemptAt} error={lastImportAttemptError} />
                  ),
                  dataTestIds: { key: "p_last_billing_report_status", value: "value_last_billing_report_status" },
                  typographyProps: {
                    noWrap: false,
                    sx: {
                      wordBreak: "break-all"
                    }
                  }
                },
                {
                  itemKey: "reason",
                  messageId: "reason",
                  value: <SlicedText limit={50} text={lastImportAttemptError} />,
                  dataTestIds: { key: "p_last_billing_report_reason", value: "value_last_billing_report_reason" },
                  show: lastImportAttemptError && lastImportAt < lastImportAttemptAt
                }
              ]}
            />
          }
        />
      </Grid>
      <Grid item xs={12} sm={4}>
        <SummaryList
          titleMessage={<FormattedMessage id="monitoringMetricsImport" />}
          items={
            <KeyValueLabelsList
              items={[
                {
                  itemKey: "lastMetricsRetrieval",
                  messageId: "lastMetricsRetrieval",
                  value: (
                    <FormattedMessage
                      id={!lastMetricsRetrieval ? "never" : "valueAgo"}
                      values={{
                        value: lastMetricsRetrieval ? getTimeDistance(lastMetricsRetrieval) : null
                      }}
                    />
                  ),
                  dataTestIds: { key: "p_last_getting_metrics_at", value: "value_last_getting_metrics_at" }
                },
                {
                  itemKey: "lastMetricsRetrievalAttempt",
                  messageId: "lastMetricsRetrievalAttempt",
                  value: (
                    <FormattedMessage
                      id={!lastMetricsRetrievalAttempt ? "never" : "valueAgo"}
                      values={{
                        value: lastMetricsRetrievalAttempt ? getTimeDistance(lastMetricsRetrievalAttempt) : null
                      }}
                    />
                  ),
                  dataTestIds: { key: "p_last_getting_metrics_attempt_at", value: "value_last_getting_metrics_attempt_at" }
                },
                {
                  itemKey: "status",
                  messageId: "status",
                  value: (
                    <Status
                      timestamp={lastMetricsRetrieval}
                      attemptTimestamp={lastMetricsRetrievalAttempt}
                      error={lastGettingMetricAttemptError}
                    />
                  ),
                  dataTestIds: { key: "p_last_metrics_report_status", value: "value_last_metrics_report_status" },
                  typographyProps: {
                    noWrap: false,
                    sx: {
                      wordBreak: "break-all"
                    }
                  }
                },
                {
                  itemKey: "reason",
                  messageId: "reason",
                  value: <SlicedText limit={50} text={lastGettingMetricAttemptError} />,
                  dataTestIds: { key: "p_last_metrics_report_reason", value: "value_last_metrics_report_reason" },
                  show: lastGettingMetricAttemptError && lastMetricsRetrieval < lastMetricsRetrievalAttempt
                }
              ]}
            />
          }
        />
      </Grid>
      {!isEmptyArray(discoveryInfos) && (
        <Grid item xs={12}>
          <Discovery discoveryInfos={discoveryInfos} />
        </Grid>
      )}
    </Grid>
  </>
);

export default AdvancedDataSourceDetails;
