import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import PoolTypeIcon from "components/PoolTypeIcon";
import Selector from "components/Selector";
import SelectorLoader from "components/SelectorLoader";

const CreatePoolPolicyPoolSelector = ({ name, onChange, pools, isLoading = false }) => {
  const {
    formState: { errors },
    control
  } = useFormContext();

  const intl = useIntl();

  const labelId = "pool";

  return isLoading ? (
    <SelectorLoader fullWidth labelId={labelId} isRequired />
  ) : (
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
          data={{
            items: pools.map(({ id, name: poolName, pool_purpose: poolPurpose }) => ({
              name: poolName,
              value: id,
              type: poolPurpose
            }))
          }}
          menuItemIcon={{
            component: PoolTypeIcon,
            getComponentProps: ({ type }) => ({
              type
            })
          }}
          fullWidth
          labelId={labelId}
          dataTestId="pool_selector"
          required
          onChange={(newPoolId) => {
            onChangeControllerValue(newPoolId);
            if (typeof onChange === "function") {
              onChange();
            }
          }}
          error={!!errors[name]}
          helperText={errors[name] && errors[name].message}
          {...rest}
        />
      )}
    />
  );
};

export default CreatePoolPolicyPoolSelector;
