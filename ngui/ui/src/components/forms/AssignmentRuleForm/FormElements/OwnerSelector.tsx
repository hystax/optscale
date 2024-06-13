import { useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import { GET_POOL_OWNERS } from "api/restapi/actionTypes";
import { Selector } from "components/forms/common/fields";
import { ItemContent } from "components/Selector";
import { useApiState } from "hooks/useApiState";
import { FIELD_NAMES } from "../utils";

const LABEL_ID = "owner";

const OwnerSelector = ({
  name = FIELD_NAMES.OWNER_ID,
  poolSelectorName = FIELD_NAMES.POOL_ID,
  poolOwners,
  pools,
  isFormDataLoading = false
}) => {
  const { watch } = useFormContext();
  const intl = useIntl();

  const { isLoading: isGetPoolOwnerLoading } = useApiState(GET_POOL_OWNERS);

  const watchSelectedPool = watch(poolSelectorName);

  const { default_owner_id: poolDefaultOwnerId } = pools.find((pool) => pool.id === watchSelectedPool) ?? {};

  return (
    <Selector
      name={name}
      required
      id="owner-selector"
      fullWidth
      isLoading={isGetPoolOwnerLoading || isFormDataLoading}
      labelMessageId={LABEL_ID}
      items={poolOwners.map(({ id, name: poolOwnerName }) => ({
        value: id,
        content: (
          <ItemContent>
            {id === poolDefaultOwnerId ? intl.formatMessage({ id: "value(default)" }, { value: poolOwnerName }) : poolOwnerName}
          </ItemContent>
        )
      }))}
    />
  );
};

export default OwnerSelector;
