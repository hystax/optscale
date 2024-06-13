import { Selector } from "components/forms/common/fields";
import { ItemContentWithPoolIcon } from "components/Selector";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.POOL_ID;

const PoolSelector = ({ pools, fullWidth = false, isLoading = false, isReadOnly = false }) => (
  <Selector
    name={FIELD_NAME}
    id="pool-selector"
    required
    readOnly={isReadOnly}
    fullWidth={fullWidth}
    labelMessageId="pool"
    isLoading={isLoading}
    items={pools.map(({ id, name: poolName, pool_purpose: poolPurpose }) => ({
      value: id,
      content: <ItemContentWithPoolIcon poolType={poolPurpose}>{poolName}</ItemContentWithPoolIcon>
    }))}
  />
);

export default PoolSelector;
