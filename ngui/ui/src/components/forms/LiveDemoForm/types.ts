import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.EMAIL]: string;
  [FIELD_NAMES.SUBSCRIBE_TO_NEWSLETTER]: boolean;
};

export type LiveDemoFormProps = {
  onSubmit: (data: FormValues) => void;
};
