import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.ORGANIZATION_MANAGER]: string;
};

export type DeleteEmployeeFormProps = {
  organizationName: string;
  onSubmit: (formData: FormValues) => void;
  isDeletingMyself?: boolean;
  isOnlyOneOrganizationManager?: boolean;
  isLoading?: boolean;
};
