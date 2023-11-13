import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector from "components/Selector";
import { useConstraints } from "hooks/useConstraints";
import { getDifference } from "utils/arrays";
import { CONSTRAINTS_TYPES } from "utils/constraints";

const CreatePoolPolicyPolicyTypeSelector = ({ name, selectedPool }) => {
  const {
    formState: { errors },
    control
  } = useFormContext();

  const intl = useIntl();
  const constraints = useConstraints();

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
          disabled={!selectedPool.id}
          data={{
            items: selectedPool.id
              ? getDifference(
                  constraints,
                  selectedPool.policies.map(({ type }) => type)
                ).map((constraintType) => ({
                  name: intl.formatMessage({ id: CONSTRAINTS_TYPES[constraintType] }),
                  value: constraintType
                }))
              : []
          }}
          fullWidth
          labelId="policyType"
          dataTestId="policy_type"
          required
          onChange={(value) => {
            onChange(value);
          }}
          error={!!errors[name]}
          helperText={errors[name] && errors[name].message}
          {...rest}
        />
      )}
    />
  );
};

export default CreatePoolPolicyPolicyTypeSelector;
