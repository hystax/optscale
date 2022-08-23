import React from "react";
import PropTypes from "prop-types";
import ConditionWrapper from "components/ConditionWrapper";
import Selector from "components/Selector";
import SelectorLoader from "components/SelectorLoader";

const OWNER = "owner";

const prepareSelectorData = (selected, data) => ({
  selected,
  items: data.map((obj) => ({
    name: obj.name,
    value: obj.id
  }))
});

const PoolOwnerSelector = ({ owners, selected, onChange, error, helperText, dataTestId, isLoading = false }) => (
  <ConditionWrapper condition={isLoading} conditionTemplate={<SelectorLoader fullWidth labelId={OWNER} isRequired />}>
    <Selector
      fullWidth
      required
      error={error}
      helperText={helperText}
      data={prepareSelectorData(selected, owners)}
      labelId={OWNER}
      name={OWNER}
      onChange={onChange}
      dataTestId={dataTestId}
    />
  </ConditionWrapper>
);

PoolOwnerSelector.propTypes = {
  owners: PropTypes.array.isRequired,
  selected: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  error: PropTypes.bool,
  helperText: PropTypes.string,
  dataTestId: PropTypes.string
};

export default PoolOwnerSelector;
