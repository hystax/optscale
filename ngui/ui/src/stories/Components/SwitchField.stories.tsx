import { useForm } from "react-hook-form";
import QuestionMark from "components/QuestionMark";
import SwitchField from "components/SwitchField";

export default {
  component: SwitchField,
  argTypes: {
    labelMessageId: { name: "Label message ID", control: "text", defaultValue: "name" },
    withEndAdornment: { name: "With end adornment", control: "boolean", defaultValue: false }
  }
};

const Component = ({ labelMessageId, endAdornment }) => {
  const { control } = useForm();
  return (
    <SwitchField
      name="name"
      defaultValue={false}
      labelMessageId={labelMessageId}
      control={control}
      endAdornment={endAdornment}
    />
  );
};

export const withKnobs = (args) => (
  <Component
    labelMessageId={args.labelMessageId}
    endAdornment={
      args.withEndAdornment ? (
        <QuestionMark
          messageId="dataExportDetectionTooltip"
          messageValues={{
            break: <br />
          }}
        />
      ) : null
    }
  />
);
