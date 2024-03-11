import { Typography } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import DatasetName from "components/DatasetName/DatasetName";
import ExpandableList from "components/ExpandableList";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import LabelChip from "components/LabelChip";
import SlicedText from "components/SlicedText";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { EN_FULL_FORMAT, formatUTC } from "utils/datetime";

const DatasetTimespan = ({ timespanFrom, timespanTo }) => {
  const intl = useIntl();

  const formatTime = (timestamp) => formatUTC(timestamp, EN_FULL_FORMAT);

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
  const { name, deleted, path, labels = [], training_set: trainingSet, validation_set: validationSet } = dataset;

  const { path: trainingSetPathId, timespan_from: trainingSetTimespanFrom, timespan_to: trainingSetTimespanTo } =
    // training_set field requires a strict field structure, and null is valid response representing an empty value
    trainingSet ?? {};

  const { path: validationSetPathId, timespan_from: validationSetTimespanFrom, timespan_to: validationSetTimespanTo } =
    // validation_set field requires a strict field structure, and null is valid response representing an empty value
    validationSet ?? {};

  return (
    <ExpandableList
      items={[
        <KeyValueLabel key="id" keyMessageId="id" value={<SlicedText limit={60} text={path} />} />,
        <KeyValueLabel
          key="name"
          keyMessageId="name"
          value={name ? <DatasetName name={<SlicedText limit={60} text={name} />} deleted={deleted} /> : undefined}
        />,
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
        </Typography>,
        <KeyValueLabel
          key="training"
          keyMessageId="training"
          value={trainingSetPathId ? <SlicedText limit={60} text={trainingSetPathId} /> : undefined}
        />,
        <KeyValueLabel
          key="trainingTimespan"
          keyMessageId="trainingTimespan"
          value={<DatasetTimespan timespanFrom={trainingSetTimespanFrom} timespanTo={trainingSetTimespanTo} />}
        />,
        <KeyValueLabel
          key="validation"
          keyMessageId="validation"
          value={validationSetPathId ? <SlicedText limit={60} text={validationSetPathId} /> : undefined}
        />,
        <KeyValueLabel
          key="validationTimespan"
          keyMessageId="validationTimespan"
          value={<DatasetTimespan timespanFrom={validationSetTimespanFrom} timespanTo={validationSetTimespanTo} />}
        />
      ]}
      render={(item) => item}
      maxRows={3}
    />
  );
};

export default RunDataset;
