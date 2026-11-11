import { Box } from "@mui/material";
import { useFieldArray, useFormContext } from "react-hook-form";
import { SPACING_1 } from "utils/layouts";
import { getEmptyMappingStep } from "../mapping";
import AddRowButton from "./AddRowButton";
import MappingStepSource from "./MappingStepSource";
import OrderedRowActions from "./OrderedRowActions";

type MappingChainFieldArrayProps = {
  // Path of the mapping field in the form values, e.g. "focusMapping.cost"
  fieldName: string;
};

// The ordered chain of a field: the first step is the field's source, each next step is the fallback of the previous one
const MappingChainFieldArray = ({ fieldName }: MappingChainFieldArrayProps) => {
  const { control } = useFormContext();

  const name = `${fieldName}.chain`;

  const { fields, append, remove, move } = useFieldArray({ control, name });

  return (
    <>
      {fields.map((item, index) => {
        const stepName = `${name}.${index}`;

        return (
          <Box key={item.id} display="flex" gap={SPACING_1} alignItems="flex-start">
            <MappingStepSource name={stepName} index={index} />
            <OrderedRowActions
              rowName={stepName}
              index={index}
              rowsCount={fields.length}
              onMove={move}
              onRemove={remove}
              // A field that is overridden needs a source
              isRemoveDisabled={fields.length === 1}
            />
          </Box>
        );
      })}
      <AddRowButton
        messageId="focusMappingAddFallback"
        onClick={() => append(getEmptyMappingStep())}
        dataTestId={`btn_${fieldName}_add_fallback`}
      />
    </>
  );
};

export default MappingChainFieldArray;
