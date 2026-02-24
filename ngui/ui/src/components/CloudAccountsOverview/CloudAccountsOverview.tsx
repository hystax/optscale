import { Stack } from "@mui/material";
import ActionBar from "components/ActionBar";
import CloudAccountsTable from "components/CloudAccountsTable";
import CloudExpensesChart from "components/CloudExpensesChart";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import PageContentWrapper from "components/PageContentWrapper";
import SummaryGrid from "components/SummaryGrid";
import { useIsAllowed } from "hooks/useAllowedActions";
import { getSumByNestedObjectKey, isEmptyArray } from "utils/arrays";
import { SUMMARY_VALUE_COMPONENT_TYPES, SUMMARY_CARD_TYPES, AWS_CNR } from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import { getPercentageChangeModule, round } from "utils/math";

type SummaryProps = {
  totalExpenses: number;
  totalForecast: number;
  lastMonthCost: number;
  isLoading?: boolean;
};

const actionBarDefinition = {
  title: {
    messageId: "dataSourcesTitle",
  },
};

const Summary = ({ totalExpenses, totalForecast, lastMonthCost, isLoading = false }: SummaryProps) => {
  const getSummaryData = () =>
    lastMonthCost
      ? [
          {
            key: "totalExpensesMonthToDate",
            type: SUMMARY_CARD_TYPES.EXTENDED,
            valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
            valueComponentProps: {
              value: totalExpenses,
            },
            captionMessageId: "totalExpensesMonthToDate",
            relativeValueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedNumber,
            relativeValueComponentProps: {
              value: getPercentageChangeModule(totalExpenses, lastMonthCost) / 100,
              format: "percentage",
            },
            relativeValueCaptionMessageId:
              totalExpenses > lastMonthCost ? "moreThanForPreviousMonth" : "lessThanForPreviousMonth",
            dataTestIds: {
              cardTestId: "card_total_exp",
            },
            color: totalExpenses > lastMonthCost ? "error" : "success",
            isLoading,
          },
          {
            key: "forecastForThisMonth",
            type: SUMMARY_CARD_TYPES.EXTENDED,
            valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
            valueComponentProps: {
              value: totalForecast,
            },
            captionMessageId: "forecastForThisMonth",
            relativeValueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedNumber,
            relativeValueComponentProps: {
              value: getPercentageChangeModule(totalForecast, lastMonthCost) / 100,
              format: "percentage",
            },
            relativeValueCaptionMessageId:
              totalForecast > lastMonthCost ? "moreThanForPreviousMonth" : "lessThanForPreviousMonth",
            dataTestIds: {
              cardTestId: "card_forecast",
            },
            color: totalForecast > lastMonthCost ? "error" : "success",
            isLoading,
          },
        ]
      : [
          {
            key: "totalExpensesMonthToDate",
            valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
            valueComponentProps: {
              value: totalExpenses,
            },
            captionMessageId: "totalExpensesMonthToDate",
            dataTestIds: {
              cardTestId: "card_total_exp",
            },
            isLoading,
          },
          {
            key: "forecastForThisMonth",
            valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
            valueComponentProps: {
              value: totalForecast,
            },
            captionMessageId: "forecastForThisMonth",
            dataTestIds: {
              cardTestId: "card_forecast",
            },
            isLoading,
          },
        ];

  return <SummaryGrid summaryData={getSummaryData()} />;
};

const AwsLinkedAccountsWarning = () => {
  const isManageCloudCredentialsAllowed = useIsAllowed({ requiredActions: ["MANAGE_CLOUD_CREDENTIALS"] });

  return (
    <InlineSeverityAlert
      messageId="onlyAwsLinkedAccountsConnectedWarning"
      messageValues={{
        hasPermissionsToConnectDataSources: isManageCloudCredentialsAllowed,
      }}
      severity="warning"
    />
  );
};

const CloudAccountsOverview = ({ cloudAccounts, organizationLimit, isLoading = false }) => {
  const totalExpenses = round(getSumByNestedObjectKey(cloudAccounts, "details", "cost"), 2);
  const totalForecast = round(getSumByNestedObjectKey(cloudAccounts, "details", "forecast"), 2);
  const lastMonthCost = round(getSumByNestedObjectKey(cloudAccounts, "details", "last_month_cost"), 2);

  const awsDataSources = cloudAccounts.filter(({ type }) => type === AWS_CNR);
  const onlyAwsLinkedAccountsConnected = !isEmptyArray(awsDataSources) && awsDataSources.every(({ config }) => config.linked);

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Stack spacing={SPACING_2}>
          <div>
            <Summary
              totalExpenses={totalExpenses}
              totalForecast={totalForecast}
              lastMonthCost={lastMonthCost}
              isLoading={isLoading}
            />
          </div>
          <div>
            {(organizationLimit === 0 && totalForecast === 0) || totalExpenses === 0 ? null : (
              <CloudExpensesChart
                cloudAccounts={cloudAccounts}
                limit={organizationLimit}
                forecast={totalForecast}
                isLoading={isLoading}
              />
            )}
          </div>
          {!isLoading && onlyAwsLinkedAccountsConnected && (
            <div>
              <AwsLinkedAccountsWarning />
            </div>
          )}
          <div>
            <CloudAccountsTable cloudAccounts={cloudAccounts} isLoading={isLoading} />
          </div>
        </Stack>
      </PageContentWrapper>
    </>
  );
};

export default CloudAccountsOverview;
