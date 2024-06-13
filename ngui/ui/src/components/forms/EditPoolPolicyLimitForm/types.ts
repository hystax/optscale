import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.LIMIT]: string;
};

export type EditPoolPolicyLimitFormProps = {
  policyType: string;
  policyLimit: number;
  onSubmit: (formData: FormValues) => void;
  onCancel: () => void;
  isLoading?: boolean;
};
