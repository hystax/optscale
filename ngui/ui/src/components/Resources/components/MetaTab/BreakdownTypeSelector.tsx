import { FormattedMessage } from "react-intl";
import Selector, { Item, ItemContent } from "components/Selector";
import { BREAKDOWN_TYPE } from "./constants";
import { BreakdownTypeSelectorProps } from "./types";

const items = [
  {
    value: BREAKDOWN_TYPE.EXPENSES,
    name: <FormattedMessage id="expenses" />,
  },
  {
    value: BREAKDOWN_TYPE.EXPENSES_PERCENT,
    name: <FormattedMessage id="expensesPercentage" />,
  },
  {
    value: BREAKDOWN_TYPE.COUNT,
    name: <FormattedMessage id="count" />,
  },
  {
    value: BREAKDOWN_TYPE.COUNT_PERCENT,
    name: <FormattedMessage id="countPercentage" />,
  },
];

const BreakdownTypeSelector = ({ value, onChange }: BreakdownTypeSelectorProps) => (
  <Selector id="resources-meta-breakdown-type-selector" labelMessageId="breakdownType" value={value} onChange={onChange}>
    {items.map(({ value: itemValue, name: itemName }) => (
      <Item key={itemValue} value={itemValue}>
        <ItemContent>{itemName}</ItemContent>
      </Item>
    ))}
  </Selector>
);

export default BreakdownTypeSelector;
