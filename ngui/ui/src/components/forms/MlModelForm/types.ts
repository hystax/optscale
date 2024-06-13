import { ModelDetails } from "services/MlModelsService";
import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.NAME]: string;
  [FIELD_NAMES.KEY]: string;
  [FIELD_NAMES.DESCRIPTION]: string;
  [FIELD_NAMES.TAGS_FIELD_ARRAY.FIELD_NAME]: {
    [FIELD_NAMES.TAGS_FIELD_ARRAY.KEY]: string;
    [FIELD_NAMES.TAGS_FIELD_ARRAY.VALUE]: string;
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
