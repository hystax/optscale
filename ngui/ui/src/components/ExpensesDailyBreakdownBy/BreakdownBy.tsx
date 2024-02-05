import Selector, { Item, ItemContent } from "components/Selector";
import { breakdowns } from "hooks/useBreakdownBy";

type BreakdownByProps = {
  value: string;
  onChange: (value: string) => void;
};

const BreakdownBy = ({ value, onChange }: BreakdownByProps) => (
  <Selector id="resource-categorize-by-selector" labelMessageId="categorizeBy" value={value} onChange={onChange}>
    {breakdowns.map((breakdown) => (
      <Item key={breakdown.value} value={breakdown.value}>
        <ItemContent>{breakdown.name}</ItemContent>
      </Item>
    ))}
  </Selector>
);

export default BreakdownBy;
