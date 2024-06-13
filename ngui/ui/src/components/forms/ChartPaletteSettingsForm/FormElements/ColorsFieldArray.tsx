import SquareIcon from "@mui/icons-material/Square";
import { useFieldArray, useFormContext } from "react-hook-form";
import { TextInput } from "components/forms/common/fields";

const ColorsFieldArray = ({ fieldName, options }) => {
  const { control } = useFormContext();

  const { fields } = useFieldArray({
    control,
    name: fieldName
  });

  return fields.map((field, index) => (
    <TextInput
      key={field.id}
      label={index + 1}
      name={`${fieldName}.${index}.color`}
      InputProps={{
        endAdornment: <SquareIcon style={{ border: "1px dashed black", color: options[index] }} />
      }}
    />
  ));
};

export default ColorsFieldArray;
