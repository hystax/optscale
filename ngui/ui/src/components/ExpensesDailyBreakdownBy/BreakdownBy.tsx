import Selector from "components/Selector";
import { breakdowns } from "hooks/useBreakdownBy";

const BreakdownBy = ({ value, onChange }) => (
  <Selector
    data={{
      selected: value,
      items: breakdowns
    }}
    labelId="categorizeBy"
    onChange={onChange}
  />
);

export default BreakdownBy;
