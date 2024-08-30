export type CreateColumnSetFormProps = {
  onSubmit: (name: string) => Promise<unknown>;
  isLoadingProps?: {
    isSubmitLoading?: boolean;
  };
};

export type FormValues = {
  name: string;
};
