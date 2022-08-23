import React from "react";
import PropTypes from "prop-types";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import RadioGroupField from "components/RadioGroupField";
import { TTL_LIMIT_MAX } from "utils/constants";
import { isWholeNumber } from "utils/validation";

const TtlAnalysisFormTtlField = ({
  ttlFieldName,
  predefinedTtlRadioName,
  customTtlRadioName,
  ttlInputName,
  ttlPolicyLimit,
  ttlMode,
  isLoading = false
}) => {
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
      name={ttlFieldName}
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
                    onClick={() => setValue(ttlFieldName, customTtlRadioName)}
                    type="number"
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

TtlAnalysisFormTtlField.propTypes = {
  ttlFieldName: PropTypes.string.isRequired,
  predefinedTtlRadioName: PropTypes.string.isRequired,
  customTtlRadioName: PropTypes.string.isRequired,
  ttlInputName: PropTypes.string.isRequired,
  ttlPolicyLimit: PropTypes.number,
  ttlMode: PropTypes.string,
  isLoading: PropTypes.bool
};

export default TtlAnalysisFormTtlField;
