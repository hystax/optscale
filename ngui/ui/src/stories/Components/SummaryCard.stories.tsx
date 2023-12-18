import ArrowForwardOutlinedIcon from "@mui/icons-material/ArrowForwardOutlined";
import SummaryCard from "components/SummaryCard";

export default {
  component: SummaryCard,
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
    value: { name: "Value", control: "text", defaultValue: "$123456.321" }
  }
};

export const basic = () => <SummaryCard value="$123456.321" caption="This is some caption" />;

export const withHelp = () => (
  <SummaryCard value="$123456.321" caption="This is some caption" help={{ show: true, messageId: "hystax" }} />
);

export const withKnobs = (args) => (
  <SummaryCard
    value={args.value}
    caption={args.caption}
    color={args.color}
    help={{ show: args.withHelp, messageId: "hystax" }}
    button={{ show: args.withButton, icon: <ArrowForwardOutlinedIcon /> }}
  />
);

export const withButton = () => (
  <SummaryCard
    value="$123456.321"
    caption="This is some caption"
    button={{ show: true, icon: <ArrowForwardOutlinedIcon />, tooltip: { show: true, messageId: "add" } }}
  />
);
