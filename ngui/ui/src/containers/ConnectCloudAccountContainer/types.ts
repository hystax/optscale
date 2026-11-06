export type Config = {
  linked: boolean;
  assume_role_account_id: string;
  assume_role_name: string;
  assume_role_external_id: string;
};

export type Params = {
  name: string;
  type: string;
  config: Config;
  // FOCUS field mapping, a top-level parameter; absent when every field is left on defaults
  mapping?: Record<string, unknown>;
  // Sent for FOCUS only; absent, the API turns the scheduled import on
  autoImport?: boolean;
};
