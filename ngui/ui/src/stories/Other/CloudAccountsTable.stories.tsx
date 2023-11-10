import CloudAccountsTable from "components/CloudAccountsTable";
import { KINDS } from "stories";

export default {
  title: `${KINDS.OTHER}/CloudAccountsTable`
};

export const basic = () => <CloudAccountsTable />;
