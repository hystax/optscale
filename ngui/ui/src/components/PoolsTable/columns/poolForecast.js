import React from "react";
import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";
import Tooltip from "components/Tooltip";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { percentXofY, round } from "utils/math";
import { isForecastOverLimit } from "../utils";

const poolForecast = () => ({
  header: <TextWithDataTestId dataTestId="lbl_forecast" messageId="forecastThisMonth" />,
  accessorKey: "forecast",
  cell: ({ cell, row: { original } }) => {
    const forecast = cell.getValue();
    const { hasLimit, limit } = original;

    const exceededForecast = hasLimit && isForecastOverLimit(original);

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
      >
        <Typography component="span" sx={{ color: exceededForecast ? "warning.main" : undefined }}>
          <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cell.getValue()} />
          {timesMore}
        </Typography>
      </Tooltip>
    );
  },
  columnSelector: {
    accessor: "forecast",
    messageId: "forecast",
    dataTestId: "btn_toggle_forecast"
  }
});

export default poolForecast;
