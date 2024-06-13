import { Selector } from "components/forms/common/fields";
import { ItemContentWithPoolIcon } from "components/Selector";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.POOL_ID;

const PoolSelector = ({ pools }) => (
  <Selector
    name={FIELD_NAME}
    id="pool-selector"
    required
    labelMessageId="pools"
    items={pools.map(({ id, name, pool_purpose: poolPurpose }) => ({
      value: id,
      content: <ItemContentWithPoolIcon poolType={poolPurpose}>{name}</ItemContentWithPoolIcon>
    }))}
  />
);

export default PoolSelector;
