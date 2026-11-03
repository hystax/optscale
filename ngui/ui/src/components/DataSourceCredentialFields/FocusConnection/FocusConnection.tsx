import { useEffect } from "react";
import { Stack, Typography } from "@mui/material";
import { Controller, FieldValues, useFormContext, useWatch } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import ButtonGroup from "components/ButtonGroup";
import { TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";
import { isValidRegex } from "utils/validation";
import { CONNECTION_MODES, DEFAULT_FILE_PATTERN, FIELD_NAMES } from "./constants";
import { isHttpsEndpoint, isKeyPairConsistent } from "./utils";

const KEY_FIELD_NAMES = [FIELD_NAMES.ACCESS_KEY_ID, FIELD_NAMES.SECRET_ACCESS_KEY];

const AccessKeyInputs = () => {
  const intl = useIntl();

  const {
    control,
    trigger,
    formState: { isSubmitted },
  } = useFormContext();

  const [accessKeyId, secretAccessKey] = useWatch({ control, name: KEY_FIELD_NAMES });

  // Keep the key pair errors in sync: changing one key can fix or break the other one
  useEffect(() => {
    if (isSubmitted) {
      trigger(KEY_FIELD_NAMES);
    }
  }, [accessKeyId, secretAccessKey, isSubmitted, trigger]);

  // The error is shown on the empty key only
  const validateKeyPair = (value: string = "", formValues: FieldValues) =>
    value.trim() !== "" ||
    isKeyPairConsistent(formValues[FIELD_NAMES.ACCESS_KEY_ID] ?? "", formValues[FIELD_NAMES.SECRET_ACCESS_KEY] ?? "")
      ? true
      : intl.formatMessage({ id: "focusBothKeysRequired" });

  return (
    <>
      <TextInput
        name={FIELD_NAMES.ACCESS_KEY_ID}
        dataTestId="input_focus_access_key_id"
        validate={{ keyPair: validateKeyPair }}
        InputProps={{
          endAdornment: <QuestionMark messageId="focusAccessKeysTooltip" dataTestId="qmark_focus_access_key_id" />,
        }}
        label={<FormattedMessage id="accessKeyId" />}
        autoComplete="off"
      />
      <TextInput
        name={FIELD_NAMES.SECRET_ACCESS_KEY}
        masked
        dataTestId="input_focus_secret_access_key"
        validate={{ keyPair: validateKeyPair }}
        label={<FormattedMessage id="secretAccessKey" />}
        autoComplete="off"
      />
    </>
  );
};

const BucketInputs = () => {
  const intl = useIntl();

  return (
    <>
      <TextInput
        name={FIELD_NAMES.BUCKET_NAME}
        required
        dataTestId="input_focus_bucket_name"
        InputProps={{
          endAdornment: <QuestionMark messageId="focusBucketNameTooltip" dataTestId="qmark_focus_bucket_name" />,
        }}
        label={<FormattedMessage id="bucketName" />}
      />
      <TextInput
        name={FIELD_NAMES.BUCKET_PREFIX}
        dataTestId="input_focus_bucket_prefix"
        InputProps={{
          endAdornment: <QuestionMark messageId="focusBucketPrefixTooltip" dataTestId="qmark_focus_bucket_prefix" />,
        }}
        label={<FormattedMessage id="pathPrefix" />}
      />
      <TextInput
        name={FIELD_NAMES.S3_ENDPOINT}
        dataTestId="input_focus_s3_endpoint"
        validate={{
          https: (value: string = "") =>
            isHttpsEndpoint(value) ? true : intl.formatMessage({ id: "focusEndpointMustBeHttps" }),
        }}
        InputProps={{
          endAdornment: <QuestionMark messageId="focusS3EndpointTooltip" dataTestId="qmark_focus_s3_endpoint" />,
        }}
        label={<FormattedMessage id="s3Endpoint" />}
      />
      <TextInput
        name={FIELD_NAMES.REGION_NAME}
        dataTestId="input_focus_region_name"
        InputProps={{
          endAdornment: <QuestionMark messageId="focusRegionNameTooltip" dataTestId="qmark_focus_region_name" />,
        }}
        label={<FormattedMessage id="region" />}
      />
      <AccessKeyInputs />
      <TextInput
        name={FIELD_NAMES.FILE_PATTERN}
        dataTestId="input_focus_file_pattern"
        placeholder={DEFAULT_FILE_PATTERN}
        validate={{
          regex: (value: string = "") => (isValidRegex(value) ? true : intl.formatMessage({ id: "focusInvalidFilePattern" })),
        }}
        InputProps={{
          endAdornment: (
            <QuestionMark
              messageId="focusFilePatternTooltip"
              messageValues={{ defaultPattern: DEFAULT_FILE_PATTERN }}
              dataTestId="qmark_focus_file_pattern"
            />
          ),
        }}
        label={<FormattedMessage id="focusFilePattern" />}
      />
    </>
  );
};

const FocusConnection = () => {
  const { control } = useFormContext();

  return (
    <Controller
      name={FIELD_NAMES.CONNECTION_MODE}
      control={control}
      defaultValue={CONNECTION_MODES.MANUAL_UPLOAD}
      render={({ field: { value: connectionMode, onChange } }) => (
        <>
          <Stack direction="row" alignItems="center" spacing={2} mt={2} mb={2}>
            <Typography>
              <FormattedMessage id="connectionType" />
            </Typography>
            <ButtonGroup
              buttons={[
                {
                  id: CONNECTION_MODES.MANUAL_UPLOAD,
                  messageId: "focusManualUpload",
                  dataTestId: "btn_focus_manual_upload",
                  action: () => onChange(CONNECTION_MODES.MANUAL_UPLOAD),
                },
                {
                  id: CONNECTION_MODES.BUCKET,
                  messageId: "focusS3CompatibleBucket",
                  dataTestId: "btn_focus_bucket",
                  action: () => onChange(CONNECTION_MODES.BUCKET),
                },
              ]}
              activeButtonId={connectionMode}
              activeButtonIndex={undefined}
              fullWidth={false}
            />
          </Stack>
          {connectionMode === CONNECTION_MODES.BUCKET && <BucketInputs />}
        </>
      )}
    />
  );
};

export default FocusConnection;
