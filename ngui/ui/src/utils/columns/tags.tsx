import { FormattedMessage } from "react-intl";
import CopyText from "components/CopyText";
import ExpandableList from "components/ExpandableList";
import TextWithDataTestId from "components/TextWithDataTestId";
import Tooltip from "components/Tooltip";
import { isEmptyObject } from "utils/objects";
import { sliceByLimitWithEllipsis } from "utils/strings";
import { CELL_EMPTY_VALUE } from "utils/tables";

const OVERFLOW_LIMIT = 32;
const MAX_ROWS = 3;

const renderTagKey = (key: string) => {
  const isOverflow = key.length > OVERFLOW_LIMIT;
  const keyLabel = isOverflow ? sliceByLimitWithEllipsis(key, OVERFLOW_LIMIT) : key;

  return isOverflow ? (
    <Tooltip title={key} placement="top">
      <span>{keyLabel}</span>
    </Tooltip>
  ) : (
    keyLabel
  );
};

const renderTagValue = (value: string | null) => {
  if (!value) {
    return null;
  }

  const isOverflow = value.length > OVERFLOW_LIMIT;
  const valueLabel = isOverflow ? sliceByLimitWithEllipsis(value, OVERFLOW_LIMIT) : value;

  return isOverflow ? (
    <Tooltip title={value} placement="top">
      <strong>{valueLabel}</strong>
    </Tooltip>
  ) : (
    <strong>{valueLabel}</strong>
  );
};

const tags = ({
  headerDataTestId = "lbl_tags",
  headerMessageId = "tags",
  id,
  accessorKey,
  accessorFn,
  columnSelector,
  enableSorting = false,
  getTags,
  sorted = true,
}) => ({
  id,
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  columnSelector,
  accessorKey,
  accessorFn,
  enableSorting,
  cell: ({ row: { original } }) => {
    const tagsValue = getTags(original);

    if (isEmptyObject(tagsValue)) {
      return CELL_EMPTY_VALUE;
    }

    const sortedTags = sorted
      ? Object.entries(tagsValue).sort(([key1, value1], [key2, value2]) =>
          `${key1}:${value1}`.localeCompare(`${key2}:${value2}`)
        )
      : Object.entries(tagsValue);

    const renderTag = ([key, value]) => (
      <CopyText
        key={key}
        text={`${key}: ${value}`}
        sx={{ width: "fit-content", whiteSpace: "nowrap", display: "flex" }}
        dynamicCopyIcon
      >
        {renderTagKey(key)}:&nbsp;<>{renderTagValue(value)}</>
      </CopyText>
    );

    return <ExpandableList items={sortedTags} render={renderTag} maxRows={MAX_ROWS} />;
  },
});

export default tags;
