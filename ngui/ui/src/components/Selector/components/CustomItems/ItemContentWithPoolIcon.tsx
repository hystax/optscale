import { type ReactNode } from "react";
import { getIcon } from "components/PoolTypeIcon";
import PoolTypeIconTooltipContent from "components/PoolTypeIconTooltipContent";
import { POOL_TYPES } from "utils/constants";
import ItemContent from "../ItemContent";

type ItemWithPoolIconProps = {
  poolType: keyof typeof POOL_TYPES;
  children: ReactNode;
};

const ItemContentWithPoolIcon = ({ poolType, children }: ItemWithPoolIconProps) => (
  <ItemContent
    icon={{
      placement: "start",
      IconComponent: getIcon(poolType),
      tooltipTitle: <PoolTypeIconTooltipContent type={poolType} />
    }}
  >
    {children}
  </ItemContent>
);

export default ItemContentWithPoolIcon;
