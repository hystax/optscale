import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import MlRunStatus from "components/MlRunStatus/MlRunStatus";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { ML_RUN_STATUS } from "utils/constants";

const MlRunStatusCell = ({
  reason,
  status,
  // Used only in live demo mockups
  status_description: { type: statusDescriptionType, payload: statusDescriptionPayload = {} } = {}
}) => {
  const { isDemo } = useOrganizationInfo();

  if (isDemo) {
    const getFormatStatusDescriptionHandler = () =>
      ({
        reached_plateau: () => {
          const { goal: goalName, value: goalValue } = statusDescriptionPayload;
          return (
            <FormattedMessage
              id="reachedPlateau"
              values={{
                name: goalName,
                value: goalValue,
                strong: (chunks) => <strong>{chunks}</strong>
              }}
            />
          );
        },
        time_exceeded: () => <FormattedMessage id="timeExceeded" />,
        goals_met: () => <FormattedMessage id="allGoalsMet" />
      })[statusDescriptionType];

    const handler = getFormatStatusDescriptionHandler();

    const formattedDescription = typeof handler === "function" ? <Typography variant="caption">{handler()}</Typography> : "";

    return (
      <CaptionedCell
        caption={{
          key: "caption",
          node: formattedDescription
        }}
      >
        <MlRunStatus status={status} />
      </CaptionedCell>
    );
  }

  return (
    <CaptionedCell caption={[ML_RUN_STATUS.FAILED, ML_RUN_STATUS.ABORTED].includes(status) ? reason : undefined}>
      <MlRunStatus status={status} />
    </CaptionedCell>
  );
};

export default MlRunStatusCell;
