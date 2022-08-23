import React, { useState } from "react";
import PoolTypeSelector from "components/PoolTypeSelector";
import { text, boolean } from "@storybook/addon-knobs";
import { KINDS } from "stories";
import { POOL_TYPE_BUDGET } from "utils/constants";

export default {
  title: `${KINDS.COMPONENTS}/PoolTypeSelector`
};

const BasicSelector = () => {
  const [selected, setSelected] = useState(POOL_TYPE_BUDGET);

  const onChange = (value) => setSelected(value);

  return (
    <PoolTypeSelector
      required={boolean("required", true)}
      value={selected}
      onChange={onChange}
      error={boolean("error", false)}
      helperText={text("helperText", "")}
    />
  );
};

export const withKnobs = () => <BasicSelector />;
