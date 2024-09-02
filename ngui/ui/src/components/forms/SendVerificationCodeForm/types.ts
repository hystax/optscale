import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.EMAIL]: string;
};

export type SendVerificationCodeFormProps = {
  onSubmit: (data: FormValues) => void;
  isLoading?: boolean;
};
