import React, { useMemo } from "react";
import { Typography } from "@mui/material";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";
import { FormattedMessage, FormattedNumber } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CaptionedCell from "components/CaptionedCell";
import CloudLabel from "components/CloudLabel";
import FormattedDigitalUnit, { IEC_UNITS } from "components/FormattedDigitalUnit";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import Tooltip from "components/Tooltip";
import { getResourcesExpensesUrl } from "urls";
import resourcesMeter from "utils/columns/resourcesMeter";
import resourcesUsed from "utils/columns/resourcesUsed";
import { CLOUD_ACCOUNT_ID_FILTER, K8S_NAMESPACE_FILTER } from "utils/constants";
import { getCurrentMonthRange } from "utils/datetime";
import ApproximatelyZero from "../ApproximatelyZero";

const MAXIMUM_FRACTION_DIGITS = 2;
const APPROXIMATE_ZERO_THRESHOLD = 0.01;

const K8sRightsizingTable = ({ namespaces, isLoading = false }) => {
  const { today, startOfMonth } = getCurrentMonthRange(true);
  const memoizedNamespaces = useMemo(
    () =>
      namespaces.map((obj) => ({
        ...obj,
        location: [obj.cloud_account_name, obj.namespace].join()
      })),
    [namespaces]
  );

  const columns = useMemo(
    () => [
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_application">
            <FormattedMessage id="application" />
          </TextWithDataTestId>
        ),
        accessor: "name",
        defaultSort: "asc",
        style: {
          maxWidth: 200
        }
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_location">
            <FormattedMessage id="location" />
          </TextWithDataTestId>
        ),
        accessor: "location",
        defaultSort: "asc",
        Cell: ({
          row: {
            original: { application, namespace, cloud_account_id: cloudAccountId, cloud_account_name: cloudAccountName }
          }
        }) => {
          const link = (
            <Tooltip title={<FormattedMessage id={"showResources"} />}>
              <Link
                data-test-id={`dt_show_resources_${cloudAccountId}`}
                color="primary"
                to={getResourcesExpensesUrl({
                  [CLOUD_ACCOUNT_ID_FILTER]: cloudAccountId,
                  [K8S_NAMESPACE_FILTER]: namespace,
                  sStartDate: startOfMonth,
                  sEndDate: today
                })}
                component={RouterLink}
              >
                {namespace}
              </Link>
            </Tooltip>
          );
          const namespaceCaption = {
            key: `${application}_${cloudAccountId}`,
            node: <Typography variant="caption">{link}</Typography>
          };
          return (
            <CaptionedCell caption={namespaceCaption}>
              <CloudLabel
                dataTestId={`resource_location_${application}`}
                id={cloudAccountId}
                name={cloudAccountName}
                type={"kubernetes_cnr"}
              />
            </CaptionedCell>
          );
        }
      },
      resourcesMeter({
        id: "cpu_utilization",
        headerDataTestId: "lbl_cpu_utilization",
        messageId: "cpuUtilization",
        questionMarkMessageId: "cpuUtilizationTooltip",
        questionMarkUsedMessageId: "cpuUtilizationTooltip.used",
        questionMarkRequestsMessageId: "cpuUtilizationTooltip.requests",
        questionMarkLimitMessageId: "cpuUtilizationTooltip.limit",
        questionMarkDataTestId: "qmark_cpu_utilization",
        averageUsedAccessor: "average_pod_cpu_used",
        requestsAccessor: "pod_cpu_requests",
        provisionAccessor: "pod_cpu_provision",
        limitExceededMessageId: "cpuUtilizationProgressbarTooltip.limitExceeded",
        limitNotSetMessageId: "cpuUtilizationProgressbarTooltip.limitsNotSet",
        mismatchedLimitMessageId: "cpuUtilizationProgressbarTooltip.mismatchedLimit",
        valueFormatterFn: (value) =>
          value < APPROXIMATE_ZERO_THRESHOLD ? (
            <ApproximatelyZero />
          ) : (
            <FormattedNumber value={value} maximumFractionDigits={MAXIMUM_FRACTION_DIGITS} />
          )
      }),
      resourcesUsed({
        headerDataTestId: "lbl_total_pod_cpu_hours",
        messageId: "cpuUsed",
        questionMarkMessageId: "cpuUsedTooltip",
        accessor: "total_pod_cpu_hours",
        totalAccessor: "total_pod_cpu_hours",
        totalRequestsAccessor: "total_pod_cpu_requests"
      }),
      resourcesMeter({
        id: "memory_utilization",
        headerDataTestId: "lbl_memory_utilization",
        messageId: "memoryUtilization",
        questionMarkMessageId: "memoryUtilizationTooltip",
        questionMarkUsedMessageId: "memoryUtilizationTooltip.used",
        questionMarkRequestsMessageId: "memoryUtilizationTooltip.requests",
        questionMarkLimitMessageId: "memoryUtilizationTooltip.limit",
        questionMarkDataTestId: "qmark_memory_utilization",
        averageUsedAccessor: "average_pod_memory_used",
        requestsAccessor: "pod_memory_requests",
        provisionAccessor: "pod_memory_provision",
        limitExceededMessageId: "memoryUtilizationProgressbarTooltip.limitExceeded",
        limitNotSetMessageId: "memoryUtilizationProgressbarTooltip.limitsNotSet",
        mismatchedLimitMessageId: "memoryUtilizationProgressbarTooltip.mismatchedLimit",
        valueFormatterFn: (value) => (
          <FormattedDigitalUnit value={value} baseUnit={IEC_UNITS.BYTE} maximumFractionDigits={MAXIMUM_FRACTION_DIGITS} />
        )
      }),
      resourcesUsed({
        headerDataTestId: "lbl_total_pod_memory_gb",
        messageId: "memoryHours",
        questionMarkMessageId: "totalPodMemoryUsedTooltip",
        accessor: "total_pod_memory_gb",
        totalAccessor: "total_pod_memory_gb",
        totalRequestsAccessor: "total_pod_memory_requests_gb"
      })
    ],
    [startOfMonth, today]
  );

  return isLoading ? (
    <TableLoader columnsCounter={columns.length} showHeader />
  ) : (
    <>
      <Table
        data={memoizedNamespaces}
        columns={columns}
        withSearch
        dataTestIds={{
          searchInput: "input_search"
        }}
        localization={{ emptyMessageId: "noApplications" }}
      />
    </>
  );
};

K8sRightsizingTable.propTypes = {
  namespaces: PropTypes.array.isRequired,
  isLoading: PropTypes.bool
};

export default K8sRightsizingTable;
