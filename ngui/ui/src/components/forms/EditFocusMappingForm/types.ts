import { FOCUS_MAPPING_FIELD_NAME, type ApiMapping, type FocusMappingFormValues } from "components/FocusMappingEditor";

export type FormValues = {
  [FOCUS_MAPPING_FIELD_NAME]: FocusMappingFormValues;
};

export type EditFocusMappingFormProps = {
  // Stored mapping of the data source (config.mapping)
  mapping?: ApiMapping | null;
  // null resets the mapping to defaults
  onSubmit: (mapping: ApiMapping | null) => void;
  onCancel: () => void;
  isLoading?: boolean;
};

export type FormButtonsProps = {
  onCancel: () => void;
  onReset: () => void;
  isResetDisabled: boolean;
  isLoading: boolean;
};
