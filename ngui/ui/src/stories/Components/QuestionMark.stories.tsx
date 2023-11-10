import QuestionMark from "components/QuestionMark";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/QuestionMark`,
  argTypes: {
    fontSize: {
      name: "Font size",
      control: "select",
      options: ["inherit", "default", "small", "large"],
      defaultValue: "inherit"
    },
    messageId: { name: "Message ID", control: "text", defaultValue: "assignmentRuleConditionsDescription" },
    rightSide: { name: "Right side", control: "boolean", defaultValue: false }
  }
};

export const basic = () => <QuestionMark messageId="assignmentRuleConditionsDescription" />;

export const withKnobs = (args) => (
  <QuestionMark messageId={args.messageId} fontSize={args.fontSize} rightSide={args.rightSide} />
);
