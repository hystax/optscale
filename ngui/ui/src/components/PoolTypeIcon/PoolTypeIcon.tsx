import CalculateOutlinedIcon from "@mui/icons-material/CalculateOutlined";
import DomainOutlinedIcon from "@mui/icons-material/DomainOutlined";
import DynamicFeedOutlinedIcon from "@mui/icons-material/DynamicFeedOutlined";
import GroupsOutlinedIcon from "@mui/icons-material/GroupsOutlined";
import InsightsOutlinedIcon from "@mui/icons-material/InsightsOutlined";
import MediationOutlinedIcon from "@mui/icons-material/MediationOutlined";
import WorkOutlineOutlinedIcon from "@mui/icons-material/WorkOutlineOutlined";
import { FormattedMessage } from "react-intl";
import Icon from "components/Icon";
import {
  POOL_TYPES,
  POOL_TYPE_BUDGET,
  POOL_TYPE_BUSINESS_UNIT,
  POOL_TYPE_TEAM,
  POOL_TYPE_PROJECT,
  POOL_TYPE_CICD,
  POOL_TYPE_MLAI,
  POOL_TYPE_ASSET_POOL,
  POOL_TYPES_LIST
} from "utils/constants";

type PoolType = keyof typeof POOL_TYPES;

type PoolTypeIconProps = {
  type: PoolType;
};

export const getIcon = (type: PoolType) =>
  ({
    [POOL_TYPE_BUDGET]: CalculateOutlinedIcon,
    [POOL_TYPE_BUSINESS_UNIT]: DomainOutlinedIcon,
    [POOL_TYPE_TEAM]: GroupsOutlinedIcon,
    [POOL_TYPE_PROJECT]: WorkOutlineOutlinedIcon,
    [POOL_TYPE_CICD]: MediationOutlinedIcon,
    [POOL_TYPE_MLAI]: InsightsOutlinedIcon,
    [POOL_TYPE_ASSET_POOL]: DynamicFeedOutlinedIcon
  })[type];

const PoolTypeIcon = ({ type, ...rest }: PoolTypeIconProps) =>
  POOL_TYPES_LIST.includes(type) ? (
    <Icon
      icon={getIcon(type)}
      tooltip={{ show: true, value: <FormattedMessage id={POOL_TYPES[type] || " "} />, messageId: "type" }}
      {...rest}
    />
  ) : null;

export default PoolTypeIcon;
