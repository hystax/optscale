import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.EMAIL]: string;
  [FIELD_NAMES.PASSWORD]: string;
};

export type LoginFormProps = {
  onSubmit: (data: FormValues) => void;
  isLoading?: boolean;
  isInvited?: boolean;
};
