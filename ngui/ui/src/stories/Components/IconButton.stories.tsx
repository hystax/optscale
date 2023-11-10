import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import { FormattedMessage } from "react-intl";
import IconButton from "components/IconButton";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/IconButton`,
  argTypes: {
    color: {
      name: "Color",
      control: "select",
      options: ["info", "inherit", "primary", "success", "error"],
      defaultValue: "info"
    },
    size: {
      name: "Size",
      control: "select",
      options: ["small", "medium"],
      defaultValue: "small"
    },
    edge: {
      name: "Edge",
      control: "select",
      options: [false, "end", "start"],
      defaultValue: false
    },
    disabled: { name: "Disabled", control: "boolean", defaultValue: false }
  }
};

export const basic = () => <IconButton icon={<EditOutlinedIcon />} />;
export const withOnClick = () => <IconButton icon={<EditOutlinedIcon />} onClick={() => console.log("Button clicked")} />;
export const withTooltip = () => (
  <IconButton
    icon={<EditOutlinedIcon />}
    tooltip={{
      show: true,
      value: <FormattedMessage id="edit" />
    }}
  />
);
export const disabled = () => <IconButton icon={<EditOutlinedIcon />} disabled />;
export const withKnobs = (args) => (
  <IconButton icon={<EditOutlinedIcon />} disabled={args.disabled} edge={args.edge} size={args.size} color={args.color} />
);
