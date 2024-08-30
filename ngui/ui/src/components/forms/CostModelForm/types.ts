import { FIELD_NAMES } from "./constants";

export type FormButtonsProps = {
  onCancel: () => void;
  isLoading?: boolean;
};

export type FormValues = {
  [FIELD_NAMES.CPU_PER_HOUR]: string;
  [FIELD_NAMES.MEMORY_PER_HOUR]: string;
};

export type CostModelFormProps = {
  cpuHour: number;
  memoryMbHour: number;
  onSubmit: (data: FormValues) => void;
  onCancel: () => void;
  isLoading?: boolean;
};
