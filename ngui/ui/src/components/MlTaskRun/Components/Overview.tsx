import CheckCircleOutlinedIcon from "@mui/icons-material/CheckCircleOutlined";
import WarningAmberOutlinedIcon from "@mui/icons-material/WarningAmberOutlined";
import { Box, Grid } from "@mui/material";
import { FormattedMessage } from "react-intl";
import CodeBlock from "components/CodeBlock";
import CopyText from "components/CopyText";
import ExpandableList from "components/ExpandableList";
import IconLabel from "components/IconLabel";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import RunDataset from "components/RunDataset";
import RunGoals from "components/RunGoals";
import Skeleton from "components/Skeleton";
import SubTitle from "components/SubTitle";
import Tooltip from "components/Tooltip";
import TypographyLoader from "components/TypographyLoader";
import { SPACING_2 } from "utils/layouts";
import { isEmpty as isEmptyObject } from "utils/objects";

const LOADER_LINES = 5;

const GIT_CHANGES_STATUS = Object.freeze({
  CLEAN: "clean",
  DIRTY: "dirty"
});

const Goals = ({ reachedGoals, isLoading }) => {
  if (isLoading) {
    return <TypographyLoader linesCount={LOADER_LINES} />;
  }

  return !reachedGoals || isEmptyObject(reachedGoals) ? <FormattedMessage id="noGoals" /> : <RunGoals goals={reachedGoals} />;
};

const Dataset = ({ dataset, isLoading }) => {
  if (isLoading) {
    return <TypographyLoader linesCount={LOADER_LINES} />;
  }

  return !dataset ? <FormattedMessage id="noDataset" /> : <RunDataset dataset={dataset} />;
};

const Hyperparameters = ({ hyperparameters, isLoading }) => {
  if (isLoading) {
    return <TypographyLoader linesCount={LOADER_LINES} />;
  }
  return !hyperparameters || isEmptyObject(hyperparameters) ? (
    <FormattedMessage id="noHyperparameters" />
  ) : (
    <ExpandableList
      items={Object.entries(hyperparameters)}
      render={([hyperparameterKey, hyperparameterValue]) => (
        <KeyValueLabel
          key={hyperparameterKey}
          keyText={hyperparameterKey}
          value={
            <CopyText copyIconType="animated" sx={{ fontWeight: "inherit" }} text={hyperparameterValue}>
              {hyperparameterValue}
            </CopyText>
          }
        />
      )}
      maxRows={5}
    />
  );
};

const Tags = ({ tags, isLoading }) => {
  if (isLoading) {
    return <TypographyLoader linesCount={LOADER_LINES} />;
  }

  return !tags || isEmptyObject(tags) ? (
    <FormattedMessage id="noTags" />
  ) : (
    <ExpandableList
      items={Object.entries(tags)}
      render={([tagKey, tagValue]) => (
        <KeyValueLabel
          key={tagKey}
          keyText={tagKey}
          value={
            <CopyText copyIconType="animated" sx={{ fontWeight: "inherit" }} text={tagValue}>
              {tagValue}
            </CopyText>
          }
        />
      )}
      maxRows={5}
    />
  );
};

const GitStatus = ({ git, isLoading }) => {
  if (isLoading) {
    return <TypographyLoader linesCount={LOADER_LINES} />;
  }

  if (!git) {
    return <FormattedMessage id="noGitStatus" />;
  }

  const { remote, branch, commit_id: commitId, status } = git;

  return (
    <>
      <KeyValueLabel
        keyText={<FormattedMessage id="remote" />}
        value={
          <CopyText copyIconType="animated" sx={{ fontWeight: "inherit" }} text={remote}>
            {remote}
          </CopyText>
        }
      />
      <KeyValueLabel
        keyText={<FormattedMessage id="branch" />}
        value={
          <CopyText copyIconType="animated" sx={{ fontWeight: "inherit" }} text={remote}>
            {branch}
          </CopyText>
        }
      />
      <KeyValueLabel
        keyText={<FormattedMessage id="commit" />}
        value={
          <CopyText copyIconType="animated" sx={{ fontWeight: "inherit" }} text={remote}>
            {commitId}
          </CopyText>
        }
      />
      {status === GIT_CHANGES_STATUS.CLEAN && (
        <KeyValueLabel
          keyMessageId="status"
          value={
            <IconLabel
              icon={
                <Tooltip title={<FormattedMessage id="runWasExecutedOnTheCommittedCode" />}>
                  <CheckCircleOutlinedIcon fontSize="inherit" color="success" />
                </Tooltip>
              }
              label={<FormattedMessage id="clean" />}
            />
          }
        />
      )}
      {status === GIT_CHANGES_STATUS.DIRTY && (
        <KeyValueLabel
          keyMessageId="status"
          value={
            <IconLabel
              icon={
                <Tooltip title={<FormattedMessage id="thisRunWasExecutedOnCodeThatHasBeenChangedAndNotCommitted" />}>
                  <WarningAmberOutlinedIcon fontSize="inherit" color="warning" />
                </Tooltip>
              }
              label={<FormattedMessage id="dirty" />}
            />
          }
        />
      )}
    </>
  );
};

const Command = ({ command, isLoading }) => {
  if (isLoading) {
    return <Skeleton variant="rectangle" height="100px" />;
  }

  if (!command) {
    return <FormattedMessage id="noCommand" />;
  }

  return <CodeBlock text={command} />;
};

const StdoutLog = ({ output, isLoading }) => {
  if (isLoading) {
    return <Skeleton variant="rectangle" height="200px" />;
  }

  if (!output) {
    return <FormattedMessage id="noLogOutput" />;
  }

  return <CodeBlock height="100%" maxHeight="500px" text={output} />;
};

const StderrLog = ({ error, isLoading }) => {
  if (isLoading) {
    return <Skeleton variant="rectangle" height="200px" />;
  }

  if (!error) {
    return <FormattedMessage id="noErrorOutput" />;
  }

  return <CodeBlock height="100%" maxHeight="500px" text={error} />;
};

const Overview = ({ reachedGoals, dataset, git, tags, hyperparameters, command, console, isLoading = false }) => (
  <Grid container spacing={SPACING_2}>
    <Grid item xs={12} sm={6} md={3}>
      <SubTitle>
        <FormattedMessage id="metrics" />
      </SubTitle>
      <Goals reachedGoals={reachedGoals} isLoading={isLoading} />
    </Grid>
    <Grid item xs={12} sm={6} md={3}>
      <SubTitle>
        <FormattedMessage id="dataset" />
      </SubTitle>
      <Dataset dataset={dataset} isLoading={isLoading} />
    </Grid>
    <Grid item xs={12} sm={6} md={3}>
      <SubTitle>
        <FormattedMessage id="hyperparameters" />
      </SubTitle>
      <Hyperparameters hyperparameters={hyperparameters} isLoading={isLoading} />
    </Grid>
    <Grid item xs={12} sm={6} md={3}>
      <SubTitle>
        <FormattedMessage id="tags" />
      </SubTitle>
      <Tags tags={tags} isLoading={isLoading} />
    </Grid>
    <Grid item xs={12}>
      <SubTitle>
        <FormattedMessage id="gitStatus" />
      </SubTitle>
      <GitStatus git={git} isLoading={isLoading} />
    </Grid>
    <Grid item xs={12}>
      <SubTitle>
        <FormattedMessage id="command" />
      </SubTitle>
      <Command command={command} isLoading={isLoading} />
    </Grid>
    <Grid item container xs={12} spacing={SPACING_2}>
      <Grid item xs={12} md={6} sx={{ display: "flex", flexDirection: "column" }}>
        <SubTitle>
          <FormattedMessage id="stdoutLog" />
        </SubTitle>
        <Box flexGrow={1}>
          <StdoutLog output={console?.output} isLoading={isLoading} />
        </Box>
      </Grid>
      <Grid item xs={12} md={6} sx={{ display: "flex", flexDirection: "column" }}>
        <SubTitle>
          <FormattedMessage id="stderrLog" />
        </SubTitle>
        <Box flexGrow={1}>
          <StderrLog error={console?.error} isLoading={isLoading} />
        </Box>
      </Grid>
    </Grid>
  </Grid>
);

export default Overview;
