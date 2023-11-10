import { RegionExpensesMocked } from "components/RegionExpenses";
import { KINDS } from "stories";

export default {
  title: `${KINDS.PAGES}/RegionExpenses`
};

export const basic = () => <RegionExpensesMocked />;
