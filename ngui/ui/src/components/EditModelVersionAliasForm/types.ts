import { ModelVersion } from "services/MlModelsService";
import { FIELD_NAMES } from "./FormElements";

export type FormValues = {
  [FIELD_NAMES.ALIASES_FIELD_NAME]: string[];
};

export type EditModelVersionAliasFormProps = {
  modelVersion: ModelVersion;
  onSubmit: (data: FormValues) => Promise<unknown>;
  aliasToVersionMap: Record<string, string>;
  onCancel: () => void;
  isLoadingProps: {
    isSubmitLoading: boolean;
  };
};
