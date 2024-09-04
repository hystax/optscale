import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.CODE]: string;
};

export type ConfirmVerificationCodeFormProps = {
  onSubmit: (data: FormValues) => void;
  isLoading?: boolean;
};
