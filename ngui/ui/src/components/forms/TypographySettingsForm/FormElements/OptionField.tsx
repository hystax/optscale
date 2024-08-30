import { TextInput } from "components/forms/common/fields";
import { isMedia } from "theme";

const OptionField = ({ optionName }) => (
  <TextInput key={optionName} label={optionName} name={isMedia(optionName) ? `${optionName}.fontSize` : optionName} />
);

export default OptionField;
