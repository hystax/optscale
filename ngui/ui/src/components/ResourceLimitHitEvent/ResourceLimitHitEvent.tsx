import { FormattedMessage } from "react-intl";
import Chip from "components/Chip";
import { RESOURCE_LIMIT_HIT_STATE } from "utils/constants";

const getLabel = (state) =>
  ({
    [RESOURCE_LIMIT_HIT_STATE.RED]: <FormattedMessage id="violation" />,
    [RESOURCE_LIMIT_HIT_STATE.GREEN]: <FormattedMessage id="backToNormal" />
  })[state];

const getColor = (state) =>
  ({
    [RESOURCE_LIMIT_HIT_STATE.RED]: "error",
    [RESOURCE_LIMIT_HIT_STATE.GREEN]: "success"
  })[state];

const ResourceLimitHitEvent = ({ state }) => {
  const color = getColor(state);
  const label = getLabel(state);

  return <Chip variant="outlined" uppercase color={color} label={label} />;
};

export default ResourceLimitHitEvent;
