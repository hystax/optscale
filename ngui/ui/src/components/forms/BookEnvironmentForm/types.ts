import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.BOOKING_OWNER]: string;
  [FIELD_NAMES.BOOK_SINCE]?: number;
  [FIELD_NAMES.BOOK_UNTIL]?: number;
  [FIELD_NAMES.SELECTED_KEY_FIELD_ID]?: string;
  [FIELD_NAMES.KEY_NAME]?: string;
  [FIELD_NAMES.KEY_VALUE]?: string;
};

export type BookEnvironmentFormProps = {
  onSubmit: (data: FormValues) => void;
};

export type Owner = {
  id: string;
  name: string;
  default_ssh_key_id: string;
};

export type BookingOwnerSelectorProps = {
  owners: Owner[];
  currentEmployeeId?: string;
  isSshRequired?: boolean;
  readOnly?: boolean;
  isLoading?: boolean;
};
