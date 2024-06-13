import { ModelVersion } from "services/MlModelsService";
import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.ALIASES]: string[];
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

export type AliasesFieldProps = {
  name?: string;
  modelVersion: ModelVersion;
  aliasToVersionMap: Record<string, string>;
};

export type ConflictingAliasesWarningProps = {
  modelVersion: ModelVersion;
  aliasToVersionMap: Record<string, string>;
};

export type FormButtonsProps = {
  onCancel: () => void;
  isLoading?: boolean;
};
