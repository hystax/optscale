import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import ProgressBar from "components/ProgressBar";
import Tooltip from "components/Tooltip";
import { FORMATTED_MONEY_TYPES, SUCCESS } from "utils/constants";
import { percentXofY, round, intPercentXofY } from "utils/math";

type PoolExpensesProps = {
  limit: number;
  cost: number;
};

const NoLimit = ({ cost }: { cost: number }) => (
  <Tooltip title={<FormattedMessage id="thisPoolHasNoLimit" />} placement="top">
    <Typography component="span">
      <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cost} />
    </Typography>
  </Tooltip>
);

const CostOverLimit = ({ cost, limit }: PoolExpensesProps) => {
  const xTimesMoreValue = round(percentXofY(cost, limit), 1);
  const xTimesMore = xTimesMoreValue === 1 ? "" : ` (x${xTimesMoreValue})`;

  return (
    <Tooltip
      title={
        <FormattedMessage
          id="thisMonthExpensesExceedThePoolLimitBy"
          values={{
            value: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cost - limit} />
          }}
        />
      }
      placement="top"
    >
      <Typography sx={{ fontWeight: "bold" }} color="error" component="span">
        <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cost} />
        {xTimesMore}
      </Typography>
    </Tooltip>
  );
};

const CostUnderLimit = ({ cost, limit }: PoolExpensesProps) => {
  const percent = intPercentXofY(cost, limit);

  return (
    <ProgressBar
      wrapperSx={{ width: "100%", maxWidth: "150px" }}
      tooltip={{
        show: cost !== 0,
        value: (
          <FormattedMessage
            id="leftX"
            values={{
              value: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={limit - cost} />
            }}
          />
        )
      }}
      color={SUCCESS}
      value={percent}
    >
      <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cost} />
    </ProgressBar>
  );
};

const PoolExpenses = ({ cost, limit }: PoolExpensesProps) => {
  if (limit === 0) {
    return <NoLimit cost={cost} />;
  }

  if (cost > limit) {
    return <CostOverLimit cost={cost} limit={limit} />;
  }

  return <CostUnderLimit cost={cost} limit={limit} />;
};

export default PoolExpenses;
