import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.EMAIL]: string;
};

export type ResetPasswordFormProps = {
  onSubmit: (data: FormValues) => void;
  sendState: string;
  isLoading?: boolean;
};
