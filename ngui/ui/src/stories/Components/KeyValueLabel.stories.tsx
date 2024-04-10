import KeyValueLabel from "components/KeyValueLabel";

export default {
  component: KeyValueLabel,
  argTypes: {
    keyMessageId: { name: "Key message id", control: "text", defaultValue: "name" },
    keyText: { name: "Key text", control: "text", defaultValue: "" },
    value: { name: "Value", control: "text", defaultValue: "value" }
  }
};

export const basic = () => <KeyValueLabel keyMessageId="name" value="value" />;

export const withKnobs = (args) => <KeyValueLabel keyMessageId={args.keyMessageId} keyText={args.keyText} value={args.value} />;
