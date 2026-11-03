import { FormControl, FormControlLabel, FormLabel, Radio, RadioGroup } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { TAGS_MODES } from "../constants";
import type { TagsMode } from "../types";

type TagsModeFieldProps = {
  name: string;
};

const OPTIONS: { value: TagsMode; messageId: string }[] = [
  { value: TAGS_MODES.JSON, messageId: "focusMappingTagsModeJson" },
  { value: TAGS_MODES.LIST, messageId: "focusMappingTagsModeList" },
  { value: TAGS_MODES.PREFIXED_COLUMNS, messageId: "focusMappingTagsModePrefixedColumns" },
];

// An unset mode (null) is shown as json, the mode the API uses when it is not set
const TagsModeField = ({ name }: TagsModeFieldProps) => {
  const { control } = useFormContext();

  return (
    <Controller
      name={name}
      control={control}
      render={({ field: { value, onChange } }) => (
        <FormControl fullWidth>
          <FormLabel sx={{ mb: 0.25 }}>
            <FormattedMessage id="focusMappingTagsMode" />
          </FormLabel>
          <RadioGroup row value={value ?? TAGS_MODES.JSON} onChange={(event) => onChange(event.target.value)}>
            {OPTIONS.map(({ value: optionValue, messageId }) => (
              <FormControlLabel
                key={optionValue}
                value={optionValue}
                control={<Radio size="small" inputProps={{ "data-test-id": `radio_${name}_${optionValue}` } as object} />}
                label={<FormattedMessage id={messageId} />}
              />
            ))}
          </RadioGroup>
        </FormControl>
      )}
    />
  );
};

export default TagsModeField;
