import React, { useState } from "react";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormProvider, Controller, useForm } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { GAEvent, GA_EVENT_CATEGORIES } from "components/ActivityListener";
import Button from "components/Button";
import ButtonGroupInput from "components/ButtonGroupInput";
import ButtonLoader from "components/ButtonLoader";
import ConnectForm from "components/ConnectForm";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import Input from "components/Input";
import QuestionMark from "components/QuestionMark";
import RadioGroupField from "components/RadioGroupField";
import SwitchField from "components/SwitchField";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import {
  DOCS_HYSTAX_AUTO_BILLING_AWS,
  DOCS_HYSTAX_CONNECT_AZURE_ACCOUNT,
  DOCS_HYSTAX_DISCOVER_RESOURCES,
  GITHUB_HYSTAX_K8S_COST_METRICS_COLLECTOR,
  GITHUB_HYSTAX_EXTRACT_LINKED_REPORTS,
  DOCS_HYSTAX_CONNECT_ALIBABA_CLOUD
} from "urls";
import {
  AWS_CNR,
  AZURE_CNR,
  KUBERNETES_CNR,
  AWS_ROOT_CONNECT_CONFIG_SCHEMES,
  ALIBABA_CNR,
  AWS_ROOT_ACCOUNT,
  AWS_LINKED_ACCOUNT,
  AZURE_SUBSCRIPTION,
  KUBERNETES,
  ALIBABA_ACCOUNT
} from "utils/constants";
import { getQueryParams } from "utils/network";

const MAX_LENGTH = 255;

const PREFIX_AWS_ROOT = "aws_root";
const PREFIX_AWS_LINKED = "aws_linked";
const PREFIX_ALIBABA = "alibaba";

const AWSCredentialsInputs = ({ registerNamePrefix }) => {
  const ACCESS_KEY_ID = `${registerNamePrefix}_accessKeyId`;
  const SECRET_ACCESS_KEY = `${registerNamePrefix}_secretAccessKey`;
  const intl = useIntl();
  return (
    <ConnectForm>
      {({ register, formState: { errors } }) => (
        <>
          <Input
            required
            dataTestId="input_aws_access_key_id"
            error={!!errors[ACCESS_KEY_ID]}
            helperText={errors[ACCESS_KEY_ID] && errors[ACCESS_KEY_ID].message}
            InputProps={{
              endAdornment: (
                <QuestionMark
                  messageId="awsAccessKeyIdTooltip"
                  messageValues={{
                    i: (chunks) => <i>{chunks}</i>
                  }}
                  dataTestId="qmark_access_key"
                />
              )
            }}
            label={<FormattedMessage id="awsAccessKeyId" />}
            autoComplete="off"
            {...register(ACCESS_KEY_ID, {
              required: {
                value: true,
                message: intl.formatMessage({ id: "thisFieldIsRequired" })
              },
              maxLength: {
                value: MAX_LENGTH,
                message: intl.formatMessage(
                  { id: "maxLength" },
                  { inputName: intl.formatMessage({ id: "awsAccessKeyId" }), max: MAX_LENGTH }
                )
              }
            })}
          />
          <Input
            required
            isMasked
            dataTestId="input_secret_key"
            error={!!errors[SECRET_ACCESS_KEY]}
            helperText={errors[SECRET_ACCESS_KEY] && errors[SECRET_ACCESS_KEY].message}
            InputProps={{
              endAdornment: (
                <QuestionMark
                  messageId="awsSecretAccessKeyTooltip"
                  messageValues={{
                    i: (chunks) => <i>{chunks}</i>
                  }}
                  dataTestId="qmark_secret_key"
                />
              )
            }}
            label={<FormattedMessage id="awsSecretAccessKey" />}
            autoComplete="off"
            {...register(SECRET_ACCESS_KEY, {
              required: {
                value: true,
                message: intl.formatMessage({ id: "thisFieldIsRequired" })
              },
              maxLength: {
                value: MAX_LENGTH,
                message: intl.formatMessage(
                  { id: "maxLength" },
                  { inputName: intl.formatMessage({ id: "awsSecretAccessKey" }), max: MAX_LENGTH }
                )
              }
            })}
          />
        </>
      )}
    </ConnectForm>
  );
};

const AwsRootInputs = () => {
  const BUCKET_NAME = "bucketName";
  const BUCKET_PREFIX = "bucketPrefix";
  const REPORT_NAME = "reportName";
  const IS_FIND_REPORT = "isFindReport";
  const DEFAULT_PATH_PREFIX = "reports";
  const CONFIG_SCHEME = "configScheme";

  const intl = useIntl();

  return (
    <ConnectForm>
      {({ register, formState: { errors }, control, watch }) => {
        const isFindReportWatch = watch(IS_FIND_REPORT, true);
        const configScheme =
          watch(CONFIG_SCHEME, AWS_ROOT_CONNECT_CONFIG_SCHEMES.CREATE_REPORT) || AWS_ROOT_CONNECT_CONFIG_SCHEMES.CREATE_REPORT;
        return (
          <>
            <AWSCredentialsInputs registerNamePrefix={PREFIX_AWS_ROOT} />
            <SwitchField
              name={IS_FIND_REPORT}
              defaultValue={isFindReportWatch}
              control={control}
              dataTestIds={{
                labelText: "lbl_use_report",
                input: "checkbox_user_report"
              }}
              labelMessageId="costAndUsageReportDetection"
              endAdornment={
                <QuestionMark
                  messageId="costAndUsageReportDetectionTooltip"
                  messageValues={{
                    break: <br />
                  }}
                  dataTestId="qmark_user_report"
                />
              }
            />
            {!isFindReportWatch && (
              <>
                <Controller
                  control={control}
                  name={CONFIG_SCHEME}
                  defaultValue={configScheme}
                  render={({ field }) => (
                    <RadioGroupField
                      required
                      fullWidth
                      radioGroupProps={field}
                      radioButtons={[
                        {
                          value: AWS_ROOT_CONNECT_CONFIG_SCHEMES.CREATE_REPORT,
                          label: <FormattedMessage id="createNewCostUsageReport" />
                        },
                        {
                          value: AWS_ROOT_CONNECT_CONFIG_SCHEMES.BUCKET_ONLY,
                          label: <FormattedMessage id="connectOnlyToDataInBucket" />
                        }
                      ]}
                    />
                  )}
                />
                <Typography gutterBottom data-test-id="p_report_params">
                  <FormattedMessage
                    id={
                      configScheme === AWS_ROOT_CONNECT_CONFIG_SCHEMES.CREATE_REPORT
                        ? "costAndUsageReportDetectionDescription1"
                        : "costAndUsageReportDetectionDescription2"
                    }
                  />
                </Typography>
                <Input
                  required
                  dataTestId="input_report_name"
                  key={REPORT_NAME}
                  error={!!errors[REPORT_NAME]}
                  helperText={errors[REPORT_NAME] && errors[REPORT_NAME].message}
                  InputProps={{
                    endAdornment: <QuestionMark messageId="reportNameTooltip" dataTestId="qmark_report_name" />
                  }}
                  label={<FormattedMessage id="reportName" />}
                  {...register(REPORT_NAME, {
                    required: {
                      value: true,
                      message: intl.formatMessage({ id: "thisFieldIsRequired" })
                    },
                    maxLength: {
                      value: MAX_LENGTH,
                      message: intl.formatMessage(
                        { id: "maxLength" },
                        { inputName: intl.formatMessage({ id: "reportName" }), max: MAX_LENGTH }
                      )
                    }
                  })}
                />
                <Input
                  required
                  dataTestId="input_s3_bucket_name"
                  key={BUCKET_NAME}
                  error={!!errors[BUCKET_NAME]}
                  helperText={errors[BUCKET_NAME] && errors[BUCKET_NAME].message}
                  InputProps={{
                    endAdornment: <QuestionMark messageId="reportS3BucketNameTooltip" dataTestId="qmark_bucket_name" />
                  }}
                  label={<FormattedMessage id="reportS3BucketName" />}
                  {...register(BUCKET_NAME, {
                    required: {
                      value: true,
                      message: intl.formatMessage({ id: "thisFieldIsRequired" })
                    },
                    maxLength: {
                      value: MAX_LENGTH,
                      message: intl.formatMessage(
                        { id: "maxLength" },
                        { inputName: intl.formatMessage({ id: "reportS3BucketName" }), max: MAX_LENGTH }
                      )
                    }
                  })}
                />
                <Input
                  required
                  dataTestId="input_report_path_prefix"
                  key={BUCKET_PREFIX}
                  defaultValue={DEFAULT_PATH_PREFIX}
                  error={!!errors[BUCKET_PREFIX]}
                  helperText={errors[BUCKET_PREFIX] && errors[BUCKET_PREFIX].message}
                  InputProps={{
                    endAdornment: <QuestionMark messageId="reportPathPrefixTooltip" dataTestId="qmark_prefix" />
                  }}
                  label={<FormattedMessage id="reportPathPrefix" />}
                  {...register(BUCKET_PREFIX, {
                    required: {
                      value: true,
                      message: intl.formatMessage({ id: "thisFieldIsRequired" })
                    },
                    maxLength: {
                      value: MAX_LENGTH,
                      message: intl.formatMessage(
                        { id: "maxLength" },
                        { inputName: intl.formatMessage({ id: "reportPathPrefix" }), max: MAX_LENGTH }
                      )
                    }
                  })}
                />
              </>
            )}
          </>
        );
      }}
    </ConnectForm>
  );
};

const AwsLinkedInputs = () => <AWSCredentialsInputs registerNamePrefix={PREFIX_AWS_LINKED} />;

const AzureSubscriptionInputs = () => {
  const SUBSCRIPTION_ID = "subscriptionId";
  const CLIENT_ID = "clientId";
  const TENANT = "tenant";
  const SECRET = "secret";

  const intl = useIntl();

  return (
    <ConnectForm>
      {({ register, formState: { errors } }) => (
        <>
          <Input
            required
            dataTestId="input_subscription_id"
            key={SUBSCRIPTION_ID}
            error={!!errors[SUBSCRIPTION_ID]}
            helperText={errors[SUBSCRIPTION_ID] && errors[SUBSCRIPTION_ID].message}
            InputProps={{
              endAdornment: <QuestionMark messageId="subscriptionIdTooltip" dataTestId="qmark_subs_id" />
            }}
            label={<FormattedMessage id={SUBSCRIPTION_ID} />}
            autoComplete="off"
            {...register(SUBSCRIPTION_ID, {
              required: {
                value: true,
                message: intl.formatMessage({ id: "thisFieldIsRequired" })
              },
              maxLength: {
                value: MAX_LENGTH,
                message: intl.formatMessage(
                  { id: "maxLength" },
                  { inputName: intl.formatMessage({ id: SUBSCRIPTION_ID }), max: MAX_LENGTH }
                )
              }
            })}
          />
          <Input
            required
            dataTestId="input_client_id"
            key={CLIENT_ID}
            error={!!errors[CLIENT_ID]}
            helperText={errors[CLIENT_ID] && errors[CLIENT_ID].message}
            InputProps={{
              endAdornment: (
                <QuestionMark
                  messageId="applicationClientIdTooltip"
                  messageValues={{
                    i: (chunks) => <i>{chunks}</i>
                  }}
                  dataTestId="qmark_client_id"
                />
              )
            }}
            label={<FormattedMessage id="applicationClientId" />}
            autoComplete="off"
            {...register(CLIENT_ID, {
              required: {
                value: true,
                message: intl.formatMessage({ id: "thisFieldIsRequired" })
              },
              maxLength: {
                value: MAX_LENGTH,
                message: intl.formatMessage(
                  { id: "maxLength" },
                  { inputName: intl.formatMessage({ id: "applicationClientId" }), max: MAX_LENGTH }
                )
              }
            })}
          />
          <Input
            required
            dataTestId="input_tenant_id"
            key={TENANT}
            error={!!errors[TENANT]}
            helperText={errors[TENANT] && errors[TENANT].message}
            InputProps={{
              endAdornment: (
                <QuestionMark
                  messageId="directoryTenantIdTooltip"
                  messageValues={{
                    i: (chunks) => <i>{chunks}</i>
                  }}
                  dataTestId="qmark_tenant_id"
                />
              )
            }}
            label={<FormattedMessage id="directoryTenantId" />}
            autoComplete="off"
            {...register(TENANT, {
              required: {
                value: true,
                message: intl.formatMessage({ id: "thisFieldIsRequired" })
              },
              maxLength: {
                value: MAX_LENGTH,
                message: intl.formatMessage(
                  { id: "maxLength" },
                  { inputName: intl.formatMessage({ id: "directoryTenantId" }), max: MAX_LENGTH }
                )
              }
            })}
          />
          <Input
            required
            dataTestId="input_azure_secret"
            isMasked
            key={SECRET}
            error={!!errors[SECRET]}
            helperText={errors[SECRET] && errors[SECRET].message}
            InputProps={{
              endAdornment: (
                <QuestionMark
                  messageId="secretTooltip"
                  messageValues={{
                    i: (chunks) => <i>{chunks}</i>
                  }}
                  dataTestId="qmark_secret"
                />
              )
            }}
            label={<FormattedMessage id={SECRET} />}
            autoComplete="off"
            {...register(SECRET, {
              required: {
                value: true,
                message: intl.formatMessage({ id: "thisFieldIsRequired" })
              },
              maxLength: {
                value: MAX_LENGTH,
                message: intl.formatMessage(
                  { id: "maxLength" },
                  { inputName: intl.formatMessage({ id: SECRET }), max: MAX_LENGTH }
                )
              }
            })}
          />
        </>
      )}
    </ConnectForm>
  );
};

const KubernetesInputs = () => {
  const URL = "url";
  const PORT = "port";
  const PASSWORD = "password";
  const USER = "user";

  const intl = useIntl();

  return (
    <ConnectForm>
      {({ register, formState: { errors } }) => (
        <>
          <Input
            placeholder="http(s)://192.168.0.0"
            required
            dataTestId="input_url"
            key={URL}
            error={!!errors[URL]}
            helperText={errors[URL] && errors[URL].message}
            InputProps={{
              endAdornment: <QuestionMark messageId="urlTooltip" dataTestId="qmark_url" />
            }}
            label={<FormattedMessage id={URL} />}
            {...register(URL, {
              required: {
                value: true,
                message: intl.formatMessage({ id: "thisFieldIsRequired" })
              },
              maxLength: {
                value: MAX_LENGTH,
                message: intl.formatMessage(
                  { id: "maxLength" },
                  { inputName: intl.formatMessage({ id: URL }), max: MAX_LENGTH }
                )
              }
            })}
          />
          <Input
            required
            dataTestId="input_port"
            // TODO: We need to check the behaviour (validation and parsing) of "number" type in the Mozilla firefox browser
            // type="number"
            key={PORT}
            error={!!errors[PORT]}
            helperText={errors[PORT] && errors[PORT].message}
            InputProps={{
              endAdornment: <QuestionMark messageId="portTooltip" dataTestId="qmark_port" />
            }}
            label={<FormattedMessage id={PORT} />}
            {...register(PORT, {
              required: {
                value: true,
                message: intl.formatMessage({ id: "thisFieldIsRequired" })
              },
              maxLength: {
                value: MAX_LENGTH,
                message: intl.formatMessage(
                  { id: "maxLength" },
                  { inputName: intl.formatMessage({ id: PORT }), max: MAX_LENGTH }
                )
              },
              validate: {
                positiveIntegerOrZero: (value) => {
                  const valueAsNumber = Number(value);
                  return Number.isInteger(valueAsNumber) && valueAsNumber > 0
                    ? true
                    : intl.formatMessage({ id: "positiveIntegerOrZero" });
                }
              }
            })}
            autoComplete="off"
          />
          <Input
            type="text"
            dataTestId="input_user"
            key={USER}
            error={!!errors[USER]}
            helperText={errors[USER] && errors[USER].message}
            InputProps={{
              endAdornment: <QuestionMark messageId="userTooltip" dataTestId="qmark_user" />
            }}
            label={<FormattedMessage id={USER} />}
            {...register(USER, {
              maxLength: {
                value: MAX_LENGTH,
                message: intl.formatMessage(
                  { id: "maxLength" },
                  { inputName: intl.formatMessage({ id: USER }), max: MAX_LENGTH }
                )
              }
            })}
          />
          <Input
            dataTestId="input_password"
            isMasked
            name={PASSWORD}
            key={PASSWORD}
            error={!!errors[PASSWORD]}
            helperText={errors[PASSWORD] && errors[PASSWORD].message}
            InputProps={{
              endAdornment: <QuestionMark messageId="passwordTooltip" dataTestId="qmark_password" />
            }}
            label={<FormattedMessage id="password" />}
            {...register(PASSWORD, {
              maxLength: {
                value: MAX_LENGTH,
                message: intl.formatMessage(
                  { id: "maxLength" },
                  { inputName: intl.formatMessage({ id: "password" }), max: MAX_LENGTH }
                )
              }
            })}
            autoComplete="off"
          />
        </>
      )}
    </ConnectForm>
  );
};

const AlibabaAccountInputs = () => {
  const ACCESS_KEY_ID = `${PREFIX_ALIBABA}_accessKeyId`;
  const SECRET_ACCESS_KEY = `${PREFIX_ALIBABA}_secretAccessKey`;
  const intl = useIntl();
  return (
    <ConnectForm>
      {({ register, formState: { errors } }) => (
        <>
          <Input
            required
            dataTestId="input_alibaba_access_key_id"
            error={!!errors[ACCESS_KEY_ID]}
            helperText={errors[ACCESS_KEY_ID] && errors[ACCESS_KEY_ID].message}
            InputProps={{
              endAdornment: (
                <QuestionMark
                  messageId="alibabaAccessKeyIdTooltip"
                  messageValues={{
                    i: (chunks) => <i>{chunks}</i>
                  }}
                  dataTestId="qmark_access_key"
                />
              )
            }}
            label={<FormattedMessage id="alibabaAccessKeyId" />}
            autoComplete="off"
            {...register(ACCESS_KEY_ID, {
              required: {
                value: true,
                message: intl.formatMessage({ id: "thisFieldIsRequired" })
              },
              maxLength: {
                value: MAX_LENGTH,
                message: intl.formatMessage(
                  { id: "maxLength" },
                  { inputName: intl.formatMessage({ id: "alibabaAccessKeyId" }), max: MAX_LENGTH }
                )
              }
            })}
          />
          <Input
            required
            isMasked
            dataTestId="input_secret_key"
            name={SECRET_ACCESS_KEY}
            error={!!errors[SECRET_ACCESS_KEY]}
            helperText={errors[SECRET_ACCESS_KEY] && errors[SECRET_ACCESS_KEY].message}
            InputProps={{
              endAdornment: (
                <QuestionMark
                  messageId="alibabaSecretAccessKeyTooltip"
                  messageValues={{
                    i: (chunks) => <i>{chunks}</i>
                  }}
                  dataTestId="qmark_secret_key"
                />
              )
            }}
            label={<FormattedMessage id="alibabaSecretAccessKey" />}
            autoComplete="off"
            {...register(SECRET_ACCESS_KEY, {
              required: {
                value: true,
                message: intl.formatMessage({ id: "thisFieldIsRequired" })
              },
              maxLength: {
                value: MAX_LENGTH,
                message: intl.formatMessage(
                  { id: "maxLength" },
                  { inputName: intl.formatMessage({ id: "alibabaSecretAccessKey" }), max: MAX_LENGTH }
                )
              }
            })}
          />
        </>
      )}
    </ConnectForm>
  );
};

const getCloudType = (connectionType) =>
  ({
    [AWS_ROOT_ACCOUNT]: AWS_CNR,
    [AWS_LINKED_ACCOUNT]: AWS_CNR,
    [AZURE_SUBSCRIPTION]: AZURE_CNR,
    [KUBERNETES]: KUBERNETES_CNR,
    [ALIBABA_ACCOUNT]: ALIBABA_CNR
  }[connectionType]);

const isLinked = (connectionType) =>
  ({
    [AWS_ROOT_ACCOUNT]: false,
    [AWS_LINKED_ACCOUNT]: true
  }[connectionType]);

const renderConnectionTypeSpecificInputs = (connectionType) => {
  switch (connectionType) {
    case AWS_ROOT_ACCOUNT:
      return <AwsRootInputs />;
    case AWS_LINKED_ACCOUNT:
      return <AwsLinkedInputs />;
    case AZURE_SUBSCRIPTION:
      return <AzureSubscriptionInputs />;
    case KUBERNETES:
      return <KubernetesInputs />;
    case ALIBABA_ACCOUNT:
      return <AlibabaAccountInputs />;
    default:
      return null;
  }
};

const ConnectionTypeDescriptionTypography = ({ children, withBottomMargin }) => (
  <Typography style={{ marginBottom: withBottomMargin ? "1rem" : "" }}>{children}</Typography>
);

const getAwsParameters = (formData) => {
  const getConfigSchemeParameters = () =>
    formData.isFindReport
      ? {
          config_scheme: AWS_ROOT_CONNECT_CONFIG_SCHEMES.FIND_REPORT
        }
      : {
          bucket_name: formData.bucketName,
          bucket_prefix: formData.bucketPrefix,
          report_name: formData.reportName,
          config_scheme: formData.configScheme
        };
  return {
    name: formData.name,
    type: AWS_CNR,
    config: {
      access_key_id: formData[`${PREFIX_AWS_ROOT}_accessKeyId`],
      secret_access_key: formData[`${PREFIX_AWS_ROOT}_secretAccessKey`],
      linked: false,
      ...getConfigSchemeParameters()
    }
  };
};

const getAwsLinkedParameters = (formData) => ({
  name: formData.name,
  type: AWS_CNR,
  config: {
    access_key_id: formData[`${PREFIX_AWS_LINKED}_accessKeyId`],
    secret_access_key: formData[`${PREFIX_AWS_LINKED}_secretAccessKey`],
    linked: true
  }
});

const getAzureParameters = (formData) => ({
  name: formData.name,
  type: AZURE_CNR,
  config: {
    subscription_id: formData.subscriptionId,
    client_id: formData.clientId,
    tenant: formData.tenant,
    secret: formData.secret
  }
});

const getKubernetesParameters = (formData) => ({
  name: formData.name,
  type: KUBERNETES_CNR,
  config: {
    url: formData.url,
    port: Number(formData.port),
    password: formData.password || undefined,
    user: formData.user || undefined,
    cost_model: {}
  }
});

const getAlibabaParameters = (formData) => ({
  name: formData.name,
  type: ALIBABA_CNR,
  config: {
    access_key_id: formData[`${PREFIX_ALIBABA}_accessKeyId`],
    secret_access_key: formData[`${PREFIX_ALIBABA}_secretAccessKey`]
  }
});

const CONNECTION_TYPE_DESCRIPTION_MESSAGE_TYPE = Object.freeze({
  I_RISK: "iRisk",
  I_WANT: "iWant",
  TYPOGRAPHY: "typography"
});

const renderConnectionTypeDescription = (settings) =>
  settings.map(({ type, key, ...props }, index) => {
    if (type === CONNECTION_TYPE_DESCRIPTION_MESSAGE_TYPE.TYPOGRAPHY) {
      const { messageId, values } = props;
      return (
        <ConnectionTypeDescriptionTypography key={key} withBottomMargin={index !== settings.length - 1}>
          <FormattedMessage id={messageId} values={values} />
        </ConnectionTypeDescriptionTypography>
      );
    }
    return null;
  });

const renderConnectionTypeInfoMessage = ({ connectionType }) =>
  ({
    [AWS_ROOT_ACCOUNT]: renderConnectionTypeDescription([
      {
        type: CONNECTION_TYPE_DESCRIPTION_MESSAGE_TYPE.TYPOGRAPHY,
        key: "createAwsRootDocumentationReference",
        messageId: "createAwsRootDocumentationReference",
        values: {
          link: (chunks) => (
            <Link data-test-id="link_guide" href={DOCS_HYSTAX_AUTO_BILLING_AWS} target="_blank" rel="noopener">
              {chunks}
            </Link>
          ),
          strong: (chunks) => <strong>{chunks}</strong>
        }
      }
    ]),
    [AWS_LINKED_ACCOUNT]: renderConnectionTypeDescription([
      {
        type: CONNECTION_TYPE_DESCRIPTION_MESSAGE_TYPE.TYPOGRAPHY,
        key: "createAwsLinkedDocumentationReference1",
        messageId: "createAwsLinkedDocumentationReference1",
        values: {
          autoBillingAwsLink: (chunks) => (
            <Link data-test-id="link_guide" href={DOCS_HYSTAX_AUTO_BILLING_AWS} target="_blank" rel="noopener">
              {chunks}
            </Link>
          )
        }
      },
      {
        type: CONNECTION_TYPE_DESCRIPTION_MESSAGE_TYPE.TYPOGRAPHY,
        key: "createAwsLinkedDocumentationReference2",
        messageId: "createAwsLinkedDocumentationReference2",
        values: {
          extractLinkedReports: (
            <Link
              data-test-id="extract_linked_reports"
              href={GITHUB_HYSTAX_EXTRACT_LINKED_REPORTS}
              target="_blank"
              rel="noopener"
            >
              {GITHUB_HYSTAX_EXTRACT_LINKED_REPORTS}
            </Link>
          )
        }
      },
      {
        type: CONNECTION_TYPE_DESCRIPTION_MESSAGE_TYPE.TYPOGRAPHY,
        key: "createAwsLinkedDocumentationReference3",
        messageId: "createAwsLinkedDocumentationReference3",
        values: {
          discoverResourcesLink: (chunks) => (
            <Link data-test-id="link_iam_user" href={DOCS_HYSTAX_DISCOVER_RESOURCES} target="_blank" rel="noopener">
              {chunks}
            </Link>
          )
        }
      }
    ]),
    [AZURE_SUBSCRIPTION]: renderConnectionTypeDescription([
      {
        type: CONNECTION_TYPE_DESCRIPTION_MESSAGE_TYPE.TYPOGRAPHY,
        key: "createAzureSubscriptionDocumentationReference",
        messageId: "createAzureSubscriptionDocumentationReference",
        values: {
          link: (chunks) => (
            <Link data-test-id="link_guide" href={DOCS_HYSTAX_CONNECT_AZURE_ACCOUNT} target="_blank" rel="noopener">
              {chunks}
            </Link>
          ),
          strong: (chunks) => <strong>{chunks}</strong>
        }
      }
    ]),
    [KUBERNETES]: renderConnectionTypeDescription([
      {
        key: "createKubernetesDocumentationReference1",
        type: CONNECTION_TYPE_DESCRIPTION_MESSAGE_TYPE.TYPOGRAPHY,
        messageId: "createKubernetesDocumentationReference1"
      },
      {
        key: "createKubernetesDocumentationReference2",
        type: CONNECTION_TYPE_DESCRIPTION_MESSAGE_TYPE.TYPOGRAPHY,
        messageId: "createKubernetesDocumentationReference2"
      },
      {
        type: CONNECTION_TYPE_DESCRIPTION_MESSAGE_TYPE.TYPOGRAPHY,
        key: "createKubernetesDocumentationReference3",
        messageId: "createKubernetesDocumentationReference3",
        values: {
          kubernetesConnectGuide: (
            <Link data-test-id="link_guide" href={GITHUB_HYSTAX_K8S_COST_METRICS_COLLECTOR} target="_blank" rel="noopener">
              {GITHUB_HYSTAX_K8S_COST_METRICS_COLLECTOR}
            </Link>
          ),
          p: (chunks) => <p>{chunks}</p>
        }
      },
      {
        type: CONNECTION_TYPE_DESCRIPTION_MESSAGE_TYPE.TYPOGRAPHY,
        key: "createKubernetesDocumentationReference4",
        messageId: "createKubernetesDocumentationReference4"
      },
      {
        type: CONNECTION_TYPE_DESCRIPTION_MESSAGE_TYPE.TYPOGRAPHY,
        key: "createKubernetesDocumentationReference5",
        messageId: "createKubernetesDocumentationReference5"
      }
    ]),
    [ALIBABA_ACCOUNT]: renderConnectionTypeDescription([
      {
        type: CONNECTION_TYPE_DESCRIPTION_MESSAGE_TYPE.TYPOGRAPHY,
        key: "createAlibabaDocumentationReference",
        messageId: "createAlibabaDocumentationReference",
        values: {
          link: (chunks) => (
            <Link data-test-id="link_guide" href={DOCS_HYSTAX_CONNECT_ALIBABA_CLOUD} target="_blank" rel="noopener">
              {chunks}
            </Link>
          ),
          strong: (chunks) => <strong>{chunks}</strong>
        }
      }
    ])
  }[connectionType]);

const ConnectCloudAccountForm = ({ onSubmit, onCancel, isLoading, showCancel = true }) => {
  const intl = useIntl();
  const methods = useForm();

  const { type } = getQueryParams();

  const { isDemo } = useOrganizationInfo();

  const {
    register,
    handleSubmit,
    formState: { errors }
  } = methods;

  const [connectionType, setConnectionType] = useState(getCloudType(type) ? type : AWS_ROOT_ACCOUNT);

  const buttonsGroup = [
    {
      id: AWS_ROOT_ACCOUNT,
      messageId: AWS_ROOT_ACCOUNT,
      dataTestId: "btn_aws_root_account",
      action: () => {
        setConnectionType(AWS_ROOT_ACCOUNT);
        GAEvent({ category: GA_EVENT_CATEGORIES.DATA_SOURCE, action: "Switch", label: AWS_CNR });
      }
    },
    {
      id: AWS_LINKED_ACCOUNT,
      messageId: AWS_LINKED_ACCOUNT,
      dataTestId: "btn_aws_linked_account",
      action: () => {
        setConnectionType(AWS_LINKED_ACCOUNT);
        GAEvent({ category: GA_EVENT_CATEGORIES.DATA_SOURCE, action: "Switch", label: AWS_CNR });
      }
    },
    {
      id: AZURE_SUBSCRIPTION,
      messageId: AZURE_SUBSCRIPTION,
      dataTestId: "btn_azure_subscription",
      action: () => {
        setConnectionType(AZURE_SUBSCRIPTION);
        GAEvent({ category: GA_EVENT_CATEGORIES.DATA_SOURCE, action: "Switch", label: AZURE_CNR });
      }
    },
    {
      id: KUBERNETES,
      messageId: KUBERNETES,
      dataTestId: "btn_kubernetes",
      action: () => {
        setConnectionType(KUBERNETES);
        GAEvent({ category: GA_EVENT_CATEGORIES.DATA_SOURCE, action: "Switch", label: KUBERNETES_CNR });
      }
    },
    {
      id: ALIBABA_ACCOUNT,
      messageId: ALIBABA_ACCOUNT,
      dataTestId: "btn_alibaba_account",
      action: () => {
        setConnectionType(ALIBABA_ACCOUNT);
        GAEvent({ category: GA_EVENT_CATEGORIES.DATA_SOURCE, action: "Switch", label: ALIBABA_CNR });
      }
    }
  ];

  return (
    <FormProvider {...methods}>
      <form
        onSubmit={
          isDemo
            ? (e) => e.preventDefault()
            : handleSubmit((formData) => {
                const cloudType = getCloudType(connectionType);

                const getParameters = {
                  [AWS_CNR]: isLinked(connectionType) ? getAwsLinkedParameters : getAwsParameters,
                  [AZURE_CNR]: getAzureParameters,
                  [KUBERNETES_CNR]: getKubernetesParameters,
                  [ALIBABA_CNR]: getAlibabaParameters
                }[cloudType];

                onSubmit(getParameters(formData));
              })
        }
        noValidate
      >
        <Input
          required
          dataTestId="input_cloud_account_name"
          error={!!errors.name}
          helperText={errors.name && errors.name.message}
          label={<FormattedMessage id="name" />}
          {...register("name", {
            required: {
              value: true,
              message: intl.formatMessage({ id: "thisFieldIsRequired" })
            },
            maxLength: {
              value: MAX_LENGTH,
              message: intl.formatMessage(
                { id: "maxLength" },
                { inputName: intl.formatMessage({ id: "name" }), max: MAX_LENGTH }
              )
            }
          })}
        />
        <ButtonGroupInput
          labelText={<FormattedMessage id="connectionType" />}
          helperText={renderConnectionTypeInfoMessage({ connectionType })}
          typographyProps={{
            "data-test-id": "p_create_iam_user"
          }}
          buttons={buttonsGroup}
          activeButtonIndex={buttonsGroup.findIndex((button) => button.id === connectionType)}
          fullWidth
        />
        {renderConnectionTypeSpecificInputs(connectionType)}
        <FormButtonsWrapper justifyContent={!showCancel ? "center" : "left"}>
          <ButtonLoader
            dataTestId="btn_connect_cloud_account"
            loaderDataTestId="loading_btn_connect"
            messageId="connect"
            color="primary"
            variant="contained"
            disabled={isDemo}
            isLoading={isLoading}
            tooltip={{ show: isDemo, messageId: "notAvailableInLiveDemo" }}
            type="submit"
          />
          {showCancel && <Button dataTestId="btn_cancel_cloud_account" messageId="cancel" onClick={onCancel} />}
        </FormButtonsWrapper>
      </form>
    </FormProvider>
  );
};

ConnectCloudAccountForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
  showCancel: PropTypes.bool
};

export default ConnectCloudAccountForm;
