import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.PROPERTY_NAME]: string;
  [FIELD_NAMES.PROPERTY_VALUE]: string;
};

export type EnvironmentPropertyFormProps = {
  defaultPropertyName: string;
  defaultPropertyValue: string;
  onSubmit: (data: FormValues) => void;
  onCancel: () => void;
  existingProperties: Record<string, string>;
  isLoading?: boolean;
  isEdit?: boolean;
};
