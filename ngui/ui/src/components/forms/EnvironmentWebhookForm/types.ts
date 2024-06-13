import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.WEBHOOK_URL]: string;
};

export type EnvironmentWebhookFormProps = {
  url: string;
  onSubmit: (url: string) => void;
  onCancel: () => void;
  isLoading?: boolean;
};
