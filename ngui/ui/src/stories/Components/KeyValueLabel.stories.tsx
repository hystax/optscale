import KeyValueLabel from "components/KeyValueLabel";

export default {
  component: KeyValueLabel,
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
