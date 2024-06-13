import { Typography } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import { NumberInput } from "components/forms/common/fields";
import { TTL_LIMIT_MAX } from "utils/constants";
import { isWholeNumber } from "utils/validation";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.LIMIT;

const TtlLimitField = () => {
  const intl = useIntl();

  return (
    <NumberInput
      name={FIELD_NAME}
      min={0}
      max={TTL_LIMIT_MAX}
      required
      inputProps={{ min: 0, max: TTL_LIMIT_MAX }}
      InputProps={{
        endAdornment: (
          <Typography
            variant="body2"
            sx={{
              whiteSpace: "nowrap"
            }}
          >
            <FormattedMessage id="hours" />
          </Typography>
        )
      }}
      validate={{
        whole: (value) => (isWholeNumber(value) ? intl.formatMessage({ id: "wholeNumber" }) : true)
      }}
      dataTestId="input_ttl"
      margin="none"
    />
  );
};

export default TtlLimitField;
