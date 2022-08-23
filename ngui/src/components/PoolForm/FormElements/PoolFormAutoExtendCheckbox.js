import React from "react";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import PropTypes from "prop-types";
import { useFormContext, Controller } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import CheckboxLoader from "components/CheckboxLoader";
import QuestionMark from "components/QuestionMark";

const PoolFormAutoExtendCheckbox = ({ isLoading }) => {
  const { control } = useFormContext();

  return isLoading ? (
    <CheckboxLoader fullWidth />
  ) : (
    <FormControlLabel
      control={
        <Controller
          name="autoExtension"
          control={control}
          render={({ field: { value, onChange, ...rest } }) => (
            <Checkbox
              data-test-id="checkbox_auto_extension"
              checked={value}
              {...rest}
              onChange={(event) => onChange(event.target.checked)}
            />
          )}
        />
      }
      label={
        <div style={{ display: "flex", alignItems: "center" }}>
          <FormattedMessage id="extendParentPoolsLimit" />
          <QuestionMark messageId="extendParentPoolsLimitDescription" dataTestId="qmark_auto_extension" />
        </div>
      }
    />
  );
};
PoolFormAutoExtendCheckbox.propTypes = {
  isLoading: PropTypes.bool
};

export default PoolFormAutoExtendCheckbox;
