import ArrowForwardOutlinedIcon from "@mui/icons-material/ArrowForwardOutlined";
import SummaryCardExtended from "components/SummaryCardExtended";

export default {
  component: SummaryCardExtended,
  argTypes: {
    color: {
      name: "Color",
      control: "select",
      options: ["primary", "secondary", "success", "error", "warning"],
      defaultValue: "primary"
    },
    withHelp: { name: "With help", control: "boolean", defaultValue: true },
    withButton: { name: "With button", control: "boolean", defaultValue: true },
    caption: { name: "Caption", control: "text", defaultValue: "This is some caption" },
    value: { name: "Value", control: "text", defaultValue: "$123456.321" },
    relativeCaption: { name: "Relative caption", control: "text", defaultValue: "This is some relative caption" },
    relativeValue: { name: "Relative value", control: "text", defaultValue: "%15" }
  }
};

export const withKnobs = (args) => (
  <SummaryCardExtended
    value={args.value}
    color={args.color}
    caption={args.caption}
    help={{ show: args.withHelp, messageId: "hystax" }}
    relativeValue={args.relativeValue}
    relativeValueCaption={args.relativeCaption}
    button={{ show: args.withButton, icon: <ArrowForwardOutlinedIcon /> }}
  />
);
