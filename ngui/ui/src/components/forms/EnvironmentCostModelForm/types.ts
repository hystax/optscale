import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.HOURLY_PRICE]: number;
};

export type FormButtonsProps = {
  onCancel: () => void;
  isLoading?: boolean;
};

export type EnvironmentCostModelFormProps = {
  defaultHourlyPrice: number;
  onSubmit: (data: FormValues) => void;
  onCancel: () => void;
  isLoading: boolean;
};
