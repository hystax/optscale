import { Typography } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import DatasetName from "components/DatasetName/DatasetName";
import ExpandableList from "components/ExpandableList";
import LabelChip from "components/LabelChip";
import SlicedText from "components/SlicedText";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { EN_FULL_FORMAT, formatUTC } from "utils/datetime";

const NoData = () => <span>-</span>;

const InfoLabel = ({ nameMessageId, text }) => (
  <Typography sx={{ whiteSpace: "normal", overflowWrap: "anywhere" }}>
    <Typography noWrap component="span">
      <FormattedMessage id={nameMessageId} />
      &#58;
    </Typography>
    &nbsp;
    {text}
  </Typography>
);

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
  return <NoData />;
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
        <InfoLabel
          key="id"
          nameMessageId="id"
          text={
            <strong>
              <SlicedText limit={60} text={path} />
            </strong>
          }
        />,
        <InfoLabel
          key="name"
          nameMessageId="name"
          text={
            name ? (
              <strong>
                <DatasetName name={<SlicedText limit={60} text={name} />} deleted={deleted} />
              </strong>
            ) : (
              <NoData />
            )
          }
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
        <InfoLabel
          key="training"
          nameMessageId="training"
          text={<strong>{trainingSetPathId ? <SlicedText limit={60} text={trainingSetPathId} /> : <NoData />}</strong>}
        />,
        <InfoLabel
          key="trainingTimespan"
          nameMessageId="trainingTimespan"
          text={
            <strong>
              <DatasetTimespan timespanFrom={trainingSetTimespanFrom} timespanTo={trainingSetTimespanTo} />
            </strong>
          }
        />,
        <InfoLabel
          key="validation"
          nameMessageId="validation"
          text={<strong>{validationSetPathId ? <SlicedText limit={60} text={validationSetPathId} /> : <NoData />}</strong>}
        />,
        <InfoLabel
          key="validationTimespan"
          nameMessageId="validationTimespan"
          text={
            <strong>
              <DatasetTimespan timespanFrom={validationSetTimespanFrom} timespanTo={validationSetTimespanTo} />
            </strong>
          }
        />
      ]}
      render={(item) => item}
      maxRows={3}
    />
  );
};

export default RunDataset;
