import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import ButtonLoader from "components/ButtonLoader";

export default {
  component: ButtonLoader,
  argTypes: {
    messageId: { name: "Message ID", control: "text", defaultValue: "checkConnection" },
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
    isLoading: { name: "Loading", control: "boolean", defaultValue: false },
    disabled: { name: "Disabled", control: "boolean", defaultValue: false }
  }
};

const action = () => {
  console.log("Action");
};

export const basic = (args) => (
  <ButtonLoader
    isLoading={args.isLoading}
    disabled={args.disabled}
    messageId={args.messageId}
    size={args.size}
    variant={args.variant}
    color={args.color}
    onClick={action}
  />
);

export const withIcon = (args) => (
  <ButtonLoader
    startIcon={<AddOutlinedIcon />}
    isLoading={args.isLoading}
    disabled={args.disabled}
    messageId={args.messageId}
    size={args.size}
    variant={args.variant}
    color={args.color}
    onClick={action}
  />
);
