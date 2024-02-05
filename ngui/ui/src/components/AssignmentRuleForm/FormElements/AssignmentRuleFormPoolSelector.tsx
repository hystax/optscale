import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector, { Item, ItemContentWithPoolIcon } from "components/Selector";

const AssignmentRuleFormPoolSelector = ({ name, ownerSelectorName, readOnly = false, pools, onPoolChange, isLoading }) => {
  const {
    control,
    setValue,
    getValues,
    formState: { errors }
  } = useFormContext();
  const intl = useIntl();

  return (
    <Controller
      name={name}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        }
      }}
      render={({ field: { onChange, ...rest } }) => (
        <Selector
          id="target-pool-selector"
          readOnly={readOnly}
          fullWidth
          required
          isLoading={isLoading}
          error={!!errors[name]}
          helperText={errors?.[name]?.message}
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

            onChange(id);
          }}
          {...rest}
        >
          {pools.map(({ id: poolId, name: poolName, pool_purpose: poolPurpose }) => (
            <Item key={poolId} value={poolId}>
              <ItemContentWithPoolIcon poolType={poolPurpose}>{poolName}</ItemContentWithPoolIcon>
            </Item>
          ))}
        </Selector>
      )}
    />
  );
};

export default AssignmentRuleFormPoolSelector;
