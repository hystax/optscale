import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import RadioGroupField from "components/RadioGroupField";
import { TTL_LIMIT_MAX } from "utils/constants";
import { isWholeNumber } from "utils/validation";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.TTL_MODE;

const predefinedTtlRadioName = FIELD_NAMES.PREDEFINED_TTL;
const customTtlRadioName = FIELD_NAMES.CUSTOM_TTL;
const ttlInputName = FIELD_NAMES.CUSTOM_TTL;

const TtlField = ({ ttlPolicyLimit, ttlMode, isLoading = false }) => {
  const {
    control,
    register,
    setValue,
    watch,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();
  const customTtlValue = watch(ttlInputName);

  const shouldShowCustomTtlInputError = !!(ttlMode === customTtlRadioName && errors[ttlInputName]);

  return (
    <Controller
      control={control}
      name={FIELD_NAME}
      render={({ field }) => (
        <RadioGroupField
          required
          fullWidth
          radioGroupProps={field}
          labelMessageId="ttl"
          error={shouldShowCustomTtlInputError}
          helperText={errors?.[ttlInputName]?.message}
          radioButtons={[
            {
              dataTestId: "radiobtn_current_pool",
              disabled: !ttlPolicyLimit,
              isLoading,
              value: predefinedTtlRadioName,
              label: (
                <span data-test-id="lbl_current_pool">
                  <FormattedMessage
                    id="currentPoolPolicy"
                    values={{
                      strong: (chunks) => <strong>{chunks}</strong>,
                      ttl: ttlPolicyLimit || "-"
                    }}
                  />
                </span>
              )
            },
            {
              value: customTtlRadioName,
              dataTestId: "radiobtn_custom_pool",
              isLoading,
              label: (
                <div data-test-id="lbl_custom_pool" style={{ display: "flex", justifyContent: "center", alignItems: "center" }}>
                  <FormattedMessage id="custom" />
                  {":"}&nbsp;
                  <Input
                    dataTestId="input_custom_pool"
                    onClick={() => setValue(FIELD_NAME, customTtlRadioName)}
                    error={shouldShowCustomTtlInputError}
                    style={{
                      width: 125
                    }}
                    inputProps={{
                      min: 1,
                      max: TTL_LIMIT_MAX,
                      style: {
                        textAlign: "center",
                        fontWeight: "bold"
                      }
                    }}
                    InputProps={{
                      endAdornment: (
                        <strong>
                          <FormattedMessage id="pluralHoursValue" values={{ value: customTtlValue }} />
                        </strong>
                      )
                    }}
                    {...register(ttlInputName, {
                      validate: {
                        whole: (value) => (isWholeNumber(value) ? intl.formatMessage({ id: "wholeNumber" }) : true),
                        required: (value) =>
                          ttlMode === customTtlRadioName && !value ? intl.formatMessage({ id: "specifyTheTTLValue" }) : true
                      },
                      min: {
                        value: 1,
                        message: intl.formatMessage({ id: "moreOrEqual" }, { min: 1 })
                      },
                      max: {
                        value: TTL_LIMIT_MAX,
                        message: intl.formatMessage({ id: "lessOrEqual" }, { max: TTL_LIMIT_MAX })
                      }
                    })}
                  />
                </div>
              )
            }
          ]}
        />
      )}
    />
  );
};

export default TtlField;
