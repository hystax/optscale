import { FormControl, FormControlLabel, FormLabel, Radio, RadioGroup } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import type { DecimalSeparator } from "../types";

type DecimalSeparatorFieldProps = {
  name: string;
};

const OPTIONS: { value: DecimalSeparator; messageId: string; dataTestIdSuffix: string }[] = [
  { value: ".", messageId: "focusMappingDecimalSeparatorDot", dataTestIdSuffix: "dot" },
  { value: ",", messageId: "focusMappingDecimalSeparatorComma", dataTestIdSuffix: "comma" },
];

// An unset separator (null) is shown as ".", the value the API uses when it is not set
const DecimalSeparatorField = ({ name }: DecimalSeparatorFieldProps) => {
  const { control } = useFormContext();

  return (
    <Controller
      name={name}
      control={control}
      render={({ field: { value, onChange } }) => (
        <FormControl fullWidth>
          <FormLabel sx={{ mb: 0.25 }}>
            <FormattedMessage id="focusMappingDecimalSeparator" />
          </FormLabel>
          <RadioGroup row value={value ?? "."} onChange={(event) => onChange(event.target.value)}>
            {OPTIONS.map(({ value: optionValue, messageId, dataTestIdSuffix }) => (
              <FormControlLabel
                key={optionValue}
                value={optionValue}
                control={<Radio size="small" inputProps={{ "data-test-id": `radio_${name}_${dataTestIdSuffix}` } as object} />}
                label={<FormattedMessage id={messageId} />}
              />
            ))}
          </RadioGroup>
        </FormControl>
      )}
    />
  );
};

export default DecimalSeparatorField;
