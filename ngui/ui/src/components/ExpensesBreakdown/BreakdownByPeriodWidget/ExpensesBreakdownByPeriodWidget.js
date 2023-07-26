import React, { useEffect, useState } from "react";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";
import { useIntl } from "react-intl";
import { useDispatch, useSelector } from "react-redux";
import LinearSelector from "components/LinearSelector";
import { DynamicTextPdf } from "components/PDFAble";
import QuestionMark from "components/QuestionMark";
import { EXPENSES_SPLIT_PERIODS, LINEAR_SELECTOR_ITEMS_TYPES, PDF_ELEMENTS } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { getQueryParams, updateQueryParams } from "utils/network";
import { changePeriodType } from "./actionCreator";
import { EXPENSES_BREAKDOWN_PERIOD_TYPE } from "./reducer";

const PERIOD_TYPE_QUERY_PARAMETER_NAME = "expenses";

const breakdownLinearSelectorItems = [
  {
    name: EXPENSES_SPLIT_PERIODS.DAILY,
    value: EXPENSES_SPLIT_PERIODS.DAILY,
    type: LINEAR_SELECTOR_ITEMS_TYPES.TEXT,
    dataTestId: "breakdown_ls_item_daily"
  },
  {
    name: EXPENSES_SPLIT_PERIODS.WEEKLY,
    value: EXPENSES_SPLIT_PERIODS.WEEKLY,
    type: LINEAR_SELECTOR_ITEMS_TYPES.TEXT,
    dataTestId: "breakdown_ls_item_weekly"
  },
  {
    name: EXPENSES_SPLIT_PERIODS.MONTHLY,
    value: EXPENSES_SPLIT_PERIODS.MONTHLY,
    type: LINEAR_SELECTOR_ITEMS_TYPES.TEXT,
    dataTestId: "breakdown_ls_item_monthly"
  }
];

// todo: unify with resources selector
const BreakdownLinearSelector = ({ value, items, onChange }) => {
  useEffect(() => {
    updateQueryParams({ [PERIOD_TYPE_QUERY_PARAMETER_NAME]: value.name });
  }, [value.name]);

  return <LinearSelector value={value} onChange={onChange} items={items} />;
};

const ExpensesBreakdownByPeriodWidget = ({ render }) => {
  const dispatch = useDispatch();
  const intl = useIntl();
  const { [PERIOD_TYPE_QUERY_PARAMETER_NAME]: periodTypeQueryParameter } = getQueryParams();

  const periodTypeState = useSelector((state) => state[EXPENSES_BREAKDOWN_PERIOD_TYPE]);

  const [periodType, setPeriodType] = useState(() => {
    const breakdown =
      breakdownLinearSelectorItems.find(({ name }) => name === periodTypeQueryParameter) ||
      breakdownLinearSelectorItems.find(({ name }) => name === periodTypeState);

    if (breakdown) {
      return breakdown;
    }

    return breakdownLinearSelectorItems[0];
  });

  useEffect(() => {
    updateQueryParams({
      [PERIOD_TYPE_QUERY_PARAMETER_NAME]: periodType.value
    });
    dispatch(changePeriodType(periodType.value));
  }, [dispatch, periodType]);

  return (
    <>
      <Box display="flex" alignItems="center" mb={SPACING_1}>
        <BreakdownLinearSelector
          value={periodType}
          onChange={({ name, value }) => setPeriodType({ name, value })}
          items={breakdownLinearSelectorItems}
        />
        <QuestionMark
          messageId="expensesBreakdownBarChartDescription"
          messageValues={{ periodType: intl.formatMessage({ id: periodType.value }) }}
        />
      </Box>
      <DynamicTextPdf
        pdfId={PDF_ELEMENTS.costExplorer.periodWidgetTitle}
        renderData={() => ({
          text: {
            [EXPENSES_SPLIT_PERIODS.DAILY]: "dailyExpenses",
            [EXPENSES_SPLIT_PERIODS.WEEKLY]: "weeklyExpenses",
            [EXPENSES_SPLIT_PERIODS.MONTHLY]: "monthlyExpenses"
          }[periodType.value],
          elementType: PDF_ELEMENTS.basics.H2
        })}
      />
      {render(periodType.value)}
    </>
  );
};

ExpensesBreakdownByPeriodWidget.propTypes = {
  render: PropTypes.func.isRequired
};

export default ExpensesBreakdownByPeriodWidget;
