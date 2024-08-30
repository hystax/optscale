import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.NAME]: string;
  [FIELD_NAMES.TAG_KEY]: string;
};

export type CreateClusterTypeFormProps = {
  onSubmit: (data: FormValues) => void;
  onCancel: () => void;
  isSubmitLoading?: boolean;
};

export type FormButtonsProps = {
  onCancel: () => void;
  isLoading?: boolean;
};
