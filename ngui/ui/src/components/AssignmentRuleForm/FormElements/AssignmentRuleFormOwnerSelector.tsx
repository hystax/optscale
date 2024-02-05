import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import { GET_POOL_OWNERS } from "api/restapi/actionTypes";
import Selector, { Item, ItemContent } from "components/Selector";
import { useApiState } from "hooks/useApiState";

const LABEL_ID = "owner";

const AssignmentRuleFormOwnerSelector = ({
  name: fieldName,
  poolSelectorName,
  poolOwners,
  pools,
  isFormDataLoading = false,
  readOnly = false
}) => {
  const {
    control,
    watch,
    formState: { errors }
  } = useFormContext();
  const intl = useIntl();

  const { isLoading: isGetPoolOwnerLoading } = useApiState(GET_POOL_OWNERS);

  const watchSelectedPool = watch(poolSelectorName);

  const { default_owner_id: poolDefaultOwnerId } = pools.find((pool) => pool.id === watchSelectedPool) ?? {};

  return (
    <Controller
      name={fieldName}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        }
      }}
      // it is important to define selector inside the Controller since we need to persist currently selected owner between loading-rendered states
      render={({ field }) => (
        <Selector
          id="owner-selector"
          fullWidth
          readOnly={readOnly}
          isLoading={isGetPoolOwnerLoading || isFormDataLoading}
          required
          error={!!errors[fieldName]}
          helperText={errors?.[fieldName]?.message}
          labelMessageId={LABEL_ID}
          {...field}
        >
          {poolOwners.map(({ id, name }) => (
            <Item key={id} value={id}>
              <ItemContent>
                {id === poolDefaultOwnerId ? intl.formatMessage({ id: "value(default)" }, { value: name }) : name}
              </ItemContent>
            </Item>
          ))}
        </Selector>
      )}
    />
  );
};

export default AssignmentRuleFormOwnerSelector;
