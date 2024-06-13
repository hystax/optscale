import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.NAME]: string;
};

export type CreateOrganizationFormProps = {
  onSubmit: (data: FormValues) => void;
  onCancel: () => void;
  isLoading: boolean;
};

export type FormButtonsProps = {
  onCancel: () => void;
  isLoading?: boolean;
};
