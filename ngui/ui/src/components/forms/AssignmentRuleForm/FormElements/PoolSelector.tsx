import { useFormContext } from "react-hook-form";
import { Selector } from "components/forms/common/fields";
import { ItemContentWithPoolIcon } from "components/Selector";
import { FIELD_NAMES } from "../utils";

const PoolSelector = ({
  name = FIELD_NAMES.POOL_ID,
  ownerSelectorName = FIELD_NAMES.OWNER_ID,
  pools,
  onPoolChange,
  isLoading
}) => {
  const { setValue, getValues } = useFormContext();

  return (
    <Selector
      name={name}
      items={pools.map(({ id: poolId, name: poolName, pool_purpose: poolPurpose }) => ({
        value: poolId,
        content: <ItemContentWithPoolIcon poolType={poolPurpose}>{poolName}</ItemContentWithPoolIcon>
      }))}
      id="target-pool-selector"
      fullWidth
      required
      isLoading={isLoading}
      labelMessageId="targetPool"
      onChange={(id) => {
        onPoolChange(id, (owners) => {
          const { default_owner_id: defaultOwnerId } = pools.find((pool) => pool.id === id);

          const currentlySelectedOwner = getValues(ownerSelectorName);

          const newSelectedOwner = owners.find((owner) => owner.id === currentlySelectedOwner)
            ? currentlySelectedOwner
            : defaultOwnerId;

          setValue(ownerSelectorName, newSelectedOwner);
        });
      }}
    />
  );
};

export default PoolSelector;
