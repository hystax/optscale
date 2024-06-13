import { FIELD_NAMES } from "./constants";

export type FormButtonsProps = {
  onCancel: () => void;
  isLoading?: boolean;
};

export type FormValues = {
  [FIELD_NAMES.OPTION_NAME]: string;
};

export type OrganizationOptionFormProps = {
  onSubmit: (organizationOptionName: string, value: Record<string, unknown>) => void;
  onCancel: () => void;
  isLoading?: boolean;
};
