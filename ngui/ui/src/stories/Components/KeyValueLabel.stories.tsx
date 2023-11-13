import KeyValueLabel from "components/KeyValueLabel";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/KeyValueLabel`,
  argTypes: {
    separator: {
      name: "Separator",
      control: "select",
      options: ["colon", "hyphen"],
      defaultValue: "colon"
    },
    messageId: { name: "Message ID", control: "text", defaultValue: "name" },
    text: { name: "Text", control: "text", defaultValue: "" },
    value: { name: "Value", control: "text", defaultValue: "value" }
  }
};

export const basic = () => <KeyValueLabel messageId="name" value="value" />;

export const withKnobs = (args) => (
  <KeyValueLabel messageId={args.messageId} text={args.text} value={args.value} separator={args.separator} />
);
