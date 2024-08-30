import { Artifact } from "services/MlArtifactsService";
import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.PATH]: string;
  [FIELD_NAMES.NAME]: string;
  [FIELD_NAMES.DESCRIPTION]: string;
  [FIELD_NAMES.TAGS_FIELD_ARRAY.FIELD_NAME]: {
    [FIELD_NAMES.TAGS_FIELD_ARRAY.KEY]: string;
    [FIELD_NAMES.TAGS_FIELD_ARRAY.VALUE]: string;
  }[];
};

export type FormSubmitValues = {
  name: string;
  description: string;
  path: string;
  tags: Record<string, string>;
};

export type MlCreateArtifactFormProps = {
  onSubmit: (data: FormSubmitValues) => void;
  onCancel: () => void;
  isLoadingProps?: { isCreateArtifactLoading?: boolean };
};

export type MlEditArtifactFormProps = {
  artifact: Partial<Artifact>;
  onSubmit: (data: FormSubmitValues) => void;
  onCancel: () => void;
  isLoadingProps?: {
    isGetArtifactLoading?: boolean;
    isUpdateArtifactLoading?: boolean;
  };
};
