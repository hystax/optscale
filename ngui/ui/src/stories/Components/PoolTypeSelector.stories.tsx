import { useState } from "react";
import PoolTypeSelector from "components/PoolTypeSelector";
import { POOL_TYPE_BUDGET } from "utils/constants";

export default {
  component: PoolTypeSelector,
  argTypes: {
    required: { name: "Required", control: "boolean", defaultValue: true },
    error: { name: "Error", control: "boolean", defaultValue: false },
    helperText: { name: "Helper text", control: "text", defaultValue: "" }
  }
};

const BasicSelector = (args) => {
  const [selected, setSelected] = useState(POOL_TYPE_BUDGET);

  const onChange = (value) => setSelected(value);

  return (
    <PoolTypeSelector
      required={args.required}
      value={selected}
      onChange={onChange}
      error={args.error}
      helperText={args.helperText}
    />
  );
};

export const withKnobs = () => <BasicSelector />;
