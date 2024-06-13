import { ObjectValues } from "utils/types";
import { FIELD_NAMES, REASONS } from "./constants";

export type Reason = ObjectValues<typeof REASONS>;

export type FormValues = {
  [FIELD_NAMES.REASON]: Reason | "";
  [FIELD_NAMES.OTHER_REASON]: string;
  [FIELD_NAMES.MISSING_CAPABILITIES]: string;
};

export type DisconnectCloudAccountFormProps = {
  // TODO TS: Define union type for "type" consisting of all disconnectable data source types
  type: string;
  parentId: string;
  onSubmit: (params: FormValues) => void;
  onCancel: () => void;
  isLoading?: boolean;
  isLastDataSource?: boolean;
};
