import { Typography } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import { NumberInput } from "components/forms/common/fields";
import { TTL_LIMIT_MAX } from "utils/constants";
import { isWholeNumber } from "utils/validation";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.LIMIT;

const TtlLimitInput = () => {
  const intl = useIntl();

  return (
    <NumberInput
      name={FIELD_NAME}
      dataTestId="input_ttl"
      required
      label={<FormattedMessage id="ttl" />}
      InputProps={{
        endAdornment: (
          <Typography variant="body2">
            <FormattedMessage id="hours" />
          </Typography>
        )
      }}
      min={0}
      max={TTL_LIMIT_MAX}
      validate={{
        whole: (value) => (isWholeNumber(value) ? intl.formatMessage({ id: "wholeNumber" }) : true)
      }}
    />
  );
};

export default TtlLimitInput;
