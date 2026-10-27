import { TODO } from "utils/types";

export type UpdateDataSourceCredentialsContainerProps = {
  id: string;
  type: string;
  config: TODO;
  closeSideModal: () => void;
};

export type Config = {
  linked: boolean;
  assume_role_account_id: string;
  assume_role_name: string;
  assume_role_external_id?: string;
};

export type Params = {
  config: Config;
};
