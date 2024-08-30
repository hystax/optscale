import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.EMAIL]: string;
  [FIELD_NAMES.FULL_NAME]: string;
  [FIELD_NAMES.PASSWORD]: string;
  [FIELD_NAMES.CONFIRM_PASSWORD]: string;
};

export type RegistrationFormProps = {
  onSubmit: (data: FormValues) => void;
  isLoading?: boolean;
  isInvited?: boolean;
};
