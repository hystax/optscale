import { useEffect, useState } from "react";
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

  const [selectedStartDate, setSelectedStartDate] = useState(() => Number(initialStartDateValue));
  const [selectedEndDate, setSelectedEndDate] = useState(() => Number(initialEndDateValue));

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

export default RangePickerFormContainer;
