import React from "react";
import { FormHelperText, Input, Skeleton, Typography } from "@mui/material";
import PropTypes from "prop-types";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import {
  INACTIVE_USERS_TYPE,
  INACTIVE_CONSOLE_USERS_TYPE,
  ABANDONED_INSTANCES_TYPE,
  INSTANCES_FOR_SHUTDOWN_TYPE,
  VOLUMES_NOT_ATTACHED_FOR_A_LONG_TIME_TYPE,
  OBSOLETE_IMAGES_TYPE,
  OBSOLETE_SNAPSHOTS_TYPE,
  ABANDONED_KINESIS_STREAMS_TYPE,
  ABANDONED_S3_BUCKETS_TYPE,
  COMMON_YEAR_LENGTH,
  MAX_INT_32
} from "utils/constants";
import { isEmpty as isEmptyObject } from "utils/objects";
import { isWhitespaceString } from "utils/strings";
import { isPositiveNumberOrZero, isWholeNumber, lessOrEqual, notOnlyWhiteSpaces } from "utils/validation";

export const THRESHOLDS_FORM_FIELD_NAME_ROOT = "thresholds";
export const THRESHOLD_INPUT_NAMES = Object.freeze({
  DAYS_THRESHOLD: "daysThreshold",
  CPU_PERCENT_THRESHOLD: "cpuPercentThreshold",
  NETWORK_BPS_THRESHOLD: "networkBpsThreshold",
  DATA_SIZE_THRESHOLD: "dataSizeThreshold",
  TIER_1_REQUESTS_QUANTITY_THRESHOLD: "tier1RequestsQuantityThreshold",
  TIER_2_REQUESTS_QUANTITY_THRESHOLD: "tier2RequestsQuantityThreshold"
});

const TextWithInlineInput = ({
  formFieldNameRoot,
  name,
  messageId,
  messageValues = {},
  maxWidth = "50px",
  lessOrEqualValidation = lessOrEqual(MAX_INT_32),
  isLoading = false,
  onChange,
  ...rest
}) => {
  const intl = useIntl();

  const {
    register,
    formState: { errors }
  } = useFormContext();

  const inputName = `${formFieldNameRoot}.${name}`;

  const error = errors[formFieldNameRoot]?.[name] ?? {};
  const isError = !isEmptyObject(error);

  const input = (
    <Input
      style={{ margin: 0, maxWidth }}
      error={isError}
      inputProps={{ style: { padding: "0", textAlign: "center" } }}
      {...rest}
    />
  );

  const getInput = () => {
    const { onChange: onValueChange, ...restRegisterProps } = register(inputName, {
      // valueAsNumber converts a string with only white spaces to 0, so the notOnlyWhiteSpaces validation wont work with valueAsNumber=true
      // so we keep the value as is and just add the notOnlyWhiteSpaces validation
      setValueAs: (value) => {
        if (value === "" || isWhitespaceString(value)) {
          // Return "" in order to trigger "required" validation
          // Return string containing only whitespace characters in order to trigger "white-spaces" validation
          return value;
        }
        return +value;
      },
      required: {
        value: true,
        message: intl.formatMessage({ id: "thisFieldIsRequired" })
      },
      validate: {
        whole: (value) => (isWholeNumber(value) ? intl.formatMessage({ id: "wholeNumber" }) : true),
        moreOrEqualZero: (value) =>
          isPositiveNumberOrZero(value) ? true : intl.formatMessage({ id: "moreOrEqual" }, { min: 0 }),
        lessOrEqualValidation,
        notOnlyWhiteSpaces
      }
    });
    return (
      <Input
        style={{ margin: 0, maxWidth }}
        error={isError}
        inputProps={{ style: { padding: "0", textAlign: "center" } }}
        onChange={(event) => {
          onValueChange(event);
          onChange();
        }}
        {...restRegisterProps}
      />
    );
  };

  return (
    <Typography component="div">
      <FormattedMessage
        id={messageId}
        values={{
          ...messageValues,
          input: isLoading ? <Skeleton sx={{ display: "inline-flex" }}>{input}</Skeleton> : getInput()
        }}
      />
      {isError && <FormHelperText error>{error.message}</FormHelperText>}
    </Typography>
  );
};

const DaysThresholdTextWithInlineInput = ({ messageId, isLoading, ...rest }) => (
  <TextWithInlineInput
    messageId={messageId}
    name={THRESHOLD_INPUT_NAMES.DAYS_THRESHOLD}
    lessOrEqualValidation={lessOrEqual(COMMON_YEAR_LENGTH)}
    isLoading={isLoading}
    {...rest}
  />
);

const Form = ({ formFieldNameRoot, backendRecommendationType, onChange, isLoading }) => {
  const getSimpleDaysThresholdTextWithInlineInput = (messageId) => (
    <DaysThresholdTextWithInlineInput
      formFieldNameRoot={formFieldNameRoot}
      onChange={onChange}
      messageId={messageId}
      isLoading={isLoading}
    />
  );

  switch (backendRecommendationType) {
    case INACTIVE_USERS_TYPE:
      return getSimpleDaysThresholdTextWithInlineInput("thresholds.inactiveUsers");
    case INACTIVE_CONSOLE_USERS_TYPE:
      return getSimpleDaysThresholdTextWithInlineInput("thresholds.inactiveConsoleUsers");
    case VOLUMES_NOT_ATTACHED_FOR_A_LONG_TIME_TYPE:
      return getSimpleDaysThresholdTextWithInlineInput("thresholds.volumesNotAttached");
    case OBSOLETE_IMAGES_TYPE:
      return getSimpleDaysThresholdTextWithInlineInput("thresholds.obsoleteImages");
    case ABANDONED_KINESIS_STREAMS_TYPE:
      return getSimpleDaysThresholdTextWithInlineInput("thresholds.abandonedKinesisStreams");
    case OBSOLETE_SNAPSHOTS_TYPE:
      return (
        <Typography component="div">
          <FormattedMessage id="thresholds.obsoleteSnapshots.title" />
          <ul>
            <li>
              <FormattedMessage id="thresholds.obsoleteSnapshots.listItem1" />
            </li>
            <li>
              <FormattedMessage id="thresholds.obsoleteSnapshots.listItem2" />
            </li>
            <li>{getSimpleDaysThresholdTextWithInlineInput("thresholds.obsoleteSnapshots.listItem3")}</li>
          </ul>
        </Typography>
      );
    case ABANDONED_INSTANCES_TYPE:
      return (
        <>
          {getSimpleDaysThresholdTextWithInlineInput("thresholds.abandonedInstances.intro")}
          <ul>
            <li>
              <TextWithInlineInput
                messageId="thresholds.abandonedInstances.listItem1"
                name={THRESHOLD_INPUT_NAMES.CPU_PERCENT_THRESHOLD}
                isLoading={isLoading}
                formFieldNameRoot={formFieldNameRoot}
                onChange={onChange}
              />
            </li>
            <li>
              <TextWithInlineInput
                messageId="thresholds.abandonedInstances.listItem2"
                maxWidth="60px"
                name={THRESHOLD_INPUT_NAMES.NETWORK_BPS_THRESHOLD}
                isLoading={isLoading}
                formFieldNameRoot={formFieldNameRoot}
                onChange={onChange}
              />
            </li>
          </ul>
        </>
      );
    case INSTANCES_FOR_SHUTDOWN_TYPE:
      return (
        <>
          {getSimpleDaysThresholdTextWithInlineInput("thresholds.instancesForShutdown.intro")}
          <ul>
            <li>
              <TextWithInlineInput
                messageId="thresholds.abandonedInstances.listItem1"
                name={THRESHOLD_INPUT_NAMES.CPU_PERCENT_THRESHOLD}
                isLoading={isLoading}
                formFieldNameRoot={formFieldNameRoot}
                onChange={onChange}
              />
            </li>
            <li>
              <TextWithInlineInput
                messageId="thresholds.abandonedInstances.listItem2"
                maxWidth="60px"
                name={THRESHOLD_INPUT_NAMES.NETWORK_BPS_THRESHOLD}
                isLoading={isLoading}
                formFieldNameRoot={formFieldNameRoot}
                onChange={onChange}
              />
            </li>
          </ul>
        </>
      );
    case ABANDONED_S3_BUCKETS_TYPE: {
      return (
        <>
          {getSimpleDaysThresholdTextWithInlineInput("thresholds.abandonedS3Buckets.intro")}
          <ul>
            <li>
              <TextWithInlineInput
                messageId="thresholds.abandonedS3Buckets.dataSizeThreshold"
                name={THRESHOLD_INPUT_NAMES.DATA_SIZE_THRESHOLD}
                isLoading={isLoading}
                formFieldNameRoot={formFieldNameRoot}
                onChange={onChange}
              />
            </li>
            <li>
              <TextWithInlineInput
                messageId="thresholds.abandonedS3Buckets.tier1RequestsQuantityThreshold"
                maxWidth="60px"
                name={THRESHOLD_INPUT_NAMES.TIER_1_REQUESTS_QUANTITY_THRESHOLD}
                isLoading={isLoading}
                formFieldNameRoot={formFieldNameRoot}
                onChange={onChange}
              />
            </li>
            <li>
              <TextWithInlineInput
                messageId="thresholds.abandonedS3Buckets.getRequestsQuantityThreshold"
                maxWidth="60px"
                name={THRESHOLD_INPUT_NAMES.TIER_2_REQUESTS_QUANTITY_THRESHOLD}
                isLoading={isLoading}
                formFieldNameRoot={formFieldNameRoot}
                onChange={onChange}
              />
            </li>
          </ul>
        </>
      );
    }
    default:
      return null;
  }
};

const Thresholds = ({ formFieldNameRoot, backendRecommendationType, onChange, isLoading = false }) => (
  <Form
    formFieldNameRoot={formFieldNameRoot}
    backendRecommendationType={backendRecommendationType}
    onChange={onChange}
    isLoading={isLoading}
  />
);

Thresholds.propTypes = {
  formFieldNameRoot: PropTypes.string.isRequired,
  backendRecommendationType: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default Thresholds;
