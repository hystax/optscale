import React, { useMemo } from "react";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import FormattedMoney from "components/FormattedMoney";
import ResourceCell from "components/ResourceCell";
import ResourceTypeLabel from "components/ResourceTypeLabel";
import SummaryGrid from "components/SummaryGrid";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import WrapperCard from "components/WrapperCard";
import { SUMMARY_VALUE_COMPONENT_TYPES, SUMMARY_CARD_TYPES, FORMATTED_MONEY_TYPES } from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import { percentXofY } from "utils/math";
import { RESOURCE_ID_COLUMN_CELL_STYLE } from "utils/tables";

const TtlAnalysisReport = ({
  resourcesTracked,
  resourcesOutsideOfTtl,
  totalExpenses,
  expensesOutsideOfTtl,
  resources,
  isLoading = false
}) => {
  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_resource">
            <FormattedMessage id="resource" />
          </TextWithDataTestId>
        ),
        accessorKey: "resource",
        style: RESOURCE_ID_COLUMN_CELL_STYLE,
        cell: ({ row: { original } }) => (
          <ResourceCell
            rowData={{
              resource_name: original.name,
              cloud_resource_id: original.cloud_resource_id,
              resource_id: original.id
            }}
          />
        )
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_type">
            <FormattedMessage id="type" />
          </TextWithDataTestId>
        ),
        accessorKey: "type",
        cell: ({
          row: {
            original: { type, cluster_type_id: clusterTypeId, is_environment: isEnvironment }
          }
        }) => (
          <ResourceTypeLabel
            resourceInfo={{
              resourceType: type,
              clusterTypeId,
              isEnvironment
            }}
          />
        )
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_owner">
            <FormattedMessage id="owner" />
          </TextWithDataTestId>
        ),
        accessorKey: "owner_name"
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_cloud">
            <FormattedMessage id="source" />
          </TextWithDataTestId>
        ),
        accessorKey: "cloud_account_name",
        cell: ({ row: { original } }) =>
          original.cloud_account_id ? (
            <CloudLabel id={original.cloud_account_id} name={original.cloud_account_name} type={original.cloud_type} />
          ) : null
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_hours">
            <FormattedMessage id="hoursOutsideOfTtl" />
          </TextWithDataTestId>
        ),
        accessorKey: "hours_outside_of_ttl"
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_expenses">
            <FormattedMessage id="expensesOutsideOfTtl" />
          </TextWithDataTestId>
        ),
        accessorKey: "expenses_outside_of_ttl",
        cell: ({ cell }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cell.getValue()} />,
        defaultSort: "desc"
      }
    ],
    []
  );

  const tableData = useMemo(
    () =>
      resources.map((resource) => ({
        ...resource,
        resource: `${resource.cloud_resource_id} ${resource.name}`
      })),
    [resources]
  );

  return (
    <Grid container spacing={SPACING_2}>
      <Grid item xs={12}>
        <SummaryGrid
          summaryData={[
            {
              key: "resourcesTracked",
              value: resourcesTracked,
              captionMessageId: "resourcesTracked",
              help: {
                show: true,
                messageId: "resourcesTrackedReportDescription",
                dataTestId: "qmark_resources"
              },
              isLoading,
              dataTestId: "card_recources"
            },
            {
              key: "resourcesOutsideOfTtl",
              type: SUMMARY_CARD_TYPES.EXTENDED,
              value: resourcesOutsideOfTtl,
              captionMessageId: "resourcesOutsideOfTtl",
              relativeValueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedNumber,
              relativeValueComponentProps: {
                value: percentXofY(resourcesOutsideOfTtl, resourcesTracked),
                format: "percentage"
              },
              relativeValueCaptionMessageId: "fromTotalResourcesCount",
              help: {
                show: true,
                messageId: "resourcesOutsideOfTtlReportDescription",
                dataTestId: "qmark_resources_ttl"
              },
              isLoading,
              dataTestId: "card_recources_ttl"
            }
          ]}
        />
      </Grid>
      <Grid item xs={12}>
        <SummaryGrid
          summaryData={[
            {
              key: "totalExpenses",
              valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
              valueComponentProps: {
                value: totalExpenses
              },
              captionMessageId: "totalExpenses",
              help: {
                show: true,
                messageId: "totalExpensesReportDescription",
                dataTestId: "qmark_expenses"
              },
              isLoading,
              dataTestId: "card_expenses"
            },
            {
              key: "expensesOutsideOfTtl",
              type: SUMMARY_CARD_TYPES.EXTENDED,
              valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
              valueComponentProps: {
                value: expensesOutsideOfTtl
              },
              captionMessageId: "expensesOutsideOfTtl",
              relativeValueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedNumber,
              relativeValueComponentProps: {
                value: percentXofY(expensesOutsideOfTtl, totalExpenses),
                format: "percentage"
              },
              relativeValueCaptionMessageId: "fromTotalExpenses",
              help: {
                show: true,
                messageId: "expensesOutsideOfTtlReportDescription",
                dataTestId: "qmark_expenses_ttl"
              },
              isLoading,
              dataTestId: "card_expenses_ttl"
            }
          ]}
        />
      </Grid>
      <Grid item xs={12}>
        <WrapperCard>
          {isLoading ? (
            <TableLoader columnsCounter={columns.length} showHeader />
          ) : (
            <Table
              data={tableData}
              columns={columns}
              localization={{
                emptyMessageId: "noResources"
              }}
              dataTestIds={{
                container: "table_report_data"
              }}
            />
          )}
        </WrapperCard>
      </Grid>
    </Grid>
  );
};

TtlAnalysisReport.propTypes = {
  resourcesTracked: PropTypes.number,
  resourcesOutsideOfTtl: PropTypes.number,
  totalExpenses: PropTypes.number,
  expensesOutsideOfTtl: PropTypes.number,
  resources: PropTypes.array,
  isLoading: PropTypes.bool
};

export default TtlAnalysisReport;
