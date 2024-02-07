import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector, { Item, ItemContentWithPoolIcon } from "components/Selector";

const CreatePoolPolicyPoolSelector = ({ name, onChange, pools, isLoading = false }) => {
  const {
    formState: { errors },
    control
  } = useFormContext();

  const intl = useIntl();

  const labelId = "pool";

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
      render={({ field: { onChange: onChangeControllerValue, ...rest } }) => (
        <Selector
          id="pool-selector"
          fullWidth
          labelMessageId={labelId}
          required
          onChange={(newPoolId) => {
            onChangeControllerValue(newPoolId);
            if (typeof onChange === "function") {
              onChange();
            }
          }}
          error={!!errors[name]}
          helperText={errors[name] && errors[name].message}
          isLoading={isLoading}
          {...rest}
        >
          {pools.map(({ id, name: poolName, pool_purpose: poolPurpose }) => (
            <Item key={id} value={id}>
              <ItemContentWithPoolIcon poolType={poolPurpose}>{poolName}</ItemContentWithPoolIcon>
            </Item>
          ))}
        </Selector>
      )}
    />
  );
};

export default CreatePoolPolicyPoolSelector;
