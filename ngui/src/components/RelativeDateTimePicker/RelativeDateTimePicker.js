import React, { useState } from "react";
import PropTypes from "prop-types";
import { useIntl } from "react-intl";
import LinearSelector from "components/LinearSelector";
import { LINEAR_SELECTOR_ITEMS_TYPES } from "utils/constants";

const RelativeDateTimePicker = ({ definedRanges, defaultActiveRange, onChange }) => {
  const intl = useIntl();

  const [selectedRange, setSelectedRange] = useState(
    () => definedRanges.find((range) => range.id === defaultActiveRange)?.id ?? definedRanges[0].id
  );

  const timeItems = definedRanges.map(({ id, messageId, messageValues, dataTestId }) => ({
    displayedName: intl.formatMessage({ id: messageId }, messageValues),
    name: id,
    value: id,
    dataTestId,
    type: LINEAR_SELECTOR_ITEMS_TYPES.TEXT
  }));

  const selectedTimeItem = timeItems.find(({ value }) => value === selectedRange);

  const handleChange = ({ value }) => {
    const selectedRangeDefinition = definedRanges.find(({ id }) => id === value);
    setSelectedRange(value);
    onChange(selectedRangeDefinition);
  };

  return <LinearSelector value={selectedTimeItem} onChange={handleChange} items={timeItems} />;
};

const DateType = PropTypes.oneOfType([PropTypes.object, PropTypes.number]);

const DefinedRangesType = PropTypes.arrayOf(
  PropTypes.shape({
    messageId: PropTypes.string,
    id: PropTypes.string,
    startDate: DateType,
    endDate: DateType,
    dataTestId: PropTypes.string
  })
);

RelativeDateTimePicker.propTypes = {
  definedRanges: DefinedRangesType,
  defaultActiveRange: PropTypes.string,
  onChange: PropTypes.func.isRequired
};

export { DefinedRangesType };
export default RelativeDateTimePicker;
