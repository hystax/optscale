import React from "react";
import { Typography } from "@mui/material";
import Link from "@mui/material/Link";
import { Stack } from "@mui/system";
import PropTypes from "prop-types";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import {
  AlibabaCredentials,
  ALIBABA_CREDENTIALS_FIELD_NAMES,
  AwsCredentials,
  AWS_CREDENTIALS_FIELD_NAMES,
  AzureCredentials,
  AZURE_CREDENTIALS_FIELD_NAMES,
  GcpCredentials,
  GCP_CREDENTIALS_FIELD_NAMES,
  KubernetesCredentials,
  KUBERNETES_CREDENTIALS_FIELD_NAMES
} from "components/DataSourceCredentialFields";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import {
  DOCS_HYSTAX_AUTO_BILLING_AWS,
  DOCS_HYSTAX_CONNECT_ALIBABA_CLOUD,
  DOCS_HYSTAX_CONNECT_AZURE_ACCOUNT,
  DOCS_HYSTAX_CONNECT_GCP_CLOUD,
  DOCS_HYSTAX_DISCOVER_RESOURCES,
  GITHUB_HYSTAX_K8S_COST_METRICS_COLLECTOR
} from "urls";
import { ALIBABA_CNR, AWS_CNR, AWS_ROOT_CONNECT_CONFIG_SCHEMES, AZURE_CNR, GCP_CNR, KUBERNETES_CNR } from "utils/constants";
import { readFileAsText } from "utils/files";
import { SPACING_1 } from "utils/layouts";

const Description = ({ type, config }) => {
  switch (type) {
    case AWS_CNR:
      return (
        <Typography gutterBottom>
          {config.linked ? (
            <FormattedMessage
              id="createAwsLinkedDocumentationReference3"
              values={{
                discoverResourcesLink: (chunks) => (
                  <Link data-test-id="link_iam_user" href={DOCS_HYSTAX_DISCOVER_RESOURCES} target="_blank" rel="noopener">
                    {chunks}
                  </Link>
                )
              }}
            />
          ) : (
            <FormattedMessage
              id="createAwsRootDocumentationReference"
              values={{
                link: (chunks) => (
                  <Link data-test-id="link_guide" href={DOCS_HYSTAX_AUTO_BILLING_AWS} target="_blank" rel="noopener">
                    {chunks}
                  </Link>
                ),
                strong: (chunks) => <strong>{chunks}</strong>
              }}
            />
          )}
        </Typography>
      );
    case AZURE_CNR:
      return (
        <Typography gutterBottom>
          <FormattedMessage
            id="createAzureSubscriptionDocumentationReference"
            values={{
              link: (chunks) => (
                <Link data-test-id="link_guide" href={DOCS_HYSTAX_CONNECT_AZURE_ACCOUNT} target="_blank" rel="noopener">
                  {chunks}
                </Link>
              ),
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </Typography>
      );
    case ALIBABA_CNR:
      return (
        <Typography gutterBottom>
          <FormattedMessage
            id="createAlibabaDocumentationReference"
            values={{
              link: (chunks) => (
                <Link data-test-id="link_guide" href={DOCS_HYSTAX_CONNECT_ALIBABA_CLOUD} target="_blank" rel="noopener">
                  {chunks}
                </Link>
              ),
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </Typography>
      );
    case KUBERNETES_CNR:
      return null;
    case GCP_CNR:
      return (
        <Typography gutterBottom>
          <FormattedMessage
            id="createGCPDocumentationReference"
            values={{
              link: (chunks) => (
                <Link data-test-id="link_guide" href={DOCS_HYSTAX_CONNECT_GCP_CLOUD} target="_blank" rel="noopener">
                  {chunks}
                </Link>
              ),
              strong: (chunks) => <strong>{chunks}</strong>,
              p: (chunks) => <p>{chunks}</p>
            }}
          />
        </Typography>
      );
    default:
      return null;
  }
};

const CredentialInputs = ({ type }) => {
  switch (type) {
    case AWS_CNR:
      return <AwsCredentials />;
    case AZURE_CNR:
      return <AzureCredentials hidden={[AZURE_CREDENTIALS_FIELD_NAMES.SUBSCRIPTION_ID]} />;
    case ALIBABA_CNR:
      return <AlibabaCredentials />;
    case KUBERNETES_CNR:
      return <KubernetesCredentials />;
    case GCP_CNR:
      return (
        <GcpCredentials
          hidden={[GCP_CREDENTIALS_FIELD_NAMES.BILLING_DATA_DATASET, GCP_CREDENTIALS_FIELD_NAMES.BILLING_DATA_TABLE]}
        />
      );
    default:
      return null;
  }
};

const UpdateCredentialsWarning = ({ type }) => {
  const renderUpdateWarning = () => (
    <InlineSeverityAlert
      sx={{
        width: "100%"
      }}
      messageId="updateDateSourceCredentialsWarning"
    />
  );

  switch (type) {
    case AWS_CNR:
      return renderUpdateWarning();
    case AZURE_CNR:
      return renderUpdateWarning();
    case ALIBABA_CNR:
      return renderUpdateWarning();
    case KUBERNETES_CNR:
      return (
        <InlineSeverityAlert
          sx={{
            width: "100%"
          }}
          messageId="k8sUpdateWarning"
          messageValues={{
            link: (chunks) => (
              <Link data-test-id="link_guide" href={GITHUB_HYSTAX_K8S_COST_METRICS_COLLECTOR} target="_blank" rel="noopener">
                {chunks}
              </Link>
            )
          }}
        />
      );
    case GCP_CNR:
      return <>{renderUpdateWarning()}</>;
    default:
      return null;
  }
};

const getConfig = (type, config) => {
  switch (type) {
    case AWS_CNR:
      return {
        getDefaultFormValues: () => ({
          [AWS_CREDENTIALS_FIELD_NAMES.ACCESS_KEY_ID]: config.access_key_id,
          [AWS_CREDENTIALS_FIELD_NAMES.SECRET_ACCESS_KEY]: ""
        }),
        parseFormDataToApiParams: (formData) => ({
          config: {
            access_key_id: formData[AWS_CREDENTIALS_FIELD_NAMES.ACCESS_KEY_ID],
            secret_access_key: formData[AWS_CREDENTIALS_FIELD_NAMES.SECRET_ACCESS_KEY],
            ...(config.linked
              ? {
                  linked: true
                }
              : {
                  config_scheme: AWS_ROOT_CONNECT_CONFIG_SCHEMES.BUCKET_ONLY,
                  bucket_name: config.bucket_name,
                  report_name: config.report_name,
                  bucket_prefix: config.bucket_prefix
                })
          }
        })
      };
    case AZURE_CNR:
      return {
        getDefaultFormValues: () => ({
          [AZURE_CREDENTIALS_FIELD_NAMES.SUBSCRIPTION_ID]: config.subscription_id,
          [[AZURE_CREDENTIALS_FIELD_NAMES.CLIENT_ID]]: config.client_id,
          [AZURE_CREDENTIALS_FIELD_NAMES.TENANT]: config.tenant,
          [AZURE_CREDENTIALS_FIELD_NAMES.SECRET]: ""
        }),
        parseFormDataToApiParams: (formData) => ({
          config: {
            subscription_id: formData[AZURE_CREDENTIALS_FIELD_NAMES.SUBSCRIPTION_ID],
            client_id: formData[AZURE_CREDENTIALS_FIELD_NAMES.CLIENT_ID],
            tenant: formData[AZURE_CREDENTIALS_FIELD_NAMES.TENANT],
            secret: formData[AZURE_CREDENTIALS_FIELD_NAMES.SECRET]
          }
        })
      };
    case ALIBABA_CNR:
      return {
        getDefaultFormValues: () => ({
          [ALIBABA_CREDENTIALS_FIELD_NAMES.ACCESS_KEY_ID]: config.access_key_id,
          [ALIBABA_CREDENTIALS_FIELD_NAMES.SECRET_ACCESS_KEY]: ""
        }),
        parseFormDataToApiParams: (formData) => ({
          config: {
            access_key_id: formData[ALIBABA_CREDENTIALS_FIELD_NAMES.ACCESS_KEY_ID],
            secret_access_key: formData[ALIBABA_CREDENTIALS_FIELD_NAMES.SECRET_ACCESS_KEY]
          }
        })
      };
    case KUBERNETES_CNR:
      return {
        getDefaultFormValues: () => ({
          [KUBERNETES_CREDENTIALS_FIELD_NAMES.USER]: config.user,
          [KUBERNETES_CREDENTIALS_FIELD_NAMES.PASSWORD]: ""
        }),
        parseFormDataToApiParams: (formData) => ({
          config: {
            password: formData[KUBERNETES_CREDENTIALS_FIELD_NAMES.PASSWORD] || undefined,
            user: formData[KUBERNETES_CREDENTIALS_FIELD_NAMES.USER] || undefined
          }
        })
      };
    case GCP_CNR:
      return {
        getDefaultFormValues: () => ({
          [GCP_CREDENTIALS_FIELD_NAMES.BILLING_DATA_DATASET]: config.billing_data.dataset_name,
          [GCP_CREDENTIALS_FIELD_NAMES.BILLING_DATA_TABLE]: config.billing_data.table_name,
          [GCP_CREDENTIALS_FIELD_NAMES.CREDENTIALS]: ""
        }),
        parseFormDataToApiParams: async (formData) => {
          // TODO: the form validates the file itself, not the content.
          // Try to do both to avoid parsing the string here.
          const credentials = await readFileAsText(formData[GCP_CREDENTIALS_FIELD_NAMES.CREDENTIALS]);

          return {
            config: {
              credentials: JSON.parse(credentials),
              billing_data: {
                dataset_name: formData[GCP_CREDENTIALS_FIELD_NAMES.BILLING_DATA_DATASET],
                table_name: formData[GCP_CREDENTIALS_FIELD_NAMES.BILLING_DATA_TABLE]
              }
            }
          };
        }
      };
    default:
      return {};
  }
};

const UpdateDataSourceCredentialsForm = ({ id, type, config, onSubmit, onCancel, isLoading = false }) => {
  const { getDefaultFormValues, parseFormDataToApiParams } = getConfig(type, config);

  const methods = useForm({
    defaultValues: getDefaultFormValues()
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form
        onSubmit={handleSubmit(async (formData) => {
          onSubmit(id, await parseFormDataToApiParams(formData));
        })}
        noValidate
      >
        <Stack spacing={SPACING_1}>
          <div>
            <Description type={type} config={config} />
            <CredentialInputs type={type} />
          </div>
          <div>
            <UpdateCredentialsWarning type={type} />
          </div>
        </Stack>
        <FormButtonsWrapper>
          <ButtonLoader
            dataTestId="btn_update_data_source_credentials"
            loaderDataTestId="loading_btn_update_data_source_credentials"
            messageId="save"
            color="primary"
            variant="contained"
            type="submit"
            isLoading={isLoading}
          />
          <Button dataTestId="btn_cancel_update_data_source_credentials" messageId="cancel" onClick={onCancel} />
        </FormButtonsWrapper>
      </form>
    </FormProvider>
  );
};

UpdateDataSourceCredentialsForm.propTypes = {
  id: PropTypes.string.isRequired,
  type: PropTypes.oneOf([AWS_CNR, AZURE_CNR, ALIBABA_CNR, KUBERNETES_CNR, GCP_CNR]).isRequired,
  config: PropTypes.object.isRequired,
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default UpdateDataSourceCredentialsForm;
