import { FormEvent } from "react";
import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.DATA_SOURCES]: string[];
  [FIELD_NAMES.BUCKETS]: Record<string, boolean>;
  [FIELD_NAMES.SIZE]: string;
};

export type CreateS3DuplicateFinderCheckFormProps = {
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onCancel: () => void;
  isLoadingProps?: {
    isSubmitLoading?: boolean;
    isGetBucketsLoading?: boolean;
  };
};

export type FormButtonsProps = {
  onCancel: () => void;
  isLoading?: boolean;
};
