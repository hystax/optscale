import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.PATH]: string;
  [FIELD_NAMES.NAME]: string;
  [FIELD_NAMES.DESCRIPTION]: string;
  [FIELD_NAMES.LABELS]: string[];
  [FIELD_NAMES.TIMESPAN_FROM]: number;
  [FIELD_NAMES.TIMESPAN_TO]: number;
};

export type FormSubmitValues = {
  description: string;
  labels: string[];
  name: string;
  path: string;
  training_set: {
    path: string;
    timespan_from?: number;
    timespan_to?: number;
  } | null;
  validation_set: {
    path: string;
    timespan_from?: number;
    timespan_to?: number;
  } | null;
};

export type MlDatasetCreateFormProps = {
  onSubmit: (data: FormSubmitValues) => void;
  onCancel: () => void;
  isLoading?: Record<string, boolean>;
};

export type MlDatasetEditFormProps = {
  onSubmit: (data: FormSubmitValues) => void;
  onCancel: () => void;
  isLoadingProps?: Record<string, boolean>;
};
