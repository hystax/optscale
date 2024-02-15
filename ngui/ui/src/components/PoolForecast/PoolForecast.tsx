import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import Tooltip from "components/Tooltip";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { percentXofY, round } from "utils/math";
import { hasLimit, isForecastOverLimit } from "utils/pools";

type PoolForecastProps = {
  limit: number;
  forecast: number;
};

const PoolForecast = ({ limit, forecast }: PoolForecastProps) => {
  const exceededForecast = hasLimit(limit) && isForecastOverLimit({ limit, forecast });

  const timesMoreValue = round(percentXofY(Math.max(forecast, 0), limit), 1);
  const timesMore = exceededForecast && timesMoreValue !== 1 ? ` (x${timesMoreValue})` : "";
  return (
    <Tooltip
      title={
        exceededForecast ? (
          <FormattedMessage
            id="forecastExceedsLimitBy"
            values={{
              value: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={forecast - limit} />
            }}
          />
        ) : (
          ""
        )
      }
      placement="top"
    >
      <Typography
        component="span"
        fontWeight={exceededForecast ? "bold" : "inherit"}
        color={exceededForecast ? "warning.main" : "inherit"}
      >
        <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={forecast} />
        {timesMore}
      </Typography>
    </Tooltip>
  );
};

export default PoolForecast;
