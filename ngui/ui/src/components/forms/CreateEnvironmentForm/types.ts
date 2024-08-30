import { FIELD_NAMES } from "./constants";

export type FormButtonsProps = {
  onCancel: () => void;
  isLoading?: boolean;
};

export type FormValues = {
  [FIELD_NAMES.NAME]: string;
  [FIELD_NAMES.RESOURCE_TYPE]: string;
  [FIELD_NAMES.REQUIRE_SSH_KEY]: boolean;
  [FIELD_NAMES.PROPERTIES_FIELD_ARRAY.FIELD_NAME]: Array<{
    [FIELD_NAMES.PROPERTIES_FIELD_ARRAY.PROPERTY_NAME]: string;
    [FIELD_NAMES.PROPERTIES_FIELD_ARRAY.PROPERTY_VALUE]: string;
  }>;
};

export type CreateEnvironmentFormProps = {
  onSubmit: (data: FormValues) => void;
  onCancel: () => void;
  isSubmitLoading?: boolean;
};
