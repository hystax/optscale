import { Box } from "@mui/material";
import { useFormContext, useWatch } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { Selector, TextInput } from "components/forms/common/fields";
import { ItemContent } from "components/Selector";
import { ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { MAPPING_SOURCE_TYPES } from "../constants";
import type { MappingSourceType } from "../types";
import { hasTemplatePlaceholder } from "../validation";
import ColumnsField from "./ColumnsField";

type MappingStepSourceProps = {
  // Path of the step in the form values, e.g. "focusMapping.cost.chain.0"
  name: string;
  index: number;
};

const SOURCE_TYPE_ITEMS: { value: MappingSourceType; messageId: string }[] = [
  { value: MAPPING_SOURCE_TYPES.COLUMNS, messageId: "columns" },
  { value: MAPPING_SOURCE_TYPES.VALUE, messageId: "focusMappingConstant" },
  { value: MAPPING_SOURCE_TYPES.TEMPLATE, messageId: "focusMappingTemplate" },
];

// One step of a chain: a list of columns (the first non-empty one wins), a constant or a template
const MappingStepSource = ({ name, index }: MappingStepSourceProps) => {
  const intl = useIntl();

  const { control } = useFormContext();

  const sourceType: MappingSourceType = useWatch({ control, name: `${name}.sourceType` });

  return (
    <Box flexGrow={1} minWidth={0}>
      <Box display="flex" gap={SPACING_1} flexWrap="wrap" alignItems="flex-start">
        <Box flexBasis={ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH.MEDIUM}>
          <Selector
            name={`${name}.sourceType`}
            id={`${name}-source-type-selector`}
            // The first step is the source, each next one is a fallback of the previous one
            labelMessageId={index === 0 ? "source" : "focusMappingFallback"}
            fullWidth
            items={SOURCE_TYPE_ITEMS.map(({ value, messageId }) => ({
              value,
              content: (
                <ItemContent>
                  <FormattedMessage id={messageId} />
                </ItemContent>
              ),
            }))}
          />
        </Box>
        <Box flexGrow={1} flexBasis={ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH.LARGE} minWidth={0}>
          {sourceType === MAPPING_SOURCE_TYPES.COLUMNS && <ColumnsField name={`${name}.columns`} />}
          {sourceType === MAPPING_SOURCE_TYPES.VALUE && (
            <TextInput
              name={`${name}.value`}
              // The API accepts any string, an empty or blank one included, of any length
              maxLength={null}
              validate={{ notOnlyWhiteSpaces: () => true }}
              dataTestId={`input_${name}.value`}
              label={<FormattedMessage id="focusMappingConstant" />}
            />
          )}
          {sourceType === MAPPING_SOURCE_TYPES.TEMPLATE && (
            <TextInput
              name={`${name}.template`}
              required
              // The API has no length limit for a template
              maxLength={null}
              dataTestId={`input_${name}.template`}
              label={<FormattedMessage id="focusMappingTemplate" />}
              placeholder="{ServiceName}/{SkuId}"
              validate={{
                placeholder: (template: string | undefined) =>
                  hasTemplatePlaceholder(template) || intl.formatMessage({ id: "focusMappingTemplatePlaceholderRequired" }),
              }}
            />
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default MappingStepSource;
