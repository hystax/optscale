import React from "react";
import PropTypes from "prop-types";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import QuestionMark from "components/QuestionMark";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";

export const FIELD_NAME = "bucketName";

const ReportBucketName = ({ disabled = false }) => {
  const intl = useIntl();

  const {
    register,
    formState: { errors }
  } = useFormContext();

  return (
    <Input
      required
      dataTestId="input_nebius_report_bucket_name"
      disabled={disabled}
      error={!!errors[FIELD_NAME]}
      helperText={errors[FIELD_NAME] && errors[FIELD_NAME].message}
      InputProps={{
        endAdornment: (
          <QuestionMark
            messageId="nebiusReportBucketNameTooltip"
            messageValues={{
              i: (chunks) => <i>{chunks}</i>
            }}
            dataTestId="qmark_report_bucket_name"
          />
        )
      }}
      label={<FormattedMessage id="bucketName" />}
      autoComplete="off"
      {...register(FIELD_NAME, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        maxLength: {
          value: DEFAULT_MAX_INPUT_LENGTH,
          message: intl.formatMessage(
            { id: "maxLength" },
            { inputName: intl.formatMessage({ id: "bucketName" }), max: DEFAULT_MAX_INPUT_LENGTH }
          )
        }
      })}
    />
  );
};

ReportBucketName.propTypes = {
  disabled: PropTypes.bool
};

export default ReportBucketName;
