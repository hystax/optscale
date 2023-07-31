import React from "react";
import FormattedMoney from "components/FormattedMoney";
import { FORMATTED_MONEY_TYPES, COST_MODEL_MONEY_MAXIMUM_FRACTION_DIGITS } from "utils/constants";

const CostModelFormattedMoney = ({ value }) => (
  <FormattedMoney
    type={FORMATTED_MONEY_TYPES.TINY}
    maximumFractionDigits={COST_MODEL_MONEY_MAXIMUM_FRACTION_DIGITS}
    value={value}
  />
);

export default CostModelFormattedMoney;
