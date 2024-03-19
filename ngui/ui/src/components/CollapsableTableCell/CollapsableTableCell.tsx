import { Typography } from "@mui/material";
import CopyTextComponent from "components/CopyText";
import ExpandableList from "components/ExpandableList";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import Tooltip from "components/Tooltip";
import { sliceByLimitWithEllipsis } from "utils/strings";

/**
 * TODO - copy icon appears only on value hover, but key + value is copied,
 * enable the icon appear on a "key: value" string hover
 */
const CopyText = ({ children, textToCopy, dataTestId }) => (
  <CopyTextComponent
    dataTestIds={{ text: dataTestId }}
    variant="inherit"
    copyIconType="animated"
    text={textToCopy}
    sx={{ fontWeight: "inherit", display: "inline-flex" }}
  >
    {children}
  </CopyTextComponent>
);

const renderItems =
  (limit) =>
  ([key, value], index) => {
    const stringKey = String(key);
    const stringValue = String(value);

    const keyLength = stringKey.length;
    const valueLength = stringValue.length;

    const displayedKey = sliceByLimitWithEllipsis(stringKey, limit);

    const dataTestIdIndex = index;

    const renderTag = () => {
      if (value === null) {
        return (
          <Typography>
            <CopyText textToCopy={stringKey}>{displayedKey}</CopyText>
          </Typography>
        );
      }

      const textToCopy = `${stringKey}: ${stringValue}`;

      if (keyLength + valueLength < limit) {
        return (
          <KeyValueLabel
            dataTestIds={{ key: `lbl_tags_key_${dataTestIdIndex}`, value: `lbl_tags_value_${dataTestIdIndex}` }}
            key={displayedKey}
            keyText={displayedKey}
            value={<CopyText textToCopy={textToCopy}>{value}</CopyText>}
          />
        );
      }

      const cutValueLengthLimit = limit - keyLength;
      const cutValue = sliceByLimitWithEllipsis(stringValue, cutValueLengthLimit);

      if (keyLength < limit) {
        return (
          <KeyValueLabel
            dataTestIds={{ key: `lbl_tags_key_${dataTestIdIndex}`, value: `lbl_tags_value_${dataTestIdIndex}` }}
            keyText={key}
            value={<CopyText textToCopy={textToCopy}>{cutValue}</CopyText>}
          />
        );
      }

      return <CopyText textToCopy={textToCopy}>{displayedKey}</CopyText>;
    };

    const getTooltipTitle = () => {
      if (value === null) {
        if (keyLength < limit) {
          return undefined;
        }
        return stringKey;
      }

      if (keyLength + valueLength < limit) {
        return undefined;
      }

      return (
        <span style={{ overflowWrap: "anywhere" }}>
          <KeyValueLabel keyText={key} value={value} />
        </span>
      );
    };

    return (
      <Tooltip key={key} title={getTooltipTitle()} placement="top">
        <span>{renderTag()}</span>
      </Tooltip>
    );
  };

const getTagItems = ({ tags, sorted }) => {
  const entries = Object.entries(tags);
  const sortedEntries = sorted ? entries.sort() : entries;

  return sortedEntries;
};

const CollapsableTableCell = ({ tags, limit = 64, sorted = true, maxRows = undefined }) => (
  <ExpandableList items={getTagItems({ tags, sorted })} render={renderItems(limit)} maxRows={maxRows} />
);

export default CollapsableTableCell;
