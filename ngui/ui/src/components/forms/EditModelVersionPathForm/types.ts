import { ModelVersion } from "services/MlModelsService";
import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.PATH]: string;
};

export type EditModelVersionPathFormProps = {
  modelVersion: ModelVersion;
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
