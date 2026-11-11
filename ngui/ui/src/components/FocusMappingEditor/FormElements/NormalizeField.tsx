import { Checkbox, FormControl, FormControlLabel, FormLabel, FormGroup, FormHelperText } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import type { NormalizeOption } from "../types";

type NormalizeFieldProps = {
  name: string;
};

const OPTIONS: { value: NormalizeOption; messageId: string }[] = [
  { value: "strip", messageId: "focusMappingNormalizeStrip" },
  { value: "lower", messageId: "focusMappingNormalizeLower" },
];

// Three states: not set (null, the default mapping's normalization is used when the chain ends with it),
// no normalization ([]) and the chosen options. The options are shown only when the normalization is set.
const NormalizeField = ({ name }: NormalizeFieldProps) => {
  const { control } = useFormContext();

  return (
    <Controller
      name={name}
      control={control}
      render={({ field: { value, onChange } }) => {
        const selected: NormalizeOption[] | null = value ?? null;

        const toggle = (option: NormalizeOption, checked: boolean) =>
          // Keep the order of the options
          onChange(
            OPTIONS.map(({ value: optionValue }) => optionValue).filter((optionValue) =>
              optionValue === option ? checked : (selected ?? []).includes(optionValue)
            )
          );

        return (
          <FormControl fullWidth>
            <FormLabel sx={{ mb: 0.25 }}>
              <FormattedMessage id="focusMappingNormalize" />
            </FormLabel>
            <FormGroup>
              <FormControlLabel
                control={
                  <Checkbox
                    size="small"
                    checked={selected === null}
                    onChange={(event) => onChange(event.target.checked ? null : [])}
                    inputProps={{ "data-test-id": `checkbox_${name}_default` } as object}
                  />
                }
                label={<FormattedMessage id="focusMappingNormalizeUseDefault" />}
              />
            </FormGroup>
            {selected === null ? (
              <FormHelperText>
                <FormattedMessage id="focusMappingNormalizeUseDefaultHelperText" />
              </FormHelperText>
            ) : (
              <FormGroup row>
                {OPTIONS.map(({ value: optionValue, messageId }) => (
                  <FormControlLabel
                    key={optionValue}
                    control={
                      <Checkbox
                        size="small"
                        checked={selected.includes(optionValue)}
                        onChange={(event) => toggle(optionValue, event.target.checked)}
                        inputProps={{ "data-test-id": `checkbox_${name}_${optionValue}` } as object}
                      />
                    }
                    label={<FormattedMessage id={messageId} />}
                  />
                ))}
              </FormGroup>
            )}
          </FormControl>
        );
      }}
    />
  );
};

export default NormalizeField;
