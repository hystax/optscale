import React from "react";
import { Box, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import QuestionMark from "components/QuestionMark";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const Cell = ({ discovered, resource }) => {
  const { isDemo } = useOrganizationInfo();

  if (discovered) {
    const { cloud_account: { id, name, type } = {} } = resource ?? {};

    return <CloudLabel id={id} name={name} type={type} disableLink={isDemo} />;
  }

  return (
    <Box display="flex" alignItems="center">
      <Typography>
        <FormattedMessage id="unknown" />
      </Typography>
      <QuestionMark messageId="executorIsNotFoundInConnectedDataSources" />
    </Box>
  );
};

const mlExecutorLocation = ({ headerDataTestId = "lbl_location", headerMessageId = "location" } = {}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  id: "location",
  cell: ({
    row: {
      original: { discovered, resource }
    }
  }) => <Cell discovered={discovered} resource={resource} />
});

export default mlExecutorLocation;
