import InputAdornment from "@mui/material/InputAdornment";
import Input from "components/Input";
import QuestionMark from "components/QuestionMark";

export default {
  component: Input,
  argTypes: {
    label: { name: "Label", control: "text", defaultValue: "Label" },
    isMasked: { name: "Masked", control: "boolean", defaultValue: false }
  }
};

export const basic = () => <Input />;

export const withHelp = () => (
  <Input
    InputProps={{
      endAdornment: (
        <InputAdornment position="end">
          <QuestionMark messageId="hystax" />
        </InputAdornment>
      )
    }}
    label={"Label"}
  />
);

export const withKnobs = (args) => <Input label={args.label} isMasked={args.isMasked} />;
