import React from "react";
import PropTypes from "prop-types";
import ConditionWrapper from "components/ConditionWrapper";
import Selector from "components/Selector";
import SelectorLoader from "components/SelectorLoader";

const USER = "user";

const prepareSelectorData = (selected, data) => ({
  selected,
  items: data.map((obj) => ({
    name: obj.name,
    value: obj.id
  }))
});

const EmployeeSelector = ({ employees, selected, onChange, error, helperText, dataTestId, isLoading = false }) => (
  <ConditionWrapper condition={isLoading} conditionTemplate={<SelectorLoader fullWidth labelId={USER} isRequired />}>
    <Selector
      fullWidth
      required
      error={error}
      helperText={helperText}
      data={prepareSelectorData(selected, employees)}
      labelId={USER}
      name={USER}
      onChange={onChange}
      dataTestId={dataTestId}
    />
  </ConditionWrapper>
);

EmployeeSelector.propTypes = {
  employees: PropTypes.array.isRequired,
  selected: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  error: PropTypes.bool,
  helperText: PropTypes.string,
  dataTestId: PropTypes.string
};

export default EmployeeSelector;
