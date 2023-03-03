import React from "react";
import { Skeleton, Stack, Typography } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import CodeBlock from "components/CodeBlock";

const ProfilingIntegration = ({ profilingToken, isLoading }) => {
  const arceeInit = <CodeBlock text={`arcee.init("${profilingToken}", application_key)`} />;

  return (
    <Stack spacing={1}>
      <div>
        <Typography gutterBottom>
          <FormattedMessage id="mlProfilingIntegration.installModule" />
        </Typography>
        <CodeBlock text="pip install optscale_arcee" />
      </div>
      <div>
        <Typography gutterBottom>
          <FormattedMessage id="mlProfilingIntegration.importCollector" />
        </Typography>
        <CodeBlock text={`import optscale_arcee as arcee`} />
      </div>
      <div style={{ width: "100%" }}>
        <Typography gutterBottom>
          <FormattedMessage id="mlProfilingIntegration.initCollector" />
        </Typography>
        {isLoading ? <Skeleton width="100%">{arceeInit}</Skeleton> : arceeInit}
      </div>
      <div>
        <Typography gutterBottom>
          <FormattedMessage id="mlProfilingIntegration.sendStats" />
        </Typography>
        <CodeBlock text={`arcee.send({ key1: value1, key2: value2 })`} />
      </div>
      <div>
        <Typography gutterBottom>
          <FormattedMessage id="mlProfilingIntegration.addTag" />
        </Typography>
        <CodeBlock text={`arcee.tag(tag_key, tag_value)`} />
      </div>
      <div>
        <Typography gutterBottom>
          <FormattedMessage id="mlProfilingIntegration.addMilestone" />
        </Typography>
        <CodeBlock text={`arcee.milestone(milestone_name)`} />
      </div>
      <div>
        <Typography gutterBottom>
          <FormattedMessage id="mlProfilingIntegration.addStages" />
        </Typography>
        <CodeBlock text={`arcee.stage(stage_name)`} />
      </div>
      <div>
        <Typography gutterBottom>
          <FormattedMessage id="mlProfilingIntegration.finishModelRun" />
        </Typography>
        <CodeBlock text={`arcee.finish()`} />
      </div>
      <div>
        <Typography gutterBottom>
          <FormattedMessage id="mlProfilingIntegration.orForFailedTasks" />
        </Typography>
        <CodeBlock text={`arcee.error()`} />
      </div>
    </Stack>
  );
};
ProfilingIntegration.propTypes = {
  profilingToken: PropTypes.string,
  isLoading: PropTypes.bool
};

export default ProfilingIntegration;
