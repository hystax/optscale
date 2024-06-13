import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.REQUIRING_ATTENTION]: string;
  [FIELD_NAMES.CRITICAL]: string;
};

export type S3DuplicateFinderSettingsFormProps = {
  requiringAttention: number;
  critical: number;
  onCancel: () => void;
  onSubmit: (data: FormValues) => void;
  isLoadingProps?: { isGetDataLoading?: boolean; isSubmitLoading?: boolean };
};

export type DefaultValuesParams = {
  [FIELD_NAMES.REQUIRING_ATTENTION]?: number;
  [FIELD_NAMES.CRITICAL]?: number;
};
