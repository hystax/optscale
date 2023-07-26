import React from "react";
import BusinessIcon from "@mui/icons-material/Business";
import CloudIcon from "@mui/icons-material/Cloud";
import PeopleIcon from "@mui/icons-material/People";
import PictureAsPdfIcon from "@mui/icons-material/PictureAsPdf";
import PublicIcon from "@mui/icons-material/Public";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import ActionBar from "components/ActionBar";
import BarChartLoader from "components/BarChartLoader";
import ButtonSwitch from "components/ButtonSwitch";
import { getBasicRangesSet } from "components/DateRangePicker/defaults";
import ExpensesBreakdownBarChart from "components/ExpensesBreakdown/BarChart";
import ExpensesBreakdownByPeriodWidget from "components/ExpensesBreakdown/BreakdownByPeriodWidget";
import ExpensesBreakdownSummaryCards from "components/ExpensesBreakdown/SummaryCards";
import PageContentWrapper from "components/PageContentWrapper";
import SubTitle from "components/SubTitle";
import RangePickerFormContainer from "containers/RangePickerFormContainer";
import { useBreakdownData } from "hooks/useBreakdownData";
import { getResourcesExpensesUrl, EXPENSES_BY_CLOUD, EXPENSES_BY_POOL, EXPENSES_BY_OWNER, EXPENSES_MAP } from "urls";
import { PDF_ELEMENTS } from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import { createPdf } from "utils/pdf";

const breakdownByButtons = [
  { messageId: "source", link: EXPENSES_BY_CLOUD, icon: <CloudIcon /> },
  { messageId: "pool", link: EXPENSES_BY_POOL, icon: <BusinessIcon /> },
  { messageId: "owner", link: EXPENSES_BY_OWNER, icon: <PeopleIcon /> },
  { messageId: "geography", link: EXPENSES_MAP, icon: <PublicIcon /> }
];

const CostExplorer = ({
  total,
  breakdown,
  previousTotal,
  organizationName,
  isLoading,
  onApply,
  startDateTimestamp,
  endDateTimestamp,
  isInScopeOfPageMockup = false
}) => {
  const navigate = useNavigate();

  const breakdownData = useBreakdownData(breakdown);

  const actionBarData = {
    title: {
      text: (
        <FormattedMessage
          id="expensesOf"
          values={{
            name: organizationName
          }}
        />
      ),
      isLoading
    },
    items: [
      {
        key: "costExplorerPdfDownload",
        icon: <PictureAsPdfIcon fontSize="small" />,
        messageId: "download",
        type: "button",
        isLoading,
        action: () => {
          createPdf([
            { type: PDF_ELEMENTS.markup.initPortrait }, // always first

            {
              type: PDF_ELEMENTS.basics.fileName,
              value: "%orgName%_expenses_breakdown_%dateRange%",
              parameters: {
                orgName: {
                  data: organizationName,
                  type: "string"
                },
                dateRange: {
                  data: PDF_ELEMENTS.costExplorer.dates,
                  type: "object"
                }
              }
            },

            { type: PDF_ELEMENTS.markup.logo },

            { type: PDF_ELEMENTS.basics.H1, value: "expensesOf", parameters: { data: { name: organizationName } } },

            { id: PDF_ELEMENTS.costExplorer.dates }, // find component on page with that id and call its pdf render
            { id: PDF_ELEMENTS.costExplorer.expensesSummary }, // another component
            { id: PDF_ELEMENTS.costExplorer.previousExpensesSummary },

            { id: PDF_ELEMENTS.costExplorer.periodWidgetTitle },
            { type: PDF_ELEMENTS.markup.spacer },
            { id: PDF_ELEMENTS.costExplorer.barChart },

            { type: PDF_ELEMENTS.markup.footer }
          ]);
        }
      }
    ]
  };

  const renderBarChart = (periodType) => {
    if (isLoading) {
      return (
        <Grid item xs={12}>
          <BarChartLoader />
        </Grid>
      );
    }
    const isBreakdownDataEmpty = Object.values(breakdownData.daily).every((dailyData) =>
      dailyData.every((d) => d.expense === 0)
    );
    if (isBreakdownDataEmpty) {
      return null;
    }
    return (
      <Grid item xs={12}>
        <ExpensesBreakdownBarChart
          periodType={periodType}
          breakdownData={breakdownData}
          isLoading={isLoading}
          pdfId={PDF_ELEMENTS.costExplorer.barChart}
          onClick={
            isInScopeOfPageMockup
              ? undefined
              : (bandDetails) => {
                  navigate(
                    getResourcesExpensesUrl({
                      sStartDate: bandDetails.startDate,
                      sEndDate: bandDetails.endDate
                    })
                  );
                }
          }
        />
      </Grid>
    );
  };

  return (
    <>
      <ActionBar data={actionBarData} />
      <PageContentWrapper>
        <Grid container direction="row" justifyContent="space-between" spacing={SPACING_2}>
          <Grid item>
            <ExpensesBreakdownSummaryCards
              total={total}
              previousTotal={previousTotal}
              isLoading={isLoading}
              pdfIds={{
                totalExpensesForSelectedPeriod: PDF_ELEMENTS.costExplorer.expensesSummary,
                totalExpensesForPreviousPeriod: PDF_ELEMENTS.costExplorer.previousExpensesSummary
              }}
            />
          </Grid>
          <Grid item>
            <RangePickerFormContainer
              onApply={onApply}
              initialStartDateValue={startDateTimestamp}
              initialEndDateValue={endDateTimestamp}
              pdfId={PDF_ELEMENTS.costExplorer.dates}
              rangeType="expenses"
              definedRanges={getBasicRangesSet()}
            />
          </Grid>
          <Grid item xs={12}>
            <ExpensesBreakdownByPeriodWidget
              render={(periodType) => (
                <Grid container spacing={SPACING_2}>
                  {renderBarChart(periodType)}
                  <Grid item xs={12}>
                    <SubTitle align="center">
                      <FormattedMessage id="seeExpensesBreakdownBy" />
                    </SubTitle>
                    <ButtonSwitch buttons={breakdownByButtons} />
                  </Grid>
                </Grid>
              )}
            />
          </Grid>
        </Grid>
      </PageContentWrapper>
    </>
  );
};

CostExplorer.propTypes = {
  total: PropTypes.node.isRequired,
  previousTotal: PropTypes.node.isRequired,
  breakdown: PropTypes.object.isRequired,
  organizationName: PropTypes.string,
  isLoading: PropTypes.bool,
  onApply: PropTypes.func.isRequired,
  startDateTimestamp: PropTypes.number,
  endDateTimestamp: PropTypes.number,
  isInScopeOfPageMockup: PropTypes.bool
};

export default CostExplorer;
