import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import QuestionMark from "components/QuestionMark";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";

export const FIELD_NAMES = Object.freeze({
  BUCKET_NAME: "bucketName",
  EXPORT_NAME: "exportName",
  BUCKET_PREFIX: "bucketPrefix"
});

const DEFAULT_PATH_PREFIX = "reports";

const AwsRootBillingBucket = () => {
  const intl = useIntl();

  const {
    register,
    formState: { errors }
  } = useFormContext();

  return (
    <>
      <Input
        required
        dataTestId="input_export_name"
        key={FIELD_NAMES.EXPORT_NAME}
        error={!!errors[FIELD_NAMES.EXPORT_NAME]}
        helperText={errors[FIELD_NAMES.EXPORT_NAME] && errors[FIELD_NAMES.EXPORT_NAME].message}
        label={<FormattedMessage id="exportName" />}
        {...register(FIELD_NAMES.EXPORT_NAME, {
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          },
          maxLength: {
            value: DEFAULT_MAX_INPUT_LENGTH,
            message: intl.formatMessage(
              { id: "maxLength" },
              { inputName: intl.formatMessage({ id: "exportName" }), max: DEFAULT_MAX_INPUT_LENGTH }
            )
          }
        })}
      />
      <Input
        required
        dataTestId="input_s3_bucket_name"
        key={FIELD_NAMES.BUCKET_NAME}
        error={!!errors[FIELD_NAMES.BUCKET_NAME]}
        helperText={errors[FIELD_NAMES.BUCKET_NAME] && errors[FIELD_NAMES.BUCKET_NAME].message}
        InputProps={{
          endAdornment: <QuestionMark messageId="exportS3BucketNameTooltip" dataTestId="qmark_bucket_name" />
        }}
        label={<FormattedMessage id="exportS3BucketName" />}
        {...register(FIELD_NAMES.BUCKET_NAME, {
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          },
          maxLength: {
            value: DEFAULT_MAX_INPUT_LENGTH,
            message: intl.formatMessage(
              { id: "maxLength" },
              { inputName: intl.formatMessage({ id: "exportS3BucketName" }), max: DEFAULT_MAX_INPUT_LENGTH }
            )
          }
        })}
      />
      <Input
        required
        dataTestId="input_export_path_prefix"
        key={FIELD_NAMES.BUCKET_PREFIX}
        defaultValue={DEFAULT_PATH_PREFIX}
        error={!!errors[FIELD_NAMES.BUCKET_PREFIX]}
        helperText={errors[FIELD_NAMES.BUCKET_PREFIX] && errors[FIELD_NAMES.BUCKET_PREFIX].message}
        InputProps={{
          endAdornment: <QuestionMark messageId="exportPathPrefixTooltip" dataTestId="qmark_prefix" />
        }}
        label={<FormattedMessage id="exportPathPrefix" />}
        {...register(FIELD_NAMES.BUCKET_PREFIX, {
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          },
          maxLength: {
            value: DEFAULT_MAX_INPUT_LENGTH,
            message: intl.formatMessage(
              { id: "maxLength" },
              { inputName: intl.formatMessage({ id: "exportPathPrefix" }), max: DEFAULT_MAX_INPUT_LENGTH }
            )
          }
        })}
      />
    </>
  );
};

export default AwsRootBillingBucket;
