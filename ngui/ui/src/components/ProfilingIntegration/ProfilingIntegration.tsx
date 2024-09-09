import { useContext } from "react";
import { Box, Skeleton, Stack, Typography } from "@mui/material";
import Link from "@mui/material/Link";
import { FormattedMessage, useIntl } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CodeBlock from "components/CodeBlock";
import CopyText from "components/CopyText";
import HtmlSymbol from "components/HtmlSymbol";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import SubTitle from "components/SubTitle";
import { ProfilingIntegrationModalContext } from "contexts/ProfilingIntegrationModalContext";
import { ML_METRICS, ML_TASKS, PYPI_OPTSCALE_ARCEE, isProduction } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { SPACING_2 } from "utils/layouts";

type ProfilingIntegrationProps = {
  profilingToken: string;
  taskKey?: string;
  isLoading?: boolean;
};

type SectionTitleProps = {
  messageId: string;
};

type MethodParametersDescriptionProps = {
  parameterMessageIds: string[];
};

type MethodUsageProps = {
  method: string;
  example?: string;
};

type MethodDescriptionProps = {
  descriptionMessage: { id: string; values?: Record<string, unknown> };
  parameterMessageIds?: string[];
  method: string;
  example?: string;
};

const codeFormatMessageValues = {
  code: (chunks) => (
    <Box
      sx={(theme) => ({
        backgroundColor: theme.palette.background.default,
        display: "inline"
      })}
    >
      <samp>{chunks}</samp>
    </Box>
  )
};

const SectionTitle = ({ messageId }: SectionTitleProps) => (
  <SubTitle fontWeight="bold">
    <FormattedMessage id={messageId} />
  </SubTitle>
);

const MethodParametersDescription = ({ parameterMessageIds }: MethodParametersDescriptionProps) => (
  <ul>
    {parameterMessageIds.map((messageId) => (
      <li key={messageId}>
        <Typography>
          <FormattedMessage
            id={messageId}
            values={{
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </Typography>
      </li>
    ))}
  </ul>
);

const MethodUsage = ({ method, example }: MethodUsageProps) => {
  const hasExample = !!example;

  return (
    <>
      <Box mb={hasExample ? 1 : 0}>
        <CodeBlock text={method} />
      </Box>
      {hasExample && (
        <>
          <Typography gutterBottom>
            <FormattedMessage id="mlProfilingIntegration.common.example" />
            <HtmlSymbol symbol="colon" />
          </Typography>
          <Box>
            <CodeBlock text={example} />
          </Box>
        </>
      )}
    </>
  );
};

const MethodDescription = ({ descriptionMessage, parameterMessageIds = [], method, example }: MethodDescriptionProps) => (
  <>
    <Typography gutterBottom>
      <FormattedMessage id={descriptionMessage.id} values={{ ...codeFormatMessageValues, ...descriptionMessage.values }} />
      <HtmlSymbol symbol="colon" />
    </Typography>
    {isEmptyArray(parameterMessageIds) ? null : <MethodParametersDescription parameterMessageIds={parameterMessageIds} />}
    <MethodUsage method={method} example={example} />
  </>
);

const Installation = () => (
  <>
    <SectionTitle messageId="mlProfilingIntegration.installation.title" />
    <Typography gutterBottom>
      <FormattedMessage id="mlProfilingIntegration.installation.description" values={{ ...codeFormatMessageValues }} />
      <HtmlSymbol symbol="colon" />
    </Typography>
    <CodeBlock text="pip install optscale_arcee" />
  </>
);

const Import = () => (
  <>
    <SectionTitle messageId="mlProfilingIntegration.import.title" />
    <Typography gutterBottom>
      <FormattedMessage id="mlProfilingIntegration.import.description" values={{ ...codeFormatMessageValues }} />
      <HtmlSymbol symbol="colon" />
    </Typography>
    <CodeBlock text="import optscale_arcee as arcee" />
  </>
);

const Initialization = ({
  profilingToken,
  taskKey,
  isLoading = false
}: {
  profilingToken: string;
  taskKey?: string;
  isLoading?: boolean;
}) => {
  const intl = useIntl();

  const { onClose } = useContext(ProfilingIntegrationModalContext);
  const endpointUrlParameter = isProduction() ? "" : `, endpoint_url="https://${window.location.host}/arcee/v2"`;

  const arceeInitUsingContextManager = (
    <CodeBlock
      text={`with arcee.init("${profilingToken}", "${taskKey ?? "task_key"}"${endpointUrlParameter}):
    # ${intl.formatMessage({ id: "mlProfilingIntegration.common.someCode" })}`}
    />
  );
  const arceeInitUsingFunctionCall = (
    <CodeBlock
      text={`arcee.init("${profilingToken}", "${taskKey ?? "task_key"}"${endpointUrlParameter})
# ${intl.formatMessage({ id: "mlProfilingIntegration.common.someCode" })}
arcee.finish()
# ${intl.formatMessage({ id: "mlProfilingIntegration.common.orInCaseOfError" })}
arcee.error()
`}
    />
  );

  return (
    <>
      <SectionTitle messageId="mlProfilingIntegration.initialization.title" />
      <Box mb={1}>
        <Typography gutterBottom>
          <FormattedMessage id="mlProfilingIntegration.initialization.description" />
        </Typography>
        <ul>
          <li>
            {isLoading ? (
              <Skeleton />
            ) : (
              <KeyValueLabel
                keyMessageId="mlProfilingIntegration.initialization.profilingToken"
                value={<CopyText text={profilingToken}>{profilingToken}</CopyText>}
                isBoldValue={false}
              />
            )}
          </li>
          <li>
            <Typography>
              {taskKey ? (
                <KeyValueLabel
                  keyMessageId="mlProfilingIntegration.initialization.taskKey"
                  value={<CopyText text={taskKey}>{taskKey}</CopyText>}
                  isBoldValue={false}
                />
              ) : (
                <FormattedMessage
                  id="mlProfilingIntegration.initialization.taskKeyCanBeFound"
                  values={{
                    link: (chunks) => (
                      <Link
                        to={ML_TASKS}
                        // Explicitly close the modal to cover cases where it was opened on the "/tasks" page
                        onClick={onClose}
                        component={RouterLink}
                      >
                        {chunks}
                      </Link>
                    )
                  }}
                />
              )}
            </Typography>
          </li>
        </ul>
        <Typography gutterBottom>
          <FormattedMessage
            id="mlProfilingIntegration.initialization.initCollectorUsingContextManager"
            values={{
              br: <br />
            }}
          />
          <HtmlSymbol symbol="colon" />
        </Typography>
        {isLoading ? <Skeleton width="100%">{arceeInitUsingContextManager}</Skeleton> : arceeInitUsingContextManager}
        <Typography gutterBottom>
          <FormattedMessage
            id="mlProfilingIntegration.initialization.initCollectorUsingContextManagerDescription"
            values={{
              ...codeFormatMessageValues
            }}
          />
        </Typography>
      </Box>
      <Box mb={1}>
        <Typography gutterBottom>
          <FormattedMessage
            id="mlProfilingIntegration.initialization.alternativeInit"
            values={{
              ...codeFormatMessageValues
            }}
          />
        </Typography>
        {isLoading ? <Skeleton width="100%">{arceeInitUsingFunctionCall}</Skeleton> : arceeInitUsingFunctionCall}
      </Box>
      <Box mb={1}>
        <Typography gutterBottom>
          <FormattedMessage id="mlProfilingIntegration.initialization.customEndpointAdnSslChecks" />
          <HtmlSymbol symbol="colon" />
        </Typography>
        <CodeBlock
          text={`with arcee.init("${profilingToken}", "${
            taskKey ?? "task_key"
          }", endpoint_url="https://my.custom.endpoint:443/arcee/v2", ssl=False):
    # ${intl.formatMessage({ id: "mlProfilingIntegration.common.someCode" })}
`}
        />
      </Box>
      <Box>
        <Typography gutterBottom>
          <FormattedMessage id="mlProfilingIntegration.initialization.arceeDaemonProcess" />
          <HtmlSymbol symbol="colon" />
        </Typography>
        <CodeBlock
          text={`with arcee.init("${profilingToken}", "${taskKey ?? "task_key"}", period=5):
    # ${intl.formatMessage({ id: "mlProfilingIntegration.common.someCode" })}
`}
        />
      </Box>
    </>
  );
};

const SendingMetrics = () => (
  <>
    <SectionTitle messageId="mlProfilingIntegration.sendingMetrics.title" />
    <MethodDescription
      descriptionMessage={{
        id: "mlProfilingIntegration.sendingMetrics.description",
        values: {
          link: (chunks) => (
            <Link to={ML_METRICS} component={RouterLink}>
              {chunks}
            </Link>
          )
        }
      }}
      parameterMessageIds={["mlProfilingIntegration.sendingMetrics.parameters.1.data"]}
      method={`arcee.send({"metric_key_1": value_1, "metric_key_2": value_2})`}
      example={`arcee.send({ "accuracy": 71.44, "loss": 0.37 })`}
    />
  </>
);

const AddingHyperparameters = () => (
  <>
    <SectionTitle messageId="mlProfilingIntegration.addingHyperparameters.title" />{" "}
    <MethodDescription
      descriptionMessage={{
        id: "mlProfilingIntegration.addingHyperparameters.description",
        values: {
          link: (chunks) => (
            <Link to={ML_METRICS} component={RouterLink}>
              {chunks}
            </Link>
          )
        }
      }}
      parameterMessageIds={[
        "mlProfilingIntegration.addingHyperparameters.parameters.1.key",
        "mlProfilingIntegration.addingHyperparameters.parameters.2.value"
      ]}
      method={`arcee.hyperparam(key, value)`}
      example={`arcee.hyperparam("EPOCHS", 100)`}
    />
  </>
);

const TaggingTaskRun = () => (
  <>
    <SectionTitle messageId="mlProfilingIntegration.taggingTaskRun.title" />
    <MethodDescription
      descriptionMessage={{
        id: "mlProfilingIntegration.taggingTaskRun.description"
      }}
      parameterMessageIds={[
        "mlProfilingIntegration.taggingTaskRun.parameters.1.key",
        "mlProfilingIntegration.taggingTaskRun.parameters.2.value"
      ]}
      method={`arcee.tag(key, value)`}
      example={`arcee.tag("Algorithm", "Linear Learn Algorithm")`}
    />
  </>
);

const AddingMilestone = () => (
  <>
    <SectionTitle messageId="mlProfilingIntegration.addingMilestone.title" />
    <MethodDescription
      descriptionMessage={{
        id: "mlProfilingIntegration.addingMilestone.description"
      }}
      parameterMessageIds={["mlProfilingIntegration.addingMilestone.parameters.1.name"]}
      method={`arcee.milestone(name)`}
      example={`arcee.milestone("Download training data")`}
    />
  </>
);

const AddingStage = () => (
  <>
    <SectionTitle messageId={"mlProfilingIntegration.addingStage.title"} />
    <MethodDescription
      descriptionMessage={{
        id: "mlProfilingIntegration.addingStage.description"
      }}
      parameterMessageIds={["mlProfilingIntegration.addingStage.parameters.1.name"]}
      method={`arcee.stage(name)`}
      example={`arcee.stage("preparing")`}
    />
  </>
);

const LoggingDatasets = () => (
  <>
    <SectionTitle messageId="mlProfilingIntegration.loggingDatasets.title" />
    <MethodDescription
      descriptionMessage={{
        id: "mlProfilingIntegration.loggingDataset.description"
      }}
      parameterMessageIds={[
        "mlProfilingIntegration.loggingDataset.parameters.1.path",
        "mlProfilingIntegration.loggingDataset.parameters.2.name",
        "mlProfilingIntegration.loggingDataset.parameters.3.description",
        "mlProfilingIntegration.loggingDataset.parameters.4.labels"
      ]}
      method={`arcee.dataset(path, name, description, labels)`}
      example={`arcee.dataset("https://s3/ml-bucket/datasets/training_dataset.csv",
              name="Training dataset",
              description="Training dataset (100k rows)",
              labels=["training", "100k"])`}
    />
  </>
);

const CreatingModels = () => (
  <>
    <SectionTitle messageId="mlProfilingIntegration.creatingModels.title" />
    <MethodDescription
      descriptionMessage={{
        id: "mlProfilingIntegration.creatingModels.description"
      }}
      parameterMessageIds={[
        "mlProfilingIntegration.creatingModels.parameters.1.key",
        "mlProfilingIntegration.creatingModels.parameters.2.path"
      ]}
      method={`arcee.model(key, path)`}
      example={`arcee.model("my_model", "/home/user/my_model")`}
    />
  </>
);

const SettingModelVersion = () => (
  <>
    <SectionTitle messageId="mlProfilingIntegration.settingModelVersion.title" />
    <MethodDescription
      descriptionMessage={{
        id: "mlProfilingIntegration.settingModelVersion.description"
      }}
      parameterMessageIds={["mlProfilingIntegration.settingModelVersion.parameters.1.version"]}
      method={`arcee.model_version(version)`}
      example={`arcee.model_version("1.2.3-release")`}
    />
  </>
);

const SettingModelVersionAlias = () => (
  <>
    <SectionTitle messageId="mlProfilingIntegration.settingModelVersionAlias.title" />
    <MethodDescription
      descriptionMessage={{
        id: "mlProfilingIntegration.settingModelVersionAlias.description"
      }}
      parameterMessageIds={["mlProfilingIntegration.settingModelVersionAlias.parameters.1.alias"]}
      method={`arcee.model_version_alias(alias)`}
      example={`arcee.model_version_alias("winner")`}
    />
  </>
);

const SettingModelVersionTag = () => (
  <>
    <SectionTitle messageId="mlProfilingIntegration.settingModelVersionTag.title" />
    <MethodDescription
      descriptionMessage={{
        id: "mlProfilingIntegration.settingModelVersionTag.description"
      }}
      parameterMessageIds={[
        "mlProfilingIntegration.settingModelVersionTag.parameters.1.key",
        "mlProfilingIntegration.settingModelVersionTag.parameters.2.value"
      ]}
      method={`arcee.model_version_tag(key, value)`}
      example={`arcee.model_version_tag("env", "staging demo")`}
    />
  </>
);

const CreatingArtifacts = () => (
  <>
    <SectionTitle messageId="mlProfilingIntegration.creatingArtifacts.title" />
    <MethodDescription
      descriptionMessage={{
        id: "mlProfilingIntegration.creatingArtifacts.description"
      }}
      parameterMessageIds={[
        "mlProfilingIntegration.creatingArtifacts.parameters.1.path",
        "mlProfilingIntegration.creatingArtifacts.parameters.2.name",
        "mlProfilingIntegration.creatingArtifacts.parameters.3.description",
        "mlProfilingIntegration.creatingArtifacts.parameters.4.tags"
      ]}
      method={`arcee.artifact(path, name, description, tags)`}
      example={`arcee.artifact("https://s3/ml-bucket/artifacts/AccuracyChart.png",
               name="Accuracy line chart",
               description="The dependence of accuracy on the time",
               tags={"env": "staging"})`}
    />
  </>
);

const SettingArtifactTag = () => (
  <>
    <SectionTitle messageId="mlProfilingIntegration.settingArtifactTag.title" />
    <MethodDescription
      descriptionMessage={{
        id: "mlProfilingIntegration.settingArtifactTag.description"
      }}
      parameterMessageIds={[
        "mlProfilingIntegration.settingArtifactTag.parameters.1.path",
        "mlProfilingIntegration.settingArtifactTag.parameters.2.key",
        "mlProfilingIntegration.settingArtifactTag.parameters.3.value"
      ]}
      method={`arcee.artifact_tag(path, key, value)`}
      example={`arcee.artifact_tag("https://s3/ml-bucket/artifacts/AccuracyChart.png", 
                   "env", "staging demo")`}
    />
  </>
);

const FinishTaskRun = () => (
  <>
    <SectionTitle messageId="mlProfilingIntegration.finishTaskRun.title" />
    <MethodDescription
      descriptionMessage={{
        id: "mlProfilingIntegration.finishTaskRun.description"
      }}
      method={`arcee.finish()`}
    />
  </>
);

const FailTaskRun = () => (
  <>
    <SectionTitle messageId="mlProfilingIntegration.failTaskRun.title" />
    <MethodDescription
      descriptionMessage={{
        id: "mlProfilingIntegration.failTaskRun.description"
      }}
      method={`arcee.error()`}
    />
  </>
);

const ProfilingIntegration = ({ profilingToken, taskKey, isLoading = false }: ProfilingIntegrationProps) => (
  <Stack spacing={SPACING_2}>
    <div>
      <Typography gutterBottom>
        <FormattedMessage
          id="mlProfilingIntegration.checkOptscaleArceePypi"
          values={{
            link: (chunks) => (
              <Link data-test-id="link_check_pypi" href={PYPI_OPTSCALE_ARCEE} target="_blank" rel="noopener">
                {chunks}
              </Link>
            )
          }}
        />
      </Typography>
    </div>
    <div>
      <Installation />
    </div>
    <div>
      <Import />
    </div>
    <div>
      <Initialization profilingToken={profilingToken} taskKey={taskKey} isLoading={isLoading} />
    </div>
    <div>
      <SendingMetrics />
    </div>
    <div>
      <AddingHyperparameters />
    </div>
    <div>
      <TaggingTaskRun />
    </div>
    <div>
      <AddingMilestone />
    </div>
    <div>
      <AddingStage />
    </div>
    <div>
      <LoggingDatasets />
    </div>
    <div>
      <CreatingModels />
    </div>
    <div>
      <SettingModelVersion />
    </div>
    <div>
      <SettingModelVersionAlias />
    </div>
    <div>
      <SettingModelVersionTag />
    </div>
    <div>
      <CreatingArtifacts />
    </div>
    <div>
      <SettingArtifactTag />
    </div>
    <div>
      <FinishTaskRun />
    </div>
    <div>
      <FailTaskRun />
    </div>
  </Stack>
);

export default ProfilingIntegration;
