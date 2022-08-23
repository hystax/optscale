import React, { useState } from "react";
import { Grid } from "@mui/material";
import PropTypes from "prop-types";
import { isEmpty } from "utils/arrays";
import { datetimeToUnix, millisecondsToSeconds } from "utils/datetime";
import ButtonGroup from "../ButtonGroup";

const RelativeDateTimePicker = ({ definedRanges, onChange }) => {
  const [activeButtonId, setActiveButtonId] = useState();

  if (!isEmpty(definedRanges) && !activeButtonId) {
    setActiveButtonId(definedRanges[0].key);
  }

  const setActive = (id) => {
    setActiveButtonId(id);
    const endDate = new Date();
    const currentRange = definedRanges.find((range) => range.key === id);
    const { startDateFn } = currentRange;
    const startDate = startDateFn(endDate);
    onChange({ startDate: millisecondsToSeconds(startDate), endDate: datetimeToUnix(endDate) });
  };
  const buttons = definedRanges.map((range) => ({
    id: range.key,
    messageId: range.messageId,
    messageValues: range.messageValues,
    action: () => setActive(range.key),
    dataTestId: `tab_${range.key}`
  }));

  return (
    <Grid container direction="row">
      <Grid item>
        <ButtonGroup
          buttons={buttons}
          activeButtonIndex={buttons.indexOf(buttons.find((button) => button.id === activeButtonId))}
        />
      </Grid>
    </Grid>
  );
};

const DateType = PropTypes.oneOfType([PropTypes.object, PropTypes.number]);

const DefinedRangesType = PropTypes.arrayOf(
  PropTypes.shape({
    messageId: PropTypes.string,
    key: PropTypes.string,
    startDate: DateType,
    endDate: DateType,
    dataTestId: PropTypes.string
  })
);

RelativeDateTimePicker.propTypes = {
  definedRanges: DefinedRangesType,
  onChange: PropTypes.func.isRequired
};

export { DefinedRangesType };
export default RelativeDateTimePicker;
