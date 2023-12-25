import { Box } from "@mui/material";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";
import { SPACING_1 } from "utils/layouts";

export const KEY_FIELD_NAME = "tagKey";
export const VALUE_FIELD_NAME = "tagValue";

const CustomTagField = ({ isLoading }) => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return (
    <>
      <Box display="flex" gap={SPACING_1}>
        <Box flexGrow={1} flexBasis="150px">
          {isLoading ? (
            <InputLoader fullWidth />
          ) : (
            <Input
              dataTestId="input_custom_tag"
              label={<FormattedMessage id="tagForCreatedResources" />}
              error={!!errors[KEY_FIELD_NAME]}
              required
              helperText={errors[KEY_FIELD_NAME] && errors[KEY_FIELD_NAME].message}
              {...register(KEY_FIELD_NAME, {
                required: {
                  value: true,
                  message: intl.formatMessage({ id: "thisFieldIsRequired" })
                },
                maxLength: {
                  value: DEFAULT_MAX_INPUT_LENGTH,
                  message: intl.formatMessage(
                    { id: "maxLength" },
                    { inputName: intl.formatMessage({ id: "tagForCreatedResources" }), max: DEFAULT_MAX_INPUT_LENGTH }
                  )
                }
              })}
            />
          )}
        </Box>
        <Box flexGrow={2} flexBasis="200px">
          {isLoading ? (
            <InputLoader fullWidth />
          ) : (
            <Input
              dataTestId="input_custom_tag"
              label={<FormattedMessage id="customTagValue" />}
              required
              error={!!errors[VALUE_FIELD_NAME]}
              helperText={errors[VALUE_FIELD_NAME] && errors[VALUE_FIELD_NAME].message}
              {...register(VALUE_FIELD_NAME, {
                required: {
                  value: true,
                  message: intl.formatMessage({ id: "thisFieldIsRequired" })
                },
                maxLength: {
                  value: DEFAULT_MAX_INPUT_LENGTH,
                  message: intl.formatMessage(
                    { id: "maxLength" },
                    { inputName: intl.formatMessage({ id: "customTagValue" }), max: DEFAULT_MAX_INPUT_LENGTH }
                  )
                }
              })}
            />
          )}
        </Box>
      </Box>
    </>
  );
};

export default CustomTagField;
