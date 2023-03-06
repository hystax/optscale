import React from "react";
import PropTypes from "prop-types";
import CopyText from "components/CopyText";
import ExpandableList from "components/ExpandableList";
import KeyValueLabel from "components/KeyValueLabel";
import Tooltip from "components/Tooltip";
import { sliceByLimitWithEllipsis } from "utils/strings";

// TODO - copy icon appears only on value hover, but key + value is copied, enable the icon appear on a "key: value" string hover
const copyTextWrapper = (copyValue, text, dataTestId) => (
  <CopyText dataTestIds={{ text: dataTestId }} variant="inherit" copyIconType="animated" text={text}>
    {copyValue}
  </CopyText>
);

const renderItems =
  (limit) =>
  ([key, value], index) => {
    let tag;
    const keyLength = key.length;
    const valueLength = value.length;
    const text = `${key}: ${value}`;
    const dataTestIdIndex = index;
    if (keyLength + valueLength < limit) {
      tag = (
        <KeyValueLabel
          dataTestIds={{ key: `lbl_tags_key_${dataTestIdIndex}`, value: `lbl_tags_value_${dataTestIdIndex}` }}
          key={key}
          text={key}
          value={() => copyTextWrapper(value, text)}
        />
      );
    } else {
      const cutValueLengthLimit = limit - keyLength;
      const cutKey = sliceByLimitWithEllipsis(key, limit);
      const cutValue = sliceByLimitWithEllipsis(value, cutValueLengthLimit);
      tag = (
        <Tooltip
          key={key}
          title={
            <KeyValueLabel
              text={key}
              value={value}
              style={{ flexWrap: "wrap", wordBreak: "break-all", whiteSpace: "break-spaces" }}
            />
          }
          placement="top"
        >
          {keyLength < limit ? (
            <KeyValueLabel
              dataTestIds={{ key: `lbl_tags_key_${dataTestIdIndex}`, value: `lbl_tags_value_${dataTestIdIndex}` }}
              text={key}
              value={() => copyTextWrapper(cutValue, text)}
            />
          ) : (
            <span>{copyTextWrapper(cutKey, text, `lbl_tags_key_${dataTestIdIndex}`)}</span>
          )}
        </Tooltip>
      );
    }
    return tag;
  };

const CollapsableTableCell = ({ tags, limit = 64, sorted = true, maxRows = undefined }) => {
  const tagsArray = sorted ? Object.entries(tags).sort() : Object.entries(tags);

  return <ExpandableList items={tagsArray} render={renderItems(limit)} maxRows={maxRows} />;
};

CollapsableTableCell.propTypes = {
  tags: PropTypes.object.isRequired,
  maxRows: PropTypes.number,
  limit: PropTypes.number,
  sorted: PropTypes.bool
};

export default CollapsableTableCell;
