import React from "react";
import PropTypes from "prop-types";
import ConditionWrapper from "components/ConditionWrapper";
import PoolTypeIcon from "components/PoolTypeIcon";
import Selector from "components/Selector";
import SelectorLoader from "components/SelectorLoader";

const POOL = "pool";
const POOL_NAME = "pool";

const prepareSelectorData = (selected, data) => ({
  selected,
  items: data.map((obj) => ({
    name: obj.name,
    value: obj.id,
    type: obj.pool_purpose
  }))
});

const AvailablePoolSelector = ({ pools, selected, onChange, error, helperText, dataTestId, isLoading = false }) => (
  <ConditionWrapper condition={isLoading} conditionTemplate={<SelectorLoader fullWidth labelId={POOL_NAME} isRequired />}>
    <Selector
      fullWidth
      menuItemIcon={{
        component: PoolTypeIcon,
        getComponentProps: (itemInfo) => ({
          type: itemInfo.type
        })
      }}
      error={error}
      helperText={helperText}
      required
      data={prepareSelectorData(selected, pools)}
      labelId={POOL_NAME}
      name={POOL}
      onChange={onChange}
      dataTestId={dataTestId}
    />
  </ConditionWrapper>
);

AvailablePoolSelector.propTypes = {
  pools: PropTypes.array.isRequired,
  selected: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  error: PropTypes.bool,
  helperText: PropTypes.string,
  dataTestId: PropTypes.string
};

export default AvailablePoolSelector;
