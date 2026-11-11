import { ReactNode } from "react";
import { Box, Stack, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import FormContentDescription from "components/FormContentDescription";
import { SPACING_1 } from "utils/layouts";
import { MAPPING_FIELDS } from "./constants";
import {
  DecimalSeparatorField,
  MappingFieldBlock,
  NormalizeField,
  ResourceTypeRulesFieldArray,
  TagsMappingFieldBlock,
} from "./FormElements";
import type { MappingFieldKey } from "./types";

type FocusMappingEditorProps = {
  // Path of the mapping form values (FocusMappingFormValues) in the form, e.g. "focusMapping"
  name: string;
  // The "Field mapping (optional)" heading of the Connect form; a form that is all about the mapping hides it
  showTitle?: boolean;
};

type FieldBlockProps = {
  name: string;
  labelMessageId: string;
  dataTestId: string;
};

type RenderFieldParameters = (fieldName: string) => ReactNode;

// Field-level parameters of an overridden field, shown below its chain.
// They exist only at field level, never inside a fallback.
const FIELD_PARAMETERS: Partial<Record<MappingFieldKey, RenderFieldParameters>> = {
  cost: (fieldName) => <DecimalSeparatorField name={`${fieldName}.decimalSeparator`} />,
  resourceId: (fieldName) => <NormalizeField name={`${fieldName}.normalize`} />,
  // The rules are checked before the source, their description says so
  resourceType: (fieldName) => <ResourceTypeRulesFieldArray fieldName={fieldName} />,
};

const FieldBlock = ({ fieldKey, ...props }: FieldBlockProps & { fieldKey: MappingFieldKey }) => {
  if (fieldKey === "tags") {
    return <TagsMappingFieldBlock {...props} />;
  }

  return <MappingFieldBlock {...props}>{FIELD_PARAMETERS[fieldKey]?.(props.name)}</MappingFieldBlock>;
};

// Structured editor of the FOCUS field mapping, bound to a sub-tree of the form values of the parent form
// (react-hook-form context). It has no data fetching, so it is used by both the Connect and the Edit mapping forms.
const FocusMappingEditor = ({ name, showTitle = true }: FocusMappingEditorProps) => (
  <Box mb={2}>
    {showTitle && (
      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
        <FormattedMessage id="focusFieldMapping" />
      </Typography>
    )}
    {/* Adds up with the bottom margin of the description to a larger gap above the cards */}
    <Box mb={SPACING_1}>
      <FormContentDescription fullWidth alertProps={{ messageId: "focusMappingDescription" }} />
    </Box>
    <Stack spacing={SPACING_1}>
      {MAPPING_FIELDS.map(({ key, messageId }) => (
        <FieldBlock
          key={key}
          fieldKey={key}
          name={`${name}.${key}`}
          labelMessageId={messageId}
          dataTestId={`focus_mapping_${key}`}
        />
      ))}
    </Stack>
  </Box>
);

export default FocusMappingEditor;
