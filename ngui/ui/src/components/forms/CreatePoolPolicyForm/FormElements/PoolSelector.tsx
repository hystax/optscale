import { Selector } from "components/forms/common/fields";
import { ItemContentWithPoolIcon } from "components/Selector";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.POOL_ID;

const PoolSelector = ({ onChange, pools, isLoading = false }) => (
  <Selector
    id="pool-selector"
    name={FIELD_NAME}
    items={pools.map(({ id, name: poolName, pool_purpose: poolPurpose }) => ({
      value: id,
      content: <ItemContentWithPoolIcon poolType={poolPurpose}>{poolName}</ItemContentWithPoolIcon>
    }))}
    labelMessageId="pool"
    fullWidth
    required
    isLoading={isLoading}
    onChange={onChange}
  />
);

export default PoolSelector;
