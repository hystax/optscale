import Tooltip from "components/Tooltip";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Tooltip`
};

export const basic = () => (
  <Tooltip title="Tooltip message">
    <span>Hover me</span>
  </Tooltip>
);
