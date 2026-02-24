import { useFormContext } from "react-hook-form";
import { Selector } from "components/forms/common/fields";
import { ItemContentWithPoolIcon } from "components/Selector";
import { PoolSelectorProps } from "../types";
import { FIELD_NAMES } from "../utils";

const PoolSelector = ({
  name = FIELD_NAMES.POOL_ID,
  ownerSelectorName = FIELD_NAMES.OWNER_ID,
  pools,
  onPoolChange,
  isLoading = false,
}: PoolSelectorProps) => {
  const { setValue, getValues } = useFormContext();

  return (
    <Selector
      name={name}
      items={pools.map(({ id: poolId, name: poolName, pool_purpose: poolPurpose }) => ({
        value: poolId,
        content: <ItemContentWithPoolIcon poolType={poolPurpose} label={poolName} />,
      }))}
      id="target-pool-selector"
      fullWidth
      required
      isLoading={isLoading}
      labelMessageId="targetPool"
      onChange={(id) => {
        onPoolChange(id, (owners) => {
          const defaultOwnerId = pools.find((pool) => pool.id === id)?.default_owner_id;

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
