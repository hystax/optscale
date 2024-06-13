import { InputAdornment } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import { NumberInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";
import { isPositiveNumberOrZero } from "utils/validation";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.REQUIRING_ATTENTION;

const RequiringAttentionField = ({ isLoading = false }) => {
  const intl = useIntl();

  return (
    <NumberInput
      name={FIELD_NAME}
      label={<FormattedMessage id="requiringAttention" />}
      required
      dataTestId="input_requiring_attention"
      isLoading={isLoading}
      InputProps={{
        endAdornment: (
          <QuestionMark
            messageId="requiringAttentionDuplicatesSavingThresholdDescription"
            dataTestId="qmark_critical_duplicates_saving_threshold_description"
          />
        ),
        startAdornment: <InputAdornment position="start">$</InputAdornment>
      }}
      validate={{
        positiveNumber: (value) => (isPositiveNumberOrZero(value) ? true : intl.formatMessage({ id: "positiveNumberOrZero" }))
      }}
    />
  );
};

export default RequiringAttentionField;
