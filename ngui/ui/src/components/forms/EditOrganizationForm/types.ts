import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.ORGANIZATION_NAME]: string;
};

export type EditOrganizationFormProps = {
  currentOrganizationName: string;
  onSubmit: (data: FormValues) => void;
  onCancel: () => void;
  isLoading?: boolean;
};
