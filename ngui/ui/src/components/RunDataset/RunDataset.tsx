import { Typography } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import DatasetName from "components/DatasetName/DatasetName";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import LabelChip from "components/LabelChip";
import SlicedText from "components/SlicedText";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { EN_FULL_FORMAT, format, secondsToMilliseconds } from "utils/datetime";

const DatasetTimespan = ({ timespanFrom, timespanTo }) => {
  const intl = useIntl();

  const formatTime = (secondsTimestamp) => format(secondsToMilliseconds(secondsTimestamp), EN_FULL_FORMAT);

  const fromLabel = intl.formatMessage({ id: "from" }).toLocaleLowerCase();
  const toLabel = intl
    .formatMessage({
      id: "to"
    })
    .toLocaleLowerCase();

  if (timespanFrom && timespanTo) {
    return `${fromLabel} ${formatTime(timespanFrom)} ${toLabel} ${formatTime(timespanTo)}`;
  }
  if (timespanFrom) {
    return `${fromLabel} ${formatTime(timespanFrom)}`;
  }
  if (timespanTo) {
    return `${toLabel} ${formatTime(timespanTo)}`;
  }
  return "-";
};

const RunDataset = ({ dataset }) => {
  const { name, deleted, path, labels = [], timespan_from: timespanFrom, timespan_to: timespanTo } = dataset;

  return (
    <>
      <KeyValueLabel key="id" keyMessageId="id" value={<SlicedText limit={60} text={path} />} />
      <KeyValueLabel
        key="name"
        keyMessageId="name"
        value={name ? <DatasetName name={<SlicedText limit={60} text={name} />} deleted={deleted} /> : undefined}
      />
      <Typography
        key="labels"
        component="div"
        sx={{
          whiteSpace: "normal",
          overflowWrap: "anywhere",
          display: "flex",
          alignItems: "center",
          gap: 0.5,
          flexWrap: "wrap"
        }}
      >
        <FormattedMessage id="labels" />
        &#58;
        {!isEmptyArray(labels) ? labels.map((label) => <LabelChip key={label} label={label} />) : <span>-</span>}
      </Typography>
      <KeyValueLabel
        key="timespan"
        keyMessageId="timespan"
        value={<DatasetTimespan timespanFrom={timespanFrom} timespanTo={timespanTo} />}
      />
    </>
  );
};

export default RunDataset;
