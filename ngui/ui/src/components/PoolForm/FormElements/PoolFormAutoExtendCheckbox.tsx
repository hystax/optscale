import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import { useFormContext, Controller } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import CheckboxLoader from "components/CheckboxLoader";
import QuestionMark from "components/QuestionMark";

export const AUTO_EXTENTION_FIELD_NAME = "autoExtension";

const PoolFormAutoExtendCheckbox = ({ isLoading, isReadOnly = false }) => {
  const { control } = useFormContext();

  return isLoading ? (
    <CheckboxLoader fullWidth />
  ) : (
    <FormControlLabel
      control={
        <Controller
          name={AUTO_EXTENTION_FIELD_NAME}
          control={control}
          render={({ field: { onChange, ...rest } }) => (
            <Checkbox
              disabled={isReadOnly}
              data-test-id="checkbox_auto_extension"
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

export default PoolFormAutoExtendCheckbox;
