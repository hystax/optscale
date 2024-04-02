import { ModelDetails } from "services/MlModelsService";
import { FIELD_NAMES } from "./FormElements";

export type FormValues = {
  [FIELD_NAMES.NAME_FIELD_NAME]: string;
  [FIELD_NAMES.KEY_FIELD_NAME]: string;
  [FIELD_NAMES.DESCRIPTION_FIELD_NAME]: string;
  [FIELD_NAMES.TAGS_FIELD_ARRAY.FIELD_NAME]: {
    [FIELD_NAMES.TAGS_FIELD_ARRAY.KEY_FIELD_NAME]: string;
    [FIELD_NAMES.TAGS_FIELD_ARRAY.VALUE_FIELD_NAME]: string;
  }[];
};

export type MlCreateModelFormProps = {
  onSubmit: (data: FormValues) => Promise<unknown>;
  onCancel: () => void;
  isLoadingProps?: {
    isSubmitLoading?: boolean;
  };
};

export type MlEditModelFormProps = {
  model: ModelDetails;
  onSubmit: (data: FormValues) => Promise<unknown>;
  onCancel: () => void;
  isLoadingProps?: {
    isGetDataLoading?: boolean;
    isSubmitLoading?: boolean;
  };
};
