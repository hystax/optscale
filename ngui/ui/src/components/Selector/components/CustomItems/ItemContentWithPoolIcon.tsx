import { type ReactNode } from "react";
import { TooltipProps } from "@mui/material";
import { getIcon } from "components/PoolTypeIcon";
import PoolTypeIconTooltipContent from "components/PoolTypeIconTooltipContent";
import { POOL_TYPES } from "utils/constants";
import { sliceByLimitWithEllipsis } from "utils/strings";
import ItemContent from "../ItemContent";

type ItemWithPoolIconProps = {
  poolType: keyof typeof POOL_TYPES;
  label?: string;
  children?: ReactNode;
  tooltip?: {
    title: ReactNode;
    placement?: TooltipProps["placement"];
  };
};

const MAX_LABEL_LENGTH = 32;

const ItemContentWithPoolIcon = ({ poolType, label, children, tooltip: tooltipProp }: ItemWithPoolIconProps) => {
  const getProps = () => {
    if (label) {
      const isLongLabel = label.length > MAX_LABEL_LENGTH;
      return {
        content: isLongLabel ? sliceByLimitWithEllipsis(label, MAX_LABEL_LENGTH) : label,
        tooltip: tooltipProp ?? {
          title: label,
        },
      };
    }
    return {
      content: children,
      tooltipProp,
    };
  };

  const { content, tooltip } = getProps();

  return (
    <ItemContent
      icon={{
        placement: "start",
        IconComponent: getIcon(poolType),
        tooltipTitle: <PoolTypeIconTooltipContent type={poolType} />,
      }}
      tooltip={tooltip}
    >
      {content}
    </ItemContent>
  );
};

export default ItemContentWithPoolIcon;
