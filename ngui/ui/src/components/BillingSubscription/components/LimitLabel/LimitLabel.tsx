import WarningAmberOutlinedIcon from "@mui/icons-material/WarningAmberOutlined";
import { Box, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import IconLabel from "components/IconLabel";
import KeyValueLabel from "components/KeyValueLabel";
import QuestionMark from "components/QuestionMark";

type LimitLabelProps = {
  value: number;
  entityName: string;
  limit: number;
  quantity?: number;
  formatValue?: (value: number) => string;
  formatLimit?: (limit: number) => string;
};

const LimitLabel = ({ value, entityName, limit, quantity = 1, formatValue, formatLimit }: LimitLabelProps) => {
  const totalLimit = limit * quantity;

  const isLimitExceeded = value > totalLimit;

  return (
    <Box display="flex" alignItems="center">
      <IconLabel
        icon={isLimitExceeded ? <WarningAmberOutlinedIcon fontSize="inherit" color="error" /> : null}
        label={
          <Typography color={isLimitExceeded ? "error" : "inherit"}>
            <FormattedMessage
              id="value / value"
              values={{
                value1: typeof formatValue === "function" ? formatValue(value) : value,
                value2: typeof formatLimit === "function" ? formatLimit(totalLimit) : totalLimit,
              }}
            />
            &nbsp;{entityName}
          </Typography>
        }
      />
      {quantity > 1 && (
        <>
          &nbsp;
          <QuestionMark
            tooltipText={
              <>
                {limit > 1 ? (
                  <KeyValueLabel
                    keyMessageId="quantityPerSeat"
                    value={<strong>{typeof formatLimit === "function" ? formatLimit(limit) : limit}</strong>}
                  />
                ) : null}
                <KeyValueLabel keyMessageId="seats" value={<strong>{quantity}</strong>} />
              </>
            }
            fontSize="small"
            color="secondary"
            withLeftMargin={false}
          />
        </>
      )}
    </Box>
  );
};

export default LimitLabel;
