import Tooltip from "components/Tooltip";
import { sliceByLimitWithEllipsis } from "utils/strings";

const NAME_SIZE_LIMIT = 32;

const ResourceName = ({ name }) => {
  const isOverflow = name.length > NAME_SIZE_LIMIT;

  const label = isOverflow ? sliceByLimitWithEllipsis(name, NAME_SIZE_LIMIT) : name;

  return isOverflow ? (
    <Tooltip title={name} placement="right">
      <span>{label}</span>
    </Tooltip>
  ) : (
    label
  );
};

export default ResourceName;
