import { Box, FormLabel } from "@mui/material";
import { useFieldArray, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";
import { ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { isValidRegex } from "utils/validation";
import type { ResourceTypeRule } from "../types";
import AddRowButton from "./AddRowButton";
import OrderedRowActions from "./OrderedRowActions";
import ResourceTypeField from "./ResourceTypeField";

type ResourceTypeRulesFieldArrayProps = {
  // Path of the resource type field in the form values, e.g. "focusMapping.resourceType"
  fieldName: string;
};

const getEmptyRule = (): ResourceTypeRule => ({ column: "", match: "", type: "" });

// Ordered rules {column, match, type} of the resource type: the first rule whose regex matches the column value wins
const ResourceTypeRulesFieldArray = ({ fieldName }: ResourceTypeRulesFieldArrayProps) => {
  const intl = useIntl();

  const { control } = useFormContext();

  const name = `${fieldName}.rules`;

  const { fields, append, remove, move } = useFieldArray({ control, name });

  return (
    <Box mb={SPACING_1}>
      <Box display="flex" alignItems="center" mb={0.25}>
        <FormLabel>
          <FormattedMessage id="focusMappingTypeRules" />
        </FormLabel>
        <QuestionMark messageId="focusMappingTypeRulesDescription" dataTestId={`qmark_${fieldName}.rules`} fontSize="small" />
      </Box>
      {fields.map((item, index) => {
        const ruleName = `${name}.${index}`;

        return (
          <Box key={item.id} display="flex" gap={SPACING_1} alignItems="flex-start">
            <Box flexGrow={1} minWidth={0}>
              <Box display="flex" gap={SPACING_1} flexWrap="wrap" alignItems="flex-start">
                <Box flexGrow={1} flexBasis={ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH.MEDIUM}>
                  <TextInput
                    name={`${ruleName}.column`}
                    required
                    // Only the type of a rule has a length limit in the API
                    maxLength={null}
                    dataTestId={`input_${ruleName}.column`}
                    label={<FormattedMessage id="focusMappingRuleColumn" />}
                  />
                </Box>
                <Box flexGrow={1} flexBasis={ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH.MEDIUM}>
                  <TextInput
                    name={`${ruleName}.match`}
                    required
                    maxLength={null}
                    dataTestId={`input_${ruleName}.match`}
                    label={<FormattedMessage id="focusMappingRuleMatch" />}
                    validate={{
                      // The server compiles the regex with RE2, an inline (?i) prefix is accepted
                      regex: (match: string | undefined) =>
                        isValidRegex(match ?? "") || intl.formatMessage({ id: "focusMappingInvalidRuleMatch" }),
                    }}
                    InputProps={{
                      endAdornment: (
                        <QuestionMark messageId="focusMappingRuleMatchTooltip" dataTestId={`qmark_${ruleName}.match`} />
                      ),
                    }}
                  />
                </Box>
                <Box flexGrow={1} flexBasis={ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH.MEDIUM}>
                  <ResourceTypeField name={`${ruleName}.type`} />
                </Box>
              </Box>
            </Box>
            <OrderedRowActions rowName={ruleName} index={index} rowsCount={fields.length} onMove={move} onRemove={remove} />
          </Box>
        );
      })}
      <AddRowButton messageId="addRule" onClick={() => append(getEmptyRule())} dataTestId={`btn_${fieldName}_add_rule`} />
    </Box>
  );
};

export default ResourceTypeRulesFieldArray;
