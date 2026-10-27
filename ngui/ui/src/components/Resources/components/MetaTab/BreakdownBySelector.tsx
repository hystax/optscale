import { FormattedMessage } from "react-intl";
import Selector, { Item, ItemContent } from "components/Selector";
import { isEmptyArray } from "utils/arrays";
import { getMetaFormattedName } from "utils/metadata";
import { BreakdownBySelectorProps } from "./types";

const BreakdownBySelector = ({ value, onChange, metaNames, isLoading = false }: BreakdownBySelectorProps) => {
  const noMetaAvailable = isEmptyArray(metaNames);

  return (
    <Selector
      id="resources-meta-categorize-by-selector"
      labelMessageId="categorizeBy"
      value={noMetaAvailable ? "no-meta-available" : value}
      onChange={onChange}
      disabled={noMetaAvailable}
      isLoading={isLoading}
    >
      {noMetaAvailable && (
        <Item key="no-meta-available" value="no-meta-available">
          <ItemContent>
            <FormattedMessage id="noMetaAvailable" />
          </ItemContent>
        </Item>
      )}
      {metaNames
        .map((name) => ({
          value: name,
          name: getMetaFormattedName(name),
        }))
        .sort((a, b) => a.name.localeCompare(b.name))
        .map((breakdown) => (
          <Item key={breakdown.value} value={breakdown.value}>
            <ItemContent>{breakdown.name}</ItemContent>
          </Item>
        ))}
    </Selector>
  );
};

export default BreakdownBySelector;
