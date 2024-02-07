import { type ElementType, type ReactNode } from "react";
import { Box } from "@mui/system";
import Tooltip from "components/Tooltip";

type ItemContentProps = {
  children: ReactNode;
  icon?: {
    IconComponent: ElementType;
    placement?: "start" | "end";
    tooltipTitle?: ReactNode;
  };
};

const ItemContent = ({ icon, children }: ItemContentProps) => {
  if (icon) {
    const { placement = "start", IconComponent, tooltipTitle } = icon;

    const iconElement = (
      <Tooltip title={tooltipTitle}>
        <Box
          mr={placement === "start" ? "0.2rem" : 0}
          ml={placement === "end" ? "0.2rem" : 0}
          display="flex"
          alignItems="center"
        >
          <IconComponent fontSize="small" />
        </Box>
      </Tooltip>
    );

    return (
      <Box display="flex" alignItems="center">
        {placement === "start" && iconElement}
        {children}
        {placement === "end" && iconElement}
      </Box>
    );
  }

  return children;
};

export default ItemContent;
