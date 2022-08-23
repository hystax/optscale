import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import CopyText from "components/CopyText";
import DashedTypography from "components/DashedTypography";
import KeyValueLabel from "components/KeyValueLabel";
import Tooltip from "components/Tooltip";
import { useToggle } from "hooks/useToggle";
import { sliceByLimitWithEllipsis } from "utils/strings";

// TODO - copy icon appears only on value hover, but key + value is copied, enable the icon appear on a "key: value" string hover
const copyTextWrapper = (copyValue, text, dataTestId) => (
  <CopyText dataTestIds={{ text: dataTestId }} variant="inherit" copyIconType="animated" text={text}>
    {copyValue}
  </CopyText>
);

const renderItems = (tags, limit, startWithIndex = 0) =>
  tags.map(([key, value], index) => {
    let tag;
    const keyLength = key.length;
    const valueLength = value.length;
    const text = `${key}: ${value}`;
    const dataTestIdIndex = index + startWithIndex;
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
          title={<KeyValueLabel text={key} value={value} style={{ flexWrap: "wrap", wordBreak: "break-all" }} />}
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
  });

const CollapsableTableCell = ({ tags, limit = 64, sorted = true, maxRows = undefined }) => {
  const [isExpanded, setIsExpanded] = useToggle(false);
  const tagsArray = sorted ? Object.entries(tags).sort() : Object.entries(tags);

  const expander = () =>
    isExpanded ? (
      <>
        {renderItems(tagsArray.slice(maxRows), limit, maxRows)}
        <DashedTypography onClick={() => setIsExpanded()}>
          <FormattedMessage id="showLess" />
        </DashedTypography>
      </>
    ) : (
      <DashedTypography onClick={() => setIsExpanded()}>
        <FormattedMessage id="showMore" />
      </DashedTypography>
    );

  return (
    <>
      {renderItems(tagsArray.slice(0, maxRows), limit)}
      {!!maxRows && maxRows < tagsArray.length && expander()}
    </>
  );
};

CollapsableTableCell.propTypes = {
  tags: PropTypes.object,
  maxRows: PropTypes.number,
  limit: PropTypes.number,
  sorted: PropTypes.bool
};

export default CollapsableTableCell;
