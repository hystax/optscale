import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.COST]: string;
};

export type UpdateDataSourceSkuFormProps = {
  sku: string;
  cost: number;
  onSubmit: (data: FormValues) => void;
  onCancel: () => void;
  isLoading?: boolean;
};

export type FormButtonsProps = {
  onCancel: () => void;
  isLoading?: boolean;
};
