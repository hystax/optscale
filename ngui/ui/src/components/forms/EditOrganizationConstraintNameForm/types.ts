import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.NAME]: string;
};

export type EditOrganizationConstraintNameFormProps = {
  defaultName: string;
  onCancel: () => void;
  onSubmit: (newName: FormValues) => void;
  isLoading?: boolean;
};
