import { type ElementType, type ReactNode } from "react";
import Tooltip from "components/Tooltip";
import Item from "./Item";
import ItemContent from "./ItemContent";

type ButtonProps = {
  onClick: () => void;
  children: ReactNode;
  dataTestId?: string;
  disabled?: boolean;
  icon?: {
    placement?: "start" | "end";
    IconComponent: ElementType;
    tooltipTitle?: ReactNode;
  };
  tooltipTitle?: ReactNode;
};

const Button = ({ onClick, icon, dataTestId, disabled = false, children, tooltipTitle }: ButtonProps) => (
  <Tooltip title={tooltipTitle}>
    {/* 
      Use span to add tooltip for disabled button
      https://mui.com/material-ui/react-tooltip/#disabled-elements 
    */}
    <span>
      <Item onClick={onClick} data-test-id={dataTestId} disabled={disabled}>
        <ItemContent icon={icon}>{children}</ItemContent>
      </Item>
    </span>
  </Tooltip>
);

export default Button;
