import SquareIcon from "@mui/icons-material/Square";
import { TextInput } from "components/forms/common/fields";

const OptionField = ({ optionName, optionValue }) => (
  <TextInput
    key={optionName}
    label={optionName}
    name={optionName}
    InputProps={{
      endAdornment: <SquareIcon style={{ border: "1px dashed black", color: optionValue }} />
    }}
  />
);

export default OptionField;
