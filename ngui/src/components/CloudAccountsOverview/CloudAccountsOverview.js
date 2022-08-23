import React from "react";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import ActionBar from "components/ActionBar";
import CloudAccountsTable from "components/CloudAccountsTable";
import CloudExpensesChart from "components/CloudExpensesChart";
import PageContentWrapper from "components/PageContentWrapper";
import SummaryGrid from "components/SummaryGrid";
import WrapperCard from "components/WrapperCard";
import { getSumByNestedObjectKey } from "utils/arrays";
import { SUMMARY_VALUE_COMPONENT_TYPES, SUMMARY_CARD_TYPES } from "utils/constants";
import { SPACING_2, SPACING_3 } from "utils/layouts";
import { getPercentageChangeModule } from "utils/math";

const actionBarDefinition = {
  title: {
    messageId: "dataSourcesTitle"
  }
};

const CloudAccountsOverview = ({ isLoading, cloudAccounts, organizationLimit }) => {
  const totalExpenses = getSumByNestedObjectKey(cloudAccounts, "details", "cost");
  const totalForecast = getSumByNestedObjectKey(cloudAccounts, "details", "forecast");
  const lastMonthCost = getSumByNestedObjectKey(cloudAccounts, "details", "last_month_cost");

  const getSummaryData = () =>
    lastMonthCost
      ? [
          {
            key: "totalExpensesMonthToDate",
            type: SUMMARY_CARD_TYPES.EXTENDED,
            valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
            valueComponentProps: {
              value: totalExpenses
            },
            captionMessageId: "totalExpensesMonthToDate",
            relativeValueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedNumber,
            relativeValueComponentProps: {
              value: getPercentageChangeModule(totalExpenses, lastMonthCost) / 100,
              format: "percentage"
            },
            relativeValueCaptionMessageId:
              totalExpenses > lastMonthCost ? "moreThanForPreviousMonth" : "lessThanForPreviousMonth",
            dataTestIds: {
              cardTestId: "card_total_exp"
            },
            color: totalExpenses > lastMonthCost ? "error" : "success",
            isLoading
          },
          {
            key: "forecastForThisMonth",
            type: SUMMARY_CARD_TYPES.EXTENDED,
            valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
            valueComponentProps: {
              value: totalForecast
            },
            captionMessageId: "forecastForThisMonth",
            relativeValueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedNumber,
            relativeValueComponentProps: {
              value: getPercentageChangeModule(totalForecast, lastMonthCost) / 100,
              format: "percentage"
            },
            relativeValueCaptionMessageId:
              totalForecast > lastMonthCost ? "moreThanForPreviousMonth" : "lessThanForPreviousMonth",
            dataTestIds: {
              cardTestId: "card_forecast"
            },
            color: totalForecast > lastMonthCost ? "error" : "success",
            isLoading
          }
        ]
      : [
          {
            key: "totalExpensesMonthToDate",
            valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
            valueComponentProps: {
              value: totalExpenses
            },
            captionMessageId: "totalExpensesMonthToDate",
            dataTestIds: {
              cardTestId: "card_total_exp"
            },
            isLoading
          },
          {
            key: "forecastForThisMonth",
            valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
            valueComponentProps: {
              value: totalForecast
            },
            captionMessageId: "forecastForThisMonth",
            dataTestIds: {
              cardTestId: "card_forecast"
            },
            isLoading
          }
        ];

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Grid container justifyContent="flex-start" alignItems="center" spacing={SPACING_2}>
          <Grid item xs={12}>
            <SummaryGrid summaryData={getSummaryData()} />
          </Grid>
          <Grid item xs={12}>
            <WrapperCard dataTestIds={{ wrapper: "div_sum", title: "lbl_sum" }} title={<FormattedMessage id="summary" />}>
              <Grid container spacing={SPACING_3}>
                {(organizationLimit === 0 && totalForecast === 0) || totalExpenses === 0 ? null : (
                  <Grid item xs={12}>
                    <CloudExpensesChart
                      cloudAccounts={cloudAccounts}
                      limit={organizationLimit}
                      forecast={totalForecast}
                      isLoading={isLoading}
                    />
                  </Grid>
                )}
                <Grid item xs={12}>
                  <CloudAccountsTable cloudAccounts={cloudAccounts} isLoading={isLoading} />
                </Grid>
              </Grid>
            </WrapperCard>
          </Grid>
        </Grid>
      </PageContentWrapper>
    </>
  );
};

CloudAccountsOverview.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  cloudAccounts: PropTypes.array.isRequired,
  organizationLimit: PropTypes.number.isRequired
};

export default CloudAccountsOverview;
