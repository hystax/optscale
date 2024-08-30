import { Box, Stack } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import { useParams } from "react-router-dom";
import finopsCloudCostOptimization from "assets/ml/leaderbords.svg";
import Button from "components/Button";
import { useIsAllowed } from "hooks/useAllowedActions";
import { getMlSetupLeaderboardTemplate } from "urls";
import { SPACING_1, SPACING_2 } from "utils/layouts";

const SetupLeaderboardTemplateInvitation = () => {
  const intl = useIntl();
  const { taskId } = useParams();

  const isLeaderboardTemplateSetupEnabled = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  return (
    <Stack alignItems="center" spacing={SPACING_1} mt={SPACING_2}>
      <img
        style={{
          width: "160px"
        }}
        src={finopsCloudCostOptimization}
        alt={intl.formatMessage({ id: "leaderboards" })}
        data-test-id="img_banner_leaderboards"
      />
      <Box>
        <FormattedMessage id="nothingToShowHereYet" />
      </Box>
      <Box>
        {isLeaderboardTemplateSetupEnabled ? (
          <Button
            messageId="setupLeaderboardTemplate"
            color="primary"
            variant="contained"
            link={getMlSetupLeaderboardTemplate(taskId)}
          />
        ) : (
          <FormattedMessage id="leaderboardContactManagerMessage" />
        )}
      </Box>
    </Stack>
  );
};

export default SetupLeaderboardTemplateInvitation;
