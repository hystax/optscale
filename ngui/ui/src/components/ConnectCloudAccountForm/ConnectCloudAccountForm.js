import React, { useState } from "react";
import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormProvider, Controller, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import {
  BillingReportBucketDescription,
  BillingReportBucketTitle,
  CloudName,
  FIELD_NAMES as NEBIUS_FIELD_NAMES,
  ReportBucketName,
  ReportBucketPathPrefix,
  ServiceAccountCredentialsDescription
} from "components/CluidilConfigFormElements";
import ConnectForm from "components/ConnectForm";
import {
  AlibabaCredentials,
  ALIBABA_CREDENTIALS_FIELD_NAMES,
  AwsCredentials,
  AWS_CREDENTIALS_FIELD_NAMES,
  AzureTenantCredentials,
  AZURE_TENANT_CREDENTIALS_FIELD_NAMES,
  AzureSubscriptionCredentials,
  AZURE_SUBSCRIPTION_CREDENTIALS_FIELD_NAMES,
  NebiusCredentials,
  GcpCredentials,
  GCP_CREDENTIALS_FIELD_NAMES,
  KubernetesCredentials,
  KUBERNETES_CREDENTIALS_FIELD_NAMES,
  DATABRICKS_CREDENTIALS_FIELD_NAMES,
  DatabricksCredentials
} from "components/DataSourceCredentialFields";
import { DataSourceNameField, DATA_SOURCE_NAME_FIELD_NAME } from "components/DataSourceNameField";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import Input from "components/Input";
import QuestionMark from "components/QuestionMark";
import RadioGroupField from "components/RadioGroupField";
import SwitchField from "components/SwitchField";
import { useBoundingClientRect } from "hooks/useBoundingClientRect";
import { useIsDataSourceTypeConnectionEnabled } from "hooks/useIsDataSourceTypeConnectionEnabled";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import AlibabaLogoIcon from "icons/AlibabaLogoIcon";
import AwsLogoIcon from "icons/AwsLogoIcon";
import AzureLogoIcon from "icons/AzureLogoIcon";
import DatabricksLogoIcon from "icons/DatabricksLogoIcon";
import GcpLogoIcon from "icons/GcpLogoIcon";
import K8sLogoIcon from "icons/K8sLogoIcon";
import NebiusLogoIcon from "icons/NebiusLogoIcon";
import { intl } from "translations/react-intl-config";
import {
  DOCS_HYSTAX_AUTO_BILLING_AWS,
  DOCS_HYSTAX_CONNECT_AZURE_ACCOUNT,
  DOCS_HYSTAX_DISCOVER_RESOURCES,
  GITHUB_HYSTAX_K8S_COST_METRICS_COLLECTOR,
  GITHUB_HYSTAX_EXTRACT_LINKED_REPORTS,
  DOCS_HYSTAX_CONNECT_ALIBABA_CLOUD,
  DOCS_HYSTAX_CONNECT_GCP_CLOUD,
  DATABRICKS_CREATE_SERVICE_PRINCIPAL
} from "urls";
import { trackEvent, GA_EVENT_CATEGORIES } from "utils/analytics";
import {
  AWS_CNR,
  AZURE_CNR,
  AZURE_TENANT,
  KUBERNETES_CNR,
  AWS_ROOT_CONNECT_CONFIG_SCHEMES,
  ALIBABA_CNR,
  AWS_ROOT_ACCOUNT,
  AWS_LINKED_ACCOUNT,
  AZURE_SUBSCRIPTION,
  AZURE_TENANT_ACCOUNT,
  KUBERNETES,
  ALIBABA_ACCOUNT,
  GCP_CNR,
  GCP_ACCOUNT,
  DEFAULT_MAX_INPUT_LENGTH,
  NEBIUS_ACCOUNT,
  NEBIUS,
  DATABRICKS,
  DATABRICKS_ACCOUNT
} from "utils/constants";
import { readFileAsText } from "utils/files";
import { SPACING_2 } from "utils/layouts";
import { getQueryParams } from "utils/network";
import useStyles from "./ConnectCloudAccountForm.styles";

const BUCKET_NAME = "bucketName";
const BUCKET_PREFIX = "bucketPrefix";
const REPORT_NAME = "reportName";
const IS_FIND_REPORT = "isFindReport";
const DEFAULT_PATH_PREFIX = "reports";
const CONFIG_SCHEME = "configScheme";

const TILE_DIMENSION = 110;

const AwsRootInputs = () => (
  <ConnectForm>
    {({ register, formState: { errors }, control, watch }) => {
      const isFindReportWatch = watch(IS_FIND_REPORT, true);
      const configScheme =
        watch(CONFIG_SCHEME, AWS_ROOT_CONNECT_CONFIG_SCHEMES.CREATE_REPORT) || AWS_ROOT_CONNECT_CONFIG_SCHEMES.CREATE_REPORT;
      return (
        <>
          <AwsCredentials />
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
                    value: DEFAULT_MAX_INPUT_LENGTH,
                    message: intl.formatMessage(
                      { id: "maxLength" },
                      { inputName: intl.formatMessage({ id: "reportName" }), max: DEFAULT_MAX_INPUT_LENGTH }
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
                    value: DEFAULT_MAX_INPUT_LENGTH,
                    message: intl.formatMessage(
                      { id: "maxLength" },
                      { inputName: intl.formatMessage({ id: "reportS3BucketName" }), max: DEFAULT_MAX_INPUT_LENGTH }
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
                    value: DEFAULT_MAX_INPUT_LENGTH,
                    message: intl.formatMessage(
                      { id: "maxLength" },
                      { inputName: intl.formatMessage({ id: "reportPathPrefix" }), max: DEFAULT_MAX_INPUT_LENGTH }
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

const NebiusInputs = () => (
  <>
    <CloudName />
    <Box mt={1} mb={1}>
      <ServiceAccountCredentialsDescription />
    </Box>
    <NebiusCredentials />
    <BillingReportBucketTitle />
    <Box mt={1} mb={1}>
      <BillingReportBucketDescription />
    </Box>
    <ReportBucketName />
    <ReportBucketPathPrefix />
  </>
);

const getCloudType = (connectionType) =>
  ({
    [AWS_ROOT_ACCOUNT]: AWS_CNR,
    [AWS_LINKED_ACCOUNT]: AWS_CNR,
    [AZURE_SUBSCRIPTION]: AZURE_CNR,
    [AZURE_TENANT_ACCOUNT]: AZURE_TENANT,
    [ALIBABA_ACCOUNT]: ALIBABA_CNR,
    [GCP_ACCOUNT]: GCP_CNR,
    [NEBIUS_ACCOUNT]: NEBIUS,
    [DATABRICKS_ACCOUNT]: DATABRICKS,
    [KUBERNETES]: KUBERNETES_CNR
  }[connectionType]);

const isLinked = (connectionType) =>
  ({
    [AWS_ROOT_ACCOUNT]: false,
    [AWS_LINKED_ACCOUNT]: true
  }[connectionType]);

const ConnectionInputs = ({ connectionType }) => {
  switch (connectionType) {
    case AWS_ROOT_ACCOUNT:
      return <AwsRootInputs />;
    case AWS_LINKED_ACCOUNT:
      return <AwsCredentials />;
    case AZURE_TENANT_ACCOUNT:
      return <AzureTenantCredentials />;
    case AZURE_SUBSCRIPTION:
      return <AzureSubscriptionCredentials />;
    case ALIBABA_ACCOUNT:
      return <AlibabaCredentials />;
    case GCP_ACCOUNT:
      return <GcpCredentials />;
    case NEBIUS_ACCOUNT:
      return <NebiusInputs />;
    case DATABRICKS_ACCOUNT:
      return <DatabricksCredentials />;
    case KUBERNETES:
      return <KubernetesCredentials />;
    default:
      return null;
  }
};

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
      access_key_id: formData[AWS_CREDENTIALS_FIELD_NAMES.ACCESS_KEY_ID],
      secret_access_key: formData[AWS_CREDENTIALS_FIELD_NAMES.SECRET_ACCESS_KEY],
      linked: false,
      ...getConfigSchemeParameters()
    }
  };
};

const getAwsLinkedParameters = (formData) => ({
  name: formData[DATA_SOURCE_NAME_FIELD_NAME],
  type: AWS_CNR,
  config: {
    access_key_id: formData[AWS_CREDENTIALS_FIELD_NAMES.ACCESS_KEY_ID],
    secret_access_key: formData[AWS_CREDENTIALS_FIELD_NAMES.SECRET_ACCESS_KEY],
    linked: true
  }
});

const getAzureTenantParameters = (formData) => ({
  name: formData[DATA_SOURCE_NAME_FIELD_NAME],
  type: AZURE_TENANT,
  config: {
    client_id: formData[AZURE_TENANT_CREDENTIALS_FIELD_NAMES.CLIENT_ID],
    tenant: formData[AZURE_TENANT_CREDENTIALS_FIELD_NAMES.TENANT],
    secret: formData[AZURE_TENANT_CREDENTIALS_FIELD_NAMES.SECRET]
  }
});

const getAzureSubscriptionParameters = (formData) => ({
  name: formData[DATA_SOURCE_NAME_FIELD_NAME],
  type: AZURE_CNR,
  config: {
    subscription_id: formData[AZURE_SUBSCRIPTION_CREDENTIALS_FIELD_NAMES.SUBSCRIPTION_ID],
    client_id: formData[AZURE_SUBSCRIPTION_CREDENTIALS_FIELD_NAMES.CLIENT_ID],
    tenant: formData[AZURE_SUBSCRIPTION_CREDENTIALS_FIELD_NAMES.TENANT],
    secret: formData[AZURE_SUBSCRIPTION_CREDENTIALS_FIELD_NAMES.SECRET]
  }
});

const getKubernetesParameters = (formData) => ({
  name: formData[DATA_SOURCE_NAME_FIELD_NAME],
  type: KUBERNETES_CNR,
  config: {
    password: formData[KUBERNETES_CREDENTIALS_FIELD_NAMES.PASSWORD] || undefined,
    user: formData[KUBERNETES_CREDENTIALS_FIELD_NAMES.USER] || undefined,
    cost_model: {}
  }
});

const getAlibabaParameters = (formData) => ({
  name: formData[DATA_SOURCE_NAME_FIELD_NAME],
  type: ALIBABA_CNR,
  config: {
    access_key_id: formData[ALIBABA_CREDENTIALS_FIELD_NAMES.ACCESS_KEY_ID],
    secret_access_key: formData[ALIBABA_CREDENTIALS_FIELD_NAMES.SECRET_ACCESS_KEY]
  }
});

const getGoogleParameters = async (formData) => {
  const credentials = await readFileAsText(formData[GCP_CREDENTIALS_FIELD_NAMES.CREDENTIALS]);

  return {
    name: formData[DATA_SOURCE_NAME_FIELD_NAME],
    type: GCP_CNR,
    config: {
      credentials: JSON.parse(credentials),
      billing_data: {
        dataset_name: formData[GCP_CREDENTIALS_FIELD_NAMES.BILLING_DATA_DATASET],
        table_name: formData[GCP_CREDENTIALS_FIELD_NAMES.BILLING_DATA_TABLE]
      }
    }
  };
};

const getNebiusParameters = (formData) => ({
  name: formData[DATA_SOURCE_NAME_FIELD_NAME],
  type: NEBIUS,
  config: {
    // name of a cloud in Nebius console
    cloud_name: formData[NEBIUS_FIELD_NAMES.CLOUD_NAME],
    // id of a service account
    service_account_id: formData[NEBIUS_FIELD_NAMES.SERVICE_ACCOUNT_ID],
    // authorized key
    key_id: formData[NEBIUS_FIELD_NAMES.KEY_ID],
    private_key: formData[NEBIUS_FIELD_NAMES.PRIVATE_KEY],
    // access key
    access_key_id: formData[NEBIUS_FIELD_NAMES.ACCESS_KEY_ID],
    secret_access_key: formData[NEBIUS_FIELD_NAMES.SECRET_ACCESS_KEY],
    // bucket where report files are located
    bucket_name: formData[NEBIUS_FIELD_NAMES.BUCKET_NAME],
    bucket_prefix: formData[NEBIUS_FIELD_NAMES.BUCKET_PREFIX]
  }
});

const getDatabricksParameters = (formData) => ({
  name: formData[DATA_SOURCE_NAME_FIELD_NAME],
  type: DATABRICKS,
  config: {
    account_id: formData[DATABRICKS_CREDENTIALS_FIELD_NAMES.ACCOUNT_ID],
    client_id: formData[DATABRICKS_CREDENTIALS_FIELD_NAMES.CLIENT_ID],
    client_secret: formData[DATABRICKS_CREDENTIALS_FIELD_NAMES.CLIENT_SECRET],
    cost_model: {}
  }
});

const renderConnectionTypeDescription = (settings) =>
  settings.map(({ key, messageId, values }, index) => (
    <Typography key={key} style={{ marginBottom: index !== settings.length - 1 ? "1rem" : "" }}>
      <FormattedMessage id={messageId} values={values} />
    </Typography>
  ));

const renderConnectionTypeInfoMessage = ({ connectionType }) =>
  ({
    [AWS_ROOT_ACCOUNT]: renderConnectionTypeDescription([
      {
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
    [AZURE_TENANT_ACCOUNT]: renderConnectionTypeDescription([
      {
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
    [AZURE_SUBSCRIPTION]: renderConnectionTypeDescription([
      {
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
        messageId: "createKubernetesDocumentationReference1"
      },
      {
        key: "createKubernetesDocumentationReference2",
        messageId: "createKubernetesDocumentationReference2"
      },
      {
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
      }
    ]),
    [ALIBABA_ACCOUNT]: renderConnectionTypeDescription([
      {
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
    ]),
    [DATABRICKS_ACCOUNT]: renderConnectionTypeDescription([
      {
        key: "createDatabricksDocumentationReference",
        messageId: "createDatabricksDocumentationReference",
        values: {
          link: (chunks) => (
            <Link data-test-id="link_guide" href={DATABRICKS_CREATE_SERVICE_PRINCIPAL} target="_blank" rel="noopener">
              {chunks}
            </Link>
          ),
          strong: (chunks) => <strong>{chunks}</strong>
        }
      }
    ]),
    [GCP_ACCOUNT]: renderConnectionTypeDescription([
      {
        key: "createGCPDocumentationReference",
        messageId: "createGCPDocumentationReference",
        values: {
          link: (chunks) => (
            <Link data-test-id="link_guide" href={DOCS_HYSTAX_CONNECT_GCP_CLOUD} target="_blank" rel="noopener">
              {chunks}
            </Link>
          ),
          strong: (chunks) => <strong>{chunks}</strong>,
          p: (chunks) => <p>{chunks}</p>
        }
      }
    ])
  }[connectionType]);

const ConnectCloudAccountForm = ({ onSubmit, onCancel, isLoading, showCancel = true }) => {
  const methods = useForm();

  const [{ width }, ref] = useBoundingClientRect();

  const { type } = getQueryParams();

  const { isDemo } = useOrganizationInfo();

  const { handleSubmit } = methods;

  const isDataSourceTypeConnectionEnabled = useIsDataSourceTypeConnectionEnabled();

  const [connectionType, setConnectionType] = useState(() =>
    getCloudType(type) && isDataSourceTypeConnectionEnabled(type) ? type : AWS_ROOT_ACCOUNT
  );

  const { classes, cx } = useStyles();

  const defaultTileAction = (id, label) => {
    setConnectionType(id);
    trackEvent({ category: GA_EVENT_CATEGORIES.DATA_SOURCE, action: "Switch", label });
  };

  const tiles = [
    {
      id: AWS_ROOT_ACCOUNT,
      icon: AwsLogoIcon,
      messageId: AWS_ROOT_ACCOUNT,
      dataTestId: "btn_aws_root_account",
      action: () => defaultTileAction(AWS_ROOT_ACCOUNT, AWS_CNR, [IS_FIND_REPORT])
    },
    {
      id: AWS_LINKED_ACCOUNT,
      icon: AwsLogoIcon,
      messageId: AWS_LINKED_ACCOUNT,
      dataTestId: "btn_aws_linked_account",
      action: () => defaultTileAction(AWS_LINKED_ACCOUNT, AWS_CNR, [])
    },
    {
      id: AZURE_TENANT_ACCOUNT,
      icon: AzureLogoIcon,
      messageId: AZURE_TENANT_ACCOUNT,
      dataTestId: "btn_azure_tenant",
      action: () => defaultTileAction(AZURE_TENANT_ACCOUNT, AZURE_TENANT)
    },
    {
      id: AZURE_SUBSCRIPTION,
      icon: AzureLogoIcon,
      messageId: AZURE_SUBSCRIPTION,
      dataTestId: "btn_azure_subscription",
      action: () => defaultTileAction(AZURE_SUBSCRIPTION, AZURE_CNR)
    },
    {
      id: GCP_ACCOUNT,
      icon: GcpLogoIcon,
      messageId: GCP_ACCOUNT,
      dataTestId: "btn_gcp_account",
      action: () => defaultTileAction(GCP_ACCOUNT, GCP_CNR)
    },
    {
      id: ALIBABA_ACCOUNT,
      icon: AlibabaLogoIcon,
      messageId: ALIBABA_ACCOUNT,
      dataTestId: "btn_alibaba_account",
      action: () => defaultTileAction(ALIBABA_ACCOUNT, ALIBABA_CNR)
    },
    {
      id: NEBIUS_ACCOUNT,
      icon: NebiusLogoIcon,
      messageId: NEBIUS_ACCOUNT,
      dataTestId: "btn_nebius_account",
      action: () => defaultTileAction(NEBIUS_ACCOUNT, NEBIUS)
    },
    {
      id: DATABRICKS_ACCOUNT,
      icon: DatabricksLogoIcon,
      messageId: DATABRICKS_ACCOUNT,
      dataTestId: "btn_databricks_account",
      action: () => defaultTileAction(DATABRICKS_ACCOUNT, DATABRICKS)
    },
    {
      id: KUBERNETES,
      icon: K8sLogoIcon,
      messageId: KUBERNETES,
      dataTestId: "btn_kubernetes",
      action: () => defaultTileAction(KUBERNETES, KUBERNETES_CNR)
    }
  ].filter(({ id }) => isDataSourceTypeConnectionEnabled(id));

  return (
    <FormProvider {...methods}>
      <Stack>
        <div style={{ display: "flex", flexWrap: "wrap", width: "fit-content" }} ref={ref}>
          {tiles.map(({ id, icon: Icon, messageId, dataTestId, action }, index) => (
            <Paper
              key={id}
              className={cx(classes.tile, connectionType !== id && classes.inactiveTile)}
              variant="outlined"
              sx={(theme) => ({
                width: TILE_DIMENSION,
                height: TILE_DIMENSION,
                marginRight: index + 1 === tiles.length ? 0 : SPACING_2,
                display: "flex",
                marginBottom: SPACING_2,
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                fontSize: theme.typography.pxToRem(48),
                cursor: "pointer"
              })}
              onClick={action}
              data-test-id={dataTestId}
            >
              <Icon fontSize="inherit" />
              <Typography>
                <FormattedMessage id={messageId} />
              </Typography>
            </Paper>
          ))}
        </div>
        <Box sx={{ maxWidth: width }}>
          <Box sx={{ marginBottom: SPACING_2 }}>{renderConnectionTypeInfoMessage({ connectionType })}</Box>
          <form
            onSubmit={
              isDemo
                ? (e) => e.preventDefault()
                : handleSubmit(async (formData) => {
                    const cloudType = getCloudType(connectionType);

                    const getParameters = {
                      [AWS_CNR]: isLinked(connectionType) ? getAwsLinkedParameters : getAwsParameters,
                      [AZURE_TENANT]: getAzureTenantParameters,
                      [AZURE_CNR]: getAzureSubscriptionParameters,
                      [GCP_CNR]: getGoogleParameters,
                      [ALIBABA_CNR]: getAlibabaParameters,
                      [NEBIUS]: getNebiusParameters,
                      [KUBERNETES_CNR]: getKubernetesParameters,
                      [DATABRICKS]: getDatabricksParameters
                    }[cloudType];

                    onSubmit(await getParameters(formData));
                  })
            }
            noValidate
          >
            <DataSourceNameField />
            <ConnectionInputs connectionType={connectionType} />
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
        </Box>
      </Stack>
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
