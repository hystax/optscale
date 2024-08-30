import { ModelDetails } from "services/MlModelsService";
import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.TAGS_FIELD_ARRAY.FIELD_NAME]: {
    [FIELD_NAMES.TAGS_FIELD_ARRAY.KEY]: string;
    [FIELD_NAMES.TAGS_FIELD_ARRAY.VALUE]: string;
  }[];
};

export type Tags = ModelDetails["tags"];

export type EditModelVersionTagsFormProps = {
  tags: Tags;
  onSubmit: (data: FormValues) => Promise<unknown>;
  onCancel: () => void;
  isLoadingProps: {
    isSubmitLoading: boolean;
  };
};

export type FormButtonsProps = {
  onCancel: () => void;
  isLoading?: boolean;
};
