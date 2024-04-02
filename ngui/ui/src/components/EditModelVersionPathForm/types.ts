import { ModelVersion } from "services/MlModelsService";
import { FIELD_NAMES } from "./FormElements";

export type FormValues = {
  [FIELD_NAMES.PATH_FIELD_NAME]: string;
};

export type EditModelVersionAliasFormProps = {
  modelVersion: ModelVersion;
  onSubmit: (data: FormValues) => Promise<unknown>;
  onCancel: () => void;
  isLoadingProps: {
    isSubmitLoading: boolean;
  };
};
