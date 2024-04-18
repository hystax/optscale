import { useContext } from "react";
import { Box, Skeleton, Stack, Typography } from "@mui/material";
import Link from "@mui/material/Link";
import { useTheme } from "@mui/material/styles";
import { FormattedMessage, useIntl } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CodeBlock from "components/CodeBlock";
import CopyText from "components/CopyText";
import HtmlSymbol from "components/HtmlSymbol";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import SubTitle from "components/SubTitle";
import { ProfilingIntegrationModalContext } from "contexts/ProfilingIntegrationModalContext";
import { ML_TASK_METRICS, ML_TASKS, PYPI_OPTSCALE_ARCEE } from "urls";

const Pre = ({ children }) => {
  const theme = useTheme();

  return (
    <pre
      style={{
        backgroundColor: theme.palette.background.default,
        borderRadius: theme.spacing(0.5),
        margin: 0,
        display: "inline"
      }}
    >
      {children}
    </pre>
  );
};

const preFormatMessageValues = {
  pre: (chunks) => <Pre>{chunks}</Pre>
};

const Installation = () => (
  <>
    <SubTitle fontWeight="bold">
      <FormattedMessage id="installation" />
    </SubTitle>
    <Typography gutterBottom>
      <FormattedMessage id="mlProfilingIntegration.installModule" values={{ ...preFormatMessageValues }} />
      <HtmlSymbol symbol="colon" />
    </Typography>
    <CodeBlock text="pip install optscale_arcee" />
  </>
);

const Import = () => (
  <>
    <SubTitle fontWeight="bold">
      <FormattedMessage id="import" />
    </SubTitle>
    <Typography gutterBottom>
      <FormattedMessage id="mlProfilingIntegration.importCollector" values={{ ...preFormatMessageValues }} />
      <HtmlSymbol symbol="colon" />
    </Typography>
    <CodeBlock text="import optscale_arcee as arcee" />
  </>
);

const Initialization = ({ profilingToken, taskKey, isLoading }) => {
  const intl = useIntl();

  const { onClose } = useContext(ProfilingIntegrationModalContext);

  const arceeInitUsingContextManager = (
    <CodeBlock
      text={`with arcee.init("${profilingToken}", "${taskKey ?? "task_key"}"):
    # ${intl.formatMessage({ id: "mlProfilingIntegration.someCode" })}`}
    />
  );
  const arceeInitUsingFunctionCall = (
    <CodeBlock
      text={`arcee.init("${profilingToken}", "${taskKey ?? "task_key"}")
# ${intl.formatMessage({ id: "mlProfilingIntegration.someCode" })}
arcee.finish()
# ${intl.formatMessage({ id: "mlProfilingIntegration.orInCaseOfError" })}
arcee.error()
`}
    />
  );

  return (
    <>
      <SubTitle fontWeight="bold">
        <FormattedMessage id="initialization" />
      </SubTitle>
      <Box>
        <Typography gutterBottom>
          <FormattedMessage id="mlProfilingIntegration.initDescription" />
        </Typography>
        <ul>
          <li>
            {isLoading ? (
              <Skeleton />
            ) : (
              <KeyValueLabel
                keyMessageId="profilingToken"
                value={<CopyText text={profilingToken}>{profilingToken}</CopyText>}
                isBoldValue={false}
              />
            )}
          </li>
          <li>
            <Typography>
              {taskKey ? (
                <KeyValueLabel
                  keyMessageId="taskKey"
                  value={<CopyText text={taskKey}>{taskKey}</CopyText>}
                  isBoldValue={false}
                />
              ) : (
                <FormattedMessage
                  id="mlProfilingIntegration.initDescription.taskKeyCanBeFound"
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
            id="mlProfilingIntegration.initCollectorUsingContextManager"
            values={{
              br: <br />
            }}
          />
          <HtmlSymbol symbol="colon" />
        </Typography>
        {isLoading ? <Skeleton width="100%">{arceeInitUsingContextManager}</Skeleton> : arceeInitUsingContextManager}
        <Typography gutterBottom>
          <FormattedMessage
            id="mlProfilingIntegration.initCollectorUsingContextManagerDescription"
            values={{
              ...preFormatMessageValues
            }}
          />
        </Typography>
      </Box>
      <Box mb={1}>
        <Typography gutterBottom>
          <FormattedMessage
            id="mlProfilingIntegration.alternativeInit"
            values={{
              ...preFormatMessageValues
            }}
          />
        </Typography>
        {isLoading ? <Skeleton width="100%">{arceeInitUsingFunctionCall}</Skeleton> : arceeInitUsingFunctionCall}
      </Box>
    </>
  );
};

const SendingMetrics = () => (
  <>
    <SubTitle fontWeight="bold">
      <FormattedMessage id="sendingMetrics" />
    </SubTitle>
    <Typography gutterBottom>
      <FormattedMessage
        id="mlProfilingIntegration.sendMetrics"
        values={{
          ...preFormatMessageValues,
          link: (chunks) => (
            <Link to={ML_TASK_METRICS} component={RouterLink}>
              {chunks}
            </Link>
          )
        }}
      />
      <HtmlSymbol symbol="colon" />
    </Typography>
    <ul>
      <li>
        <Typography>
          <FormattedMessage
            id="mlProfilingIntegration.sendMetricsDataDescription"
            values={{
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </Typography>
      </li>
    </ul>
    <Box mb={1}>
      <CodeBlock text={`arcee.send({ "metric_key_1": value_1, "metric_key_2": value_2 })`} />
    </Box>
  </>
);

const TaggingTaskRun = () => (
  <>
    <SubTitle fontWeight="bold">
      <FormattedMessage id="mlProfilingIntegration.taggingTaskRun" />
    </SubTitle>
    <Typography gutterBottom>
      <FormattedMessage
        id="mlProfilingIntegration.addTag"
        values={{
          ...preFormatMessageValues
        }}
      />
      <HtmlSymbol symbol="colon" />
    </Typography>
    <ul>
      <li>
        <Typography>
          <FormattedMessage
            id="mlProfilingIntegration.addTagKeyDescription"
            values={{
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </Typography>
      </li>
      <li>
        <Typography>
          <FormattedMessage
            id="mlProfilingIntegration.addTagValueDescription"
            values={{
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </Typography>
      </li>
    </ul>
    <CodeBlock text={`arcee.tag("tag_key", "tag_value")`} />
  </>
);

const AddingMilestone = () => (
  <>
    <SubTitle fontWeight="bold">
      <FormattedMessage id="mlProfilingIntegration.addingMilestone" />
    </SubTitle>
    <Typography gutterBottom>
      <FormattedMessage
        id="mlProfilingIntegration.addMilestone"
        values={{
          ...preFormatMessageValues
        }}
      />
      <HtmlSymbol symbol="colon" />
    </Typography>
    <ul>
      <li>
        <Typography>
          <FormattedMessage
            id="mlProfilingIntegration.addMilestoneNameDescription"
            values={{
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </Typography>
      </li>
    </ul>
    <CodeBlock text={`arcee.milestone("milestone_name")`} />
  </>
);

const AddingStage = () => (
  <>
    <SubTitle fontWeight="bold">
      <FormattedMessage id="mlProfilingIntegration.addingStageTitle" values={{ ...preFormatMessageValues }} />
    </SubTitle>
    <Typography gutterBottom>
      <FormattedMessage id="mlProfilingIntegration.addingStage" values={{ ...preFormatMessageValues }} />
      <HtmlSymbol symbol="colon" />
    </Typography>
    <ul>
      <li>
        <Typography>
          <FormattedMessage
            id="mlProfilingIntegration.addingStageNameDescription"
            values={{
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </Typography>
      </li>
    </ul>
    <CodeBlock text={`arcee.stage("stage_name")`} />
  </>
);

const LoggingDatasets = () => (
  <>
    <SubTitle fontWeight="bold">
      <FormattedMessage id="mlProfilingIntegration.loggingDatasetsTitle" />
    </SubTitle>
    <Typography gutterBottom>
      <FormattedMessage id="mlProfilingIntegration.loggingDataset" values={{ ...preFormatMessageValues }} />
      <HtmlSymbol symbol="colon" />
    </Typography>
    <ul>
      <li>
        <Typography>
          <FormattedMessage
            id="mlProfilingIntegration.loggingDatasetDescription"
            values={{
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </Typography>
      </li>
    </ul>
    <CodeBlock text={`arcee.dataset("dataset_path")`} />
  </>
);

const CreatingModels = () => (
  <>
    <SubTitle fontWeight="bold">
      <FormattedMessage id="mlProfilingIntegration.creatingModelsTitle" />
    </SubTitle>
    <Typography gutterBottom>
      <FormattedMessage id="mlProfilingIntegration.creatingModels" values={{ ...preFormatMessageValues }} />
      <HtmlSymbol symbol="colon" />
    </Typography>
    <ul>
      <li>
        <Typography>
          <FormattedMessage
            id="mlProfilingIntegration.creatingModelsKeyDescription"
            values={{
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </Typography>
      </li>
      <li>
        <Typography>
          <FormattedMessage
            id="mlProfilingIntegration.creatingModelsPathDescription"
            values={{
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </Typography>
      </li>
    </ul>
    <CodeBlock text={`arcee.model("my_model", "/home/user/my_model")`} />
  </>
);

const SettingModelVersion = () => (
  <>
    <SubTitle fontWeight="bold">
      <FormattedMessage id="mlProfilingIntegration.settingModelVersionTitle" />
    </SubTitle>
    <Typography gutterBottom>
      <FormattedMessage id="mlProfilingIntegration.settingModelVersion" values={{ ...preFormatMessageValues }} />
      <HtmlSymbol symbol="colon" />
    </Typography>
    <ul>
      <li>
        <Typography>
          <FormattedMessage
            id="mlProfilingIntegration.settingModelVersionVersionDescription"
            values={{
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </Typography>
      </li>
    </ul>
    <CodeBlock text={`arcee.model_version("1.2.3-release")`} />
  </>
);

const AddHyperparameters = () => (
  <>
    <SubTitle fontWeight="bold">
      <FormattedMessage id="mlProfilingIntegration.addingHyperparametersTitle" />
    </SubTitle>
    <Typography gutterBottom>
      <FormattedMessage id="mlProfilingIntegration.addHyperparameters" values={{ ...preFormatMessageValues }} />
      <HtmlSymbol symbol="colon" />
    </Typography>
    <ul>
      <li>
        <Typography>
          <FormattedMessage
            id="mlProfilingIntegration.addHyperparameters.keyParameterDescription"
            values={{
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </Typography>
      </li>
      <li>
        <Typography>
          <FormattedMessage
            id="mlProfilingIntegration.addHyperparameters.valueParameterDescription"
            values={{
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </Typography>
      </li>
    </ul>
    <CodeBlock text={`arcee.hyperparam("hyperparam_key", hyperparam_value)`} />
  </>
);

const SettingModelVersionAlias = () => (
  <>
    <SubTitle fontWeight="bold">
      <FormattedMessage id="mlProfilingIntegration.settingModelVersionAliasTitle" />
    </SubTitle>
    <Typography gutterBottom>
      <FormattedMessage id="mlProfilingIntegration.settingModelVersionAlias" values={{ ...preFormatMessageValues }} />
      <HtmlSymbol symbol="colon" />
    </Typography>
    <ul>
      <li>
        <Typography>
          <FormattedMessage
            id="mlProfilingIntegration.settingModelVersionVersionAliasDescription"
            values={{
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </Typography>
      </li>
    </ul>
    <CodeBlock text={`arcee.model_version_alias("winner")`} />
  </>
);

const SettingModelVersionTag = () => (
  <>
    <SubTitle fontWeight="bold">
      <FormattedMessage id="mlProfilingIntegration.settingModelVersionTagTitle" />
    </SubTitle>
    <Typography gutterBottom>
      <FormattedMessage id="mlProfilingIntegration.settingModelVersionTag" values={{ ...preFormatMessageValues }} />
      <HtmlSymbol symbol="colon" />
    </Typography>
    <ul>
      <li>
        <Typography>
          <FormattedMessage
            id="mlProfilingIntegration.settingModelVersionTagKeyDescription"
            values={{
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </Typography>
      </li>
      <li>
        <Typography>
          <FormattedMessage
            id="mlProfilingIntegration.settingModelVersionTagValueDescription"
            values={{
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </Typography>
      </li>
    </ul>
    <CodeBlock text={`arcee.model_version_tag("env", "staging demo")`} />
  </>
);

const FinishTaskRun = () => (
  <>
    <SubTitle fontWeight="bold">
      <FormattedMessage id="mlProfilingIntegration.finishTaskRunTitle" />
    </SubTitle>
    <Typography gutterBottom>
      <FormattedMessage
        id="mlProfilingIntegration.finishTaskRun"
        values={{
          ...preFormatMessageValues
        }}
      />
    </Typography>
    <CodeBlock text="arcee.finish()" />
  </>
);

const FailTaskRun = () => (
  <>
    <Typography gutterBottom>
      <SubTitle fontWeight="bold">
        <FormattedMessage id="mlProfilingIntegration.failTaskRunTitle" />
      </SubTitle>
      <FormattedMessage
        id="mlProfilingIntegration.failTaskRun"
        values={{
          ...preFormatMessageValues
        }}
      />
    </Typography>
    <CodeBlock text="arcee.error()" />
  </>
);

const ProfilingIntegration = ({ profilingToken, taskKey, isLoading }) => (
  <Stack spacing={1}>
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
      <AddHyperparameters />
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
      <FinishTaskRun />
    </div>
    <div>
      <FailTaskRun />
    </div>
  </Stack>
);

export default ProfilingIntegration;
