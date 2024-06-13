export type CreatePoolFormValues = {
  name: string;
  limit: string;
  type: string;
  autoExtension: boolean;
};

export type EditPoolFormValues = {
  name: string;
  limit: string;
  type: string;
  defaultOwnerId: string;
  autoExtension: boolean;
};
