import React from "react";
import PropTypes from "prop-types";
import { FormattedNumber } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import {
  EXPENSE_ANOMALY,
  EXPIRING_BUDGET_POLICY,
  RECURRING_BUDGET_POLICY,
  QUOTA_POLICY,
  RESOURCE_COUNT_ANOMALY,
  TAGGING_POLICY
} from "utils/constants";
import { getPercentageChangeModule } from "utils/math";

const MAXIMUM_FRACTION_DIGITS = 2;

// Temporary solution, create factories for all types of constraints
const getValue = (hitValue, constraintLimit, type) => {
  const percentageChange =
    constraintLimit !== 0 ? (
      <>
        &nbsp;(
        <FormattedNumber value={getPercentageChangeModule(hitValue, constraintLimit) / 100} format="percentage" />)
      </>
    ) : null;

  return (
    {
      [RESOURCE_COUNT_ANOMALY]: (
        <>
          <FormattedNumber value={constraintLimit} maximumFractionDigits={MAXIMUM_FRACTION_DIGITS} />
          {" ⟶ "}
          <FormattedNumber value={hitValue} maximumFractionDigits={MAXIMUM_FRACTION_DIGITS} />
          {percentageChange}
        </>
      ),
      [EXPENSE_ANOMALY]: (
        <>
          <FormattedMoney value={constraintLimit} />
          {" ⟶ "}
          <FormattedMoney value={hitValue} />
          {percentageChange}
        </>
      ),
      [QUOTA_POLICY]: (
        <>
          <FormattedNumber value={constraintLimit} maximumFractionDigits={MAXIMUM_FRACTION_DIGITS} />
          {" ⟶ "}
          <FormattedNumber value={hitValue} maximumFractionDigits={MAXIMUM_FRACTION_DIGITS} />
        </>
      ),
      [EXPIRING_BUDGET_POLICY]: (
        <>
          <FormattedMoney value={constraintLimit} />
          {" ⟶ "}
          <FormattedMoney value={hitValue} />
        </>
      ),
      [RECURRING_BUDGET_POLICY]: (
        <>
          <FormattedMoney value={constraintLimit} />
          {" ⟶ "}
          <FormattedMoney value={hitValue} />
        </>
      ),
      [TAGGING_POLICY]: <FormattedNumber value={hitValue} maximumFractionDigits={MAXIMUM_FRACTION_DIGITS} />
    }[type] ?? null
  );
};

const ConstraintValue = ({ hitValue, constraintLimit, type }) => getValue(hitValue, constraintLimit, type);

ConstraintValue.propTypes = {
  hitValue: PropTypes.number.isRequired,
  constraintLimit: PropTypes.number.isRequired,
  type: PropTypes.string.isRequired
};

export default ConstraintValue;
