import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.KEY_NAME]: string;
  [FIELD_NAMES.KEY_VALUE]: string;
};

export type CreateSshKeyFormProps = {
  onSubmit: (data: FormValues) => void;
  isSubmitLoading?: boolean;
};
