import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import RangePickerForm from "components/RangePickerForm";
import { useInitialMount } from "hooks/useInitialMount";
import { setDate } from "./actionCreators";
import RangePickerFormContainerPdf from "./RangePickerFormContainerPdf";

const RangePickerFormContainer = ({
  onApply,
  initialStartDateValue,
  initialEndDateValue,
  rangeType,
  definedRanges,
  pdfId,
  minDate,
  maxDate
}) => {
  const dispatch = useDispatch();
  const { isInitialMount, setIsInitialMount } = useInitialMount();

  const [selectedStartDate, setSelectedStartDate] = useState(() => initialStartDateValue);
  const [selectedEndDate, setSelectedEndDate] = useState(() => initialEndDateValue);

  useEffect(() => {
    if (isInitialMount) {
      dispatch(setDate(selectedStartDate, selectedEndDate, rangeType));
      setIsInitialMount(false);
    }
  }, [dispatch, rangeType, selectedEndDate, selectedStartDate, isInitialMount, setIsInitialMount]);

  return (
    <>
      <RangePickerForm
        initialStartDateValue={selectedStartDate}
        initialEndDateValue={selectedEndDate}
        onApply={(startDateTimestamp, endDateTimestamp) => {
          onApply({
            startDate: startDateTimestamp,
            endDate: endDateTimestamp
          });
          setSelectedStartDate(startDateTimestamp);
          setSelectedEndDate(endDateTimestamp);
          dispatch(setDate(startDateTimestamp, endDateTimestamp, rangeType));
        }}
        definedRanges={definedRanges}
        minDate={minDate}
        maxDate={maxDate}
      />
      {pdfId ? <RangePickerFormContainerPdf pdfId={pdfId} renderData={() => ({ selectedStartDate, selectedEndDate })} /> : null}
    </>
  );
};

RangePickerFormContainer.propTypes = {
  onApply: PropTypes.func.isRequired,
  initialStartDateValue: PropTypes.number.isRequired,
  initialEndDateValue: PropTypes.number.isRequired,
  rangeType: PropTypes.string.isRequired,
  definedRanges: PropTypes.array,
  pdfId: PropTypes.string,
  minDate: PropTypes.number,
  maxDate: PropTypes.number
};

export default RangePickerFormContainer;
