import { useEffect, useState } from "react";
import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import ButtonGroup from "components/ButtonGroup/ButtonGroup";
import ButtonLoader from "components/ButtonLoader";
import CapabilityWrapper from "components/CapabilityWrapper";
import {
  ALIBABA_CREDENTIALS_FIELD_NAMES,
  AZURE_TENANT_CREDENTIALS_FIELD_NAMES,
  AZURE_SUBSCRIPTION_CREDENTIALS_FIELD_NAMES,
  GCP_CREDENTIALS_FIELD_NAMES,
  GCP_TENANT_CREDENTIALS_FIELD_NAMES,
  KUBERNETES_CREDENTIALS_FIELD_NAMES,
  DATABRICKS_CREDENTIALS_FIELD_NAMES,
  AWS_ROOT_CREDENTIALS_FIELD_NAMES,
  AWS_BILLING_BUCKET_FIELD_NAMES,
  AWS_EXPORT_TYPE_FIELD_NAMES,
  AWS_LINKED_CREDENTIALS_FIELD_NAMES,
  AWS_USE_AWS_EDP_DISCOUNT_FIELD_NAMES,
  AWS_ROLE_CREDENTIALS_FIELD_NAMES
} from "components/DataSourceCredentialFields";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { FIELD_NAMES as NEBIUS_FIELD_NAMES } from "components/NebiusConfigFormElements";
import { useIsDataSourceConnectionTypeEnabled } from "hooks/useIsDataSourceConnectionTypeEnabled";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import AlibabaLogoIcon from "icons/AlibabaLogoIcon";
import AwsLogoIcon from "icons/AwsLogoIcon";
import AzureLogoIcon from "icons/AzureLogoIcon";
import DatabricksLogoIcon from "icons/DatabricksLogoIcon";
import GcpLogoIcon from "icons/GcpLogoIcon";
import K8sLogoIcon from "icons/K8sLogoIcon";
import NebiusLogoIcon from "icons/NebiusLogoIcon";
import { intl } from "translations/react-intl-config";
import {
  DOCS_HYSTAX_CONNECT_AWS_ROOT,
  DOCS_HYSTAX_CONNECT_AZURE_TENANT,
  DOCS_HYSTAX_AWS_LINKED_DISCOVER_RESOURCES,
  GITHUB_HYSTAX_K8S_COST_METRICS_COLLECTOR,
  GITHUB_HYSTAX_EXTRACT_LINKED_REPORTS,
  DOCS_HYSTAX_CONNECT_ALIBABA_CLOUD,
  DOCS_HYSTAX_CONNECT_GOOGLE_CLOUD,
  DATABRICKS_CREATE_SERVICE_PRINCIPAL,
  DOCS_HYSTAX_CONNECT_KUBERNETES,
  DOCS_HYSTAX_CONNECT_AWS_LINKED,
  DOCS_HYSTAX_CONNECT_AZURE_SUBSCRIPTION,
  DOCS_HYSTAX_CONNECT_GOOGLE_CLOUD_TENANT
} from "urls";
import { trackEvent, GA_EVENT_CATEGORIES } from "utils/analytics";
import {
  AWS_CNR,
  AZURE_CNR,
  AZURE_TENANT,
  KUBERNETES_CNR,
  AWS_ROOT_CONNECT_CONFIG_SCHEMES,
  ALIBABA_CNR,
  GCP_CNR,
  NEBIUS,
  DATABRICKS,
  OPTSCALE_CAPABILITY,
  GCP_TENANT,
  CONNECTION_TYPES,
  CLOUD_PROVIDERS
} from "utils/constants";
import { readFileAsText } from "utils/files";
import { SPACING_2 } from "utils/layouts";
import { getSearchParams } from "utils/network";
import { ObjectValues } from "utils/types";
import useStyles from "./ConnectCloudAccountForm.styles";
import { ConnectionInputs, DataSourceNameField } from "./FormElements";
import { AWS_ROOT_INPUTS_FIELD_NAMES } from "./FormElements/ConnectionFields";
import { FIELD_NAME as DATA_SOURCE_NAME_FIELD_NAME } from "./FormElements/DataSourceNameField";

type ConnectionType = ObjectValues<typeof CONNECTION_TYPES>;

type CloudProvider = ObjectValues<typeof CLOUD_PROVIDERS>;

type CloudType =
  | typeof AWS_CNR
  | typeof AZURE_TENANT
  | typeof AZURE_CNR
  | typeof GCP_TENANT
  | typeof GCP_CNR
  | typeof ALIBABA_CNR
  | typeof NEBIUS
  | typeof DATABRICKS
  | typeof KUBERNETES_CNR;

type CloudProviderTypes = Record<
  CloudProvider,
  | {
      connectionType: ConnectionType;
      messageId: string;
      cloudType: CloudType;
    }[]
  | {
      connectionType: ConnectionType;
      cloudType: CloudType;
    }
>;

const CLOUD_PROVIDER_TYPES: CloudProviderTypes = {
  [CLOUD_PROVIDERS.AWS]: [
    { connectionType: CONNECTION_TYPES.AWS_ROLE, messageId: "assumedRole", cloudType: AWS_CNR },
    { connectionType: CONNECTION_TYPES.AWS_ROOT, messageId: "root", cloudType: AWS_CNR },
    { connectionType: CONNECTION_TYPES.AWS_LINKED, messageId: "linked", cloudType: AWS_CNR }
  ],
  [CLOUD_PROVIDERS.AZURE]: [
    { connectionType: CONNECTION_TYPES.AZURE_TENANT, messageId: "tenant", cloudType: AZURE_TENANT },
    { connectionType: CONNECTION_TYPES.AZURE_SUBSCRIPTION, messageId: "subscription", cloudType: AZURE_CNR }
  ],
  [CLOUD_PROVIDERS.GCP]: [
    { connectionType: CONNECTION_TYPES.GCP_TENANT, messageId: "tenant", cloudType: GCP_TENANT },
    { connectionType: CONNECTION_TYPES.GCP_PROJECT, messageId: "project", cloudType: GCP_CNR }
  ],
  [CLOUD_PROVIDERS.ALIBABA]: { connectionType: CONNECTION_TYPES.ALIBABA, cloudType: ALIBABA_CNR },
  [CLOUD_PROVIDERS.NEBIUS]: { connectionType: CONNECTION_TYPES.NEBIUS, cloudType: NEBIUS },
  [CLOUD_PROVIDERS.DATABRICKS]: { connectionType: CONNECTION_TYPES.DATABRICKS, cloudType: DATABRICKS },
  [CLOUD_PROVIDERS.KUBERNETES]: { connectionType: CONNECTION_TYPES.KUBERNETES, cloudType: KUBERNETES_CNR }
};

const getCloudProviderFromConnectionType = (connectionType: ConnectionType): CloudProvider => {
  const providerEntry = Object.entries(CLOUD_PROVIDER_TYPES).find(([, connectionTypes]) =>
    Array.isArray(connectionTypes)
      ? connectionTypes.some((type) => type.connectionType === connectionType)
      : connectionTypes.connectionType === connectionType
  );

  return providerEntry?.[0] as CloudProvider;
};

const getCloudTypeFromConnectionType = (connectionType: ConnectionType): CloudType => {
  const provider = getCloudProviderFromConnectionType(connectionType);

  const providerTypes = CLOUD_PROVIDER_TYPES[provider];

  if (Array.isArray(providerTypes)) {
    const type = providerTypes.find((type) => type.connectionType === connectionType) as { cloudType: CloudType };
    return type.cloudType;
  }

  return providerTypes.cloudType;
};

const getAwsRootParameters = (formData) => {
  const getConfigSchemeParameters = () =>
    formData.isFindReport
      ? {
          config_scheme: AWS_ROOT_CONNECT_CONFIG_SCHEMES.FIND_REPORT
        }
      : {
          bucket_name: formData[AWS_BILLING_BUCKET_FIELD_NAMES.BUCKET_NAME],
          bucket_prefix: formData[AWS_BILLING_BUCKET_FIELD_NAMES.BUCKET_PREFIX],
          report_name: formData[AWS_BILLING_BUCKET_FIELD_NAMES.EXPORT_NAME],
          region_name: formData[AWS_BILLING_BUCKET_FIELD_NAMES.REGION_NAME] || undefined,
          config_scheme: formData[AWS_ROOT_INPUTS_FIELD_NAMES.CONFIG_SCHEME]
        };
  return {
    name: formData[DATA_SOURCE_NAME_FIELD_NAME],
    type: AWS_CNR,
    config: {
      access_key_id: formData[AWS_ROOT_CREDENTIALS_FIELD_NAMES.ACCESS_KEY_ID],
      secret_access_key: formData[AWS_ROOT_CREDENTIALS_FIELD_NAMES.SECRET_ACCESS_KEY],
      use_edp_discount: formData[AWS_USE_AWS_EDP_DISCOUNT_FIELD_NAMES.USE_EDP_DISCOUNT],
      cur_version: Number(formData[AWS_EXPORT_TYPE_FIELD_NAMES.CUR_VERSION]),
      ...getConfigSchemeParameters()
    }
  };
};

const getAwsLinkedParameters = (formData) => ({
  name: formData[DATA_SOURCE_NAME_FIELD_NAME],
  type: AWS_CNR,
  config: {
    access_key_id: formData[AWS_LINKED_CREDENTIALS_FIELD_NAMES.ACCESS_KEY_ID],
    secret_access_key: formData[AWS_LINKED_CREDENTIALS_FIELD_NAMES.SECRET_ACCESS_KEY],
    linked: true
  }
});

const getAwsAssumedRoleParameters = (formData) => ({
  name: formData[DATA_SOURCE_NAME_FIELD_NAME],
  type: AWS_CNR,
  config: {
    assume_role_account_id: formData[AWS_ROLE_CREDENTIALS_FIELD_NAMES.ASSUME_ROLE_ACCOUNT_ID],
    assume_role_name: formData[AWS_ROLE_CREDENTIALS_FIELD_NAMES.ASSUME_ROLE_NAME],
    use_edp_discount: formData[AWS_USE_AWS_EDP_DISCOUNT_FIELD_NAMES.USE_EDP_DISCOUNT],
    cur_version: Number(formData[AWS_EXPORT_TYPE_FIELD_NAMES.CUR_VERSION]),
    bucket_name: formData[AWS_BILLING_BUCKET_FIELD_NAMES.BUCKET_NAME],
    bucket_prefix: formData[AWS_BILLING_BUCKET_FIELD_NAMES.BUCKET_PREFIX],
    report_name: formData[AWS_BILLING_BUCKET_FIELD_NAMES.EXPORT_NAME],
    region_name: formData[AWS_BILLING_BUCKET_FIELD_NAMES.REGION_NAME] || undefined,
    config_scheme: AWS_ROOT_CONNECT_CONFIG_SCHEMES.BUCKET_ONLY
  }
});

const getAwsParametersByConnectionType = (connectionType: string) => {
  const parameters = {
    [CONNECTION_TYPES.AWS_LINKED]: getAwsLinkedParameters,
    [CONNECTION_TYPES.AWS_ROLE]: getAwsAssumedRoleParameters
  }[connectionType];

  return parameters || getAwsRootParameters;
};

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
    secret: formData[AZURE_SUBSCRIPTION_CREDENTIALS_FIELD_NAMES.SECRET],
    ...(formData[AZURE_SUBSCRIPTION_CREDENTIALS_FIELD_NAMES.USE_BILLING_EXPORT]
      ? {
          export_name: formData[AZURE_SUBSCRIPTION_CREDENTIALS_FIELD_NAMES.EXPORT_NAME],
          sa_connection_string: formData[AZURE_SUBSCRIPTION_CREDENTIALS_FIELD_NAMES.STORAGE_ACCOUNT_CONNECTION_STRING],
          container: formData[AZURE_SUBSCRIPTION_CREDENTIALS_FIELD_NAMES.STORAGE_CONTAINER],
          directory: formData[AZURE_SUBSCRIPTION_CREDENTIALS_FIELD_NAMES.STORAGE_DIRECTORY]
        }
      : {})
  }
});

const getKubernetesParameters = (formData) => ({
  name: formData[DATA_SOURCE_NAME_FIELD_NAME],
  type: KUBERNETES_CNR,
  config: {
    password: formData[KUBERNETES_CREDENTIALS_FIELD_NAMES.PASSWORD] || undefined,
    user: formData[KUBERNETES_CREDENTIALS_FIELD_NAMES.USER] || undefined,
    custom_price: !formData[KUBERNETES_CREDENTIALS_FIELD_NAMES.USE_FLAVOR_BASED_COST_MODEL],
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
        table_name: formData[GCP_CREDENTIALS_FIELD_NAMES.BILLING_DATA_TABLE],
        project_id: formData[GCP_CREDENTIALS_FIELD_NAMES.BILLING_DATA_PROJECT_ID] || undefined
      },
      ...(formData[GCP_CREDENTIALS_FIELD_NAMES.AUTOMATICALLY_DETECT_PRICING_DATA]
        ? {}
        : {
            pricing_data: {
              dataset_name: formData[GCP_CREDENTIALS_FIELD_NAMES.PRICING_DATA_DATASET],
              table_name: formData[GCP_CREDENTIALS_FIELD_NAMES.PRICING_DATA_TABLE],
              project_id: formData[GCP_CREDENTIALS_FIELD_NAMES.PRICING_DATA_PROJECT_ID] || undefined
            }
          })
    }
  };
};

const getGoogleTenantParameters = async (formData) => {
  const credentials = await readFileAsText(formData[GCP_TENANT_CREDENTIALS_FIELD_NAMES.CREDENTIALS]);

  return {
    name: formData[DATA_SOURCE_NAME_FIELD_NAME],
    type: GCP_TENANT,
    config: {
      credentials: JSON.parse(credentials),
      billing_data: {
        dataset_name: formData[GCP_TENANT_CREDENTIALS_FIELD_NAMES.BILLING_DATA_DATASET],
        table_name: formData[GCP_TENANT_CREDENTIALS_FIELD_NAMES.BILLING_DATA_TABLE]
      },
      ...(formData[GCP_TENANT_CREDENTIALS_FIELD_NAMES.AUTOMATICALLY_DETECT_PRICING_DATA]
        ? {}
        : {
            pricing_data: {
              dataset_name: formData[GCP_TENANT_CREDENTIALS_FIELD_NAMES.PRICING_DATA_DATASET],
              table_name: formData[GCP_TENANT_CREDENTIALS_FIELD_NAMES.PRICING_DATA_TABLE]
            }
          })
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

const renderConnectionTypeInfoMessage = (connectionType: ConnectionType) =>
  ({
    [CONNECTION_TYPES.AWS_ROLE]: renderConnectionTypeDescription([
      {
        key: "createAwsAssumedRoleDescription",
        messageId: "createAwsAssumedRoleDescription",
        values: { action: intl.formatMessage({ id: "connect" }) }
      }
    ]),
    [CONNECTION_TYPES.AWS_ROOT]: renderConnectionTypeDescription([
      {
        key: "createAwsRootDocumentationReference",
        messageId: "createAwsRootDocumentationReference",
        values: {
          link: (chunks) => (
            <Link data-test-id="link_guide" href={DOCS_HYSTAX_CONNECT_AWS_ROOT} target="_blank" rel="noopener">
              {chunks}
            </Link>
          ),
          strong: (chunks) => <strong>{chunks}</strong>
        }
      }
    ]),
    [CONNECTION_TYPES.AWS_LINKED]: renderConnectionTypeDescription([
      {
        key: "createAwsLinkedDocumentationReference1",
        messageId: "createAwsLinkedDocumentationReference1",
        values: {
          autoBillingAwsLink: (chunks) => (
            <Link data-test-id="link_guide" href={DOCS_HYSTAX_CONNECT_AWS_LINKED} target="_blank" rel="noopener">
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
            <Link data-test-id="link_iam_user" href={DOCS_HYSTAX_AWS_LINKED_DISCOVER_RESOURCES} target="_blank" rel="noopener">
              {chunks}
            </Link>
          )
        }
      }
    ]),
    [CONNECTION_TYPES.AZURE_TENANT]: renderConnectionTypeDescription([
      {
        key: "createAzureSubscriptionDocumentationReference",
        messageId: "createAzureSubscriptionDocumentationReference",
        values: {
          link: (chunks) => (
            <Link data-test-id="link_guide" href={DOCS_HYSTAX_CONNECT_AZURE_TENANT} target="_blank" rel="noopener">
              {chunks}
            </Link>
          ),
          strong: (chunks) => <strong>{chunks}</strong>
        }
      }
    ]),
    [CONNECTION_TYPES.AZURE_SUBSCRIPTION]: renderConnectionTypeDescription([
      {
        key: "createAzureSubscriptionDocumentationReference",
        messageId: "createAzureSubscriptionDocumentationReference",
        values: {
          link: (chunks) => (
            <Link data-test-id="link_guide" href={DOCS_HYSTAX_CONNECT_AZURE_SUBSCRIPTION} target="_blank" rel="noopener">
              {chunks}
            </Link>
          ),
          strong: (chunks) => <strong>{chunks}</strong>
        }
      }
    ]),
    [CONNECTION_TYPES.KUBERNETES]: renderConnectionTypeDescription([
      {
        key: "createKubernetesDocumentationReference1",
        messageId: "createKubernetesDocumentationReference1",
        values: {
          link: (chunks) => (
            <Link data-test-id="link_guide" href={DOCS_HYSTAX_CONNECT_KUBERNETES} target="_blank" rel="noopener">
              {chunks}
            </Link>
          )
        }
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
    [CONNECTION_TYPES.ALIBABA]: renderConnectionTypeDescription([
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
    [CONNECTION_TYPES.DATABRICKS]: renderConnectionTypeDescription([
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
    [CONNECTION_TYPES.GCP_PROJECT]: renderConnectionTypeDescription([
      {
        key: "createGCPDocumentationReference",
        messageId: "createGCPDocumentationReference",
        values: {
          link: (chunks) => (
            <Link data-test-id="link_guide" href={DOCS_HYSTAX_CONNECT_GOOGLE_CLOUD} target="_blank" rel="noopener">
              {chunks}
            </Link>
          ),
          strong: (chunks) => <strong>{chunks}</strong>,
          p: (chunks) => <p>{chunks}</p>
        }
      }
    ]),
    [CONNECTION_TYPES.GCP_TENANT]: renderConnectionTypeDescription([
      {
        key: "createGCPTenantDocumentationReference1",
        messageId: "createGCPTenantDocumentationReference1"
      },
      {
        key: "createGCPTenantDocumentationReference2",
        messageId: "createGCPTenantDocumentationReference2",
        values: {
          link: (chunks) => (
            <Link data-test-id="link_guide" href={DOCS_HYSTAX_CONNECT_GOOGLE_CLOUD_TENANT} target="_blank" rel="noopener">
              {chunks}
            </Link>
          ),
          strong: (chunks) => <strong>{chunks}</strong>,
          p: (chunks) => <p>{chunks}</p>
        }
      }
    ]),
    [CONNECTION_TYPES.NEBIUS]: null
  })[connectionType];

const getConnectionTypeFromQueryParams = () => {
  const { type: connectionTypeQueryParameter } = getSearchParams();

  if (Object.values(CONNECTION_TYPES).includes(connectionTypeQueryParameter as ConnectionType)) {
    return connectionTypeQueryParameter as ConnectionType;
  }

  return undefined;
};

const trackConnectionTypeChangeEvent = (connectionType: ConnectionType) => {
  trackEvent({
    category: GA_EVENT_CATEGORIES.DATA_SOURCE,
    action: "Switch",
    label: getCloudTypeFromConnectionType(connectionType)
  });
};

const ConnectCloudAccountForm = ({ onSubmit, onCancel, isLoading = false, showCancel = true }) => {
  const methods = useForm();

  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  const { handleSubmit } = methods;

  const isDataSourceConnectionTypeEnabled = useIsDataSourceConnectionTypeEnabled();

  const [connectionType, setConnectionType] = useState<ConnectionType>(() => {
    const connectionTypeFromQueryParams = getConnectionTypeFromQueryParams();

    if (connectionTypeFromQueryParams && isDataSourceConnectionTypeEnabled(connectionTypeFromQueryParams)) {
      return connectionTypeFromQueryParams;
    }

    return CONNECTION_TYPES.AWS_ROLE;
  });

  const selectedProvider = getCloudProviderFromConnectionType(connectionType);

  const { classes, cx } = useStyles();

  useEffect(() => {
    trackConnectionTypeChangeEvent(connectionType);
  }, [connectionType]);

  const tiles = [
    {
      id: CLOUD_PROVIDERS.AWS,
      icon: AwsLogoIcon,
      messageId: "aws",
      dataTestId: "btn_aws_account",
      action: () => setConnectionType(CONNECTION_TYPES.AWS_ROLE)
    },
    {
      id: CLOUD_PROVIDERS.AZURE,
      icon: AzureLogoIcon,
      messageId: "azure",
      dataTestId: "btn_azure_account",
      action: () => setConnectionType(CONNECTION_TYPES.AZURE_TENANT)
    },
    {
      id: CLOUD_PROVIDERS.GCP,
      icon: GcpLogoIcon,
      messageId: "gcp",
      dataTestId: "btn_gcp_account",
      action: () => setConnectionType(CONNECTION_TYPES.GCP_TENANT)
    },
    {
      id: CLOUD_PROVIDERS.ALIBABA,
      icon: AlibabaLogoIcon,
      messageId: "alibaba",
      dataTestId: "btn_alibaba_account",
      action: () => setConnectionType(CONNECTION_TYPES.ALIBABA)
    },
    {
      id: CLOUD_PROVIDERS.NEBIUS,
      icon: NebiusLogoIcon,
      messageId: "nebius",
      dataTestId: "btn_nebius_account",
      action: () => setConnectionType(CONNECTION_TYPES.NEBIUS),
      capability: OPTSCALE_CAPABILITY.FINOPS
    },
    {
      id: CLOUD_PROVIDERS.DATABRICKS,
      icon: DatabricksLogoIcon,
      messageId: "databricks",
      dataTestId: "btn_databricks_account",
      action: () => setConnectionType(CONNECTION_TYPES.DATABRICKS),
      capability: OPTSCALE_CAPABILITY.FINOPS
    },
    {
      id: CLOUD_PROVIDERS.KUBERNETES,
      icon: K8sLogoIcon,
      messageId: "kubernetes",
      dataTestId: "btn_kubernetes_account",
      action: () => setConnectionType(CONNECTION_TYPES.KUBERNETES),
      capability: OPTSCALE_CAPABILITY.FINOPS
    }
  ].filter(({ id }) => {
    const providerTypes = CLOUD_PROVIDER_TYPES[id];

    return Array.isArray(providerTypes)
      ? providerTypes.some((subtype) => isDataSourceConnectionTypeEnabled(subtype.connectionType))
      : isDataSourceConnectionTypeEnabled(providerTypes.connectionType);
  });

  return (
    <FormProvider {...methods}>
      <Box sx={{ width: { md: "50%" } }}>
        <Box display="grid" gap={SPACING_2} mb={SPACING_2} gridTemplateColumns="repeat(auto-fit, minmax(100px, 1fr))">
          {tiles.map(({ id, icon: Icon, messageId, dataTestId, action, capability }) => (
            <CapabilityWrapper capability={capability} key={id}>
              <Paper
                key={id}
                className={cx(classes.tile, selectedProvider !== id && classes.inactiveTile)}
                variant="outlined"
                sx={{
                  height: 70,
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                  alignItems: "center",
                  cursor: "pointer"
                }}
                onClick={action}
                data-test-id={dataTestId}
              >
                <Icon fontSize="large" />
                <Typography noWrap>
                  <FormattedMessage id={messageId} />
                </Typography>
              </Paper>
            </CapabilityWrapper>
          ))}
        </Box>
        <Box>
          {Array.isArray(CLOUD_PROVIDER_TYPES[selectedProvider]) && (
            <Box alignItems="center" display="flex" mb={1}>
              <Typography sx={{ mr: 1 }}>
                <FormattedMessage id="connectionType" />{" "}
              </Typography>
              <ButtonGroup
                buttons={CLOUD_PROVIDER_TYPES[selectedProvider]
                  .filter((subtype) => isDataSourceConnectionTypeEnabled(subtype.connectionType))
                  .map((subtype) => ({
                    id: subtype.connectionType,
                    messageId: subtype.messageId,
                    action: () => setConnectionType(subtype.connectionType)
                  }))}
                activeButtonId={connectionType}
              />
            </Box>
          )}
          <Box sx={{ marginBottom: SPACING_2 }}>{renderConnectionTypeInfoMessage(connectionType)}</Box>
          <form
            onSubmit={
              isRestricted
                ? (e) => e.preventDefault()
                : handleSubmit(async (formData) => {
                    const cloudType = getCloudTypeFromConnectionType(connectionType);

                    const getParameters = {
                      [AWS_CNR]: getAwsParametersByConnectionType(connectionType),
                      [AZURE_TENANT]: getAzureTenantParameters,
                      [AZURE_CNR]: getAzureSubscriptionParameters,
                      [GCP_CNR]: getGoogleParameters,
                      [GCP_TENANT]: getGoogleTenantParameters,
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
                disabled={isRestricted}
                isLoading={isLoading}
                tooltip={{
                  show: isRestricted,
                  value: restrictionReasonMessage
                }}
                type="submit"
              />
              {showCancel && <Button dataTestId="btn_cancel_cloud_account" messageId="cancel" onClick={onCancel} />}
            </FormButtonsWrapper>
          </form>
        </Box>
      </Box>
    </FormProvider>
  );
};

export default ConnectCloudAccountForm;
