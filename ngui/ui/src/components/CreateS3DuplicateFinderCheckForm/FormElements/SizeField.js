import React from "react";
import { Typography } from "@mui/material";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { SI_UNITS } from "components/FormattedDigitalUnit";
import Input from "components/Input";
import QuestionMark from "components/QuestionMark";
import { MAX_INT_32 } from "utils/constants";
import { isWholeNumber, notOnlyWhiteSpaces } from "utils/validation";

export const FIELD_NAME = "size";

const SizeField = () => {
  const intl = useIntl();

  const {
    register,
    formState: { errors }
  } = useFormContext();

  return (
    <Input
      dataTestId="input_minimum_file_size"
      margin="normal"
      label={<FormattedMessage id="minimumFileSize" />}
      error={!!errors[FIELD_NAME]}
      required
      helperText={errors[FIELD_NAME] && errors[FIELD_NAME].message}
      {...register(FIELD_NAME, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        min: {
          value: 0,
          message: intl.formatMessage({ id: "moreOrEqual" }, { min: 0 })
        },
        max: {
          value: MAX_INT_32,
          message: intl.formatMessage({ id: "lessOrEqual" }, { max: MAX_INT_32 })
        },
        validate: {
          whole: (value) => (isWholeNumber(value) ? intl.formatMessage({ id: "wholeNumber" }) : true),
          notOnlyWhiteSpaces
        }
      })}
      InputProps={{
        endAdornment: (
          <>
            <Typography sx={{ whiteSpace: "nowrap" }}>
              <FormattedMessage
                id="digitalUnits"
                values={{
                  unit: SI_UNITS.MEGABYTE
                }}
              />
            </Typography>
            <QuestionMark messageId="filesLessThanSizeWillBeIgnored" dataTestId="qmark_min_file_size" />
          </>
        )
      }}
    />
  );
};

export default SizeField;
