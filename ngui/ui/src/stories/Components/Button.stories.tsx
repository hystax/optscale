import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import Tooltip from "components/Tooltip";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Button`,
  argTypes: {
    messageId: { name: "Message ID", control: "text", defaultValue: "add" },
    size: {
      name: "Size",
      control: "select",
      options: ["small", "medium", "large"],
      defaultValue: "medium"
    },
    variant: {
      name: "Variant",
      control: "select",
      options: ["text", "outlined", "contained"],
      defaultValue: "outlined"
    },
    color: {
      name: "Color",
      control: "select",
      options: ["info", "inherit", "primary", "success", "error"],
      defaultValue: "info"
    },
    withIcon: { name: "With icon", control: "boolean", defaultValue: false },
    uppercase: { name: "Uppercase", control: "boolean", defaultValue: false },
    disabled: { name: "Disabled", control: "boolean", defaultValue: false }
  }
};

export const basic = () => <Button messageId="add" />;
export const withIcon = () => <Button messageId="add" startIcon={<AddOutlinedIcon />} />;
export const withOnClick = () => <Button messageId="add" onClick={() => console.log("Button clicked")} />;
export const lowercase = () => <Button messageId="add" uppercase={false} />;
export const withTooltip = () => (
  <Tooltip title={<FormattedMessage id="add" />}>
    <Button messageId="add" />
  </Tooltip>
);
export const disabled = () => <Button messageId="add" disabled />;
export const withKnobs = (args) => (
  <Button
    messageId={args.messageId}
    startIcon={args.withIcon ? <AddOutlinedIcon /> : null}
    uppercase={args.uppercase}
    onClick={() => console.log("Button clicked")}
    size={args.size}
    variant={args.variant}
    disabled={args.disabled}
    color={args.color}
  />
);
