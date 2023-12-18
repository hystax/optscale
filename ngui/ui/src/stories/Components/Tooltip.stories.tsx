import Tooltip from "components/Tooltip";

export default {
  component: Tooltip
};

export const basic = () => (
  <Tooltip title="Tooltip message">
    <span>Hover me</span>
  </Tooltip>
);
