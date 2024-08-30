import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.NAME]: string;
};

export type RenameDataSourceFormProps = {
  name: string;
  onSubmit: (formData: FormValues) => void;
  onCancel: () => void;
  isLoading?: boolean;
};

export type FormButtonsProps = {
  onCancel: () => void;
  isLoading?: boolean;
};
