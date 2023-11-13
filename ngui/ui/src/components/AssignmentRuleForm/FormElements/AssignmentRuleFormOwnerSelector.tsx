import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import { GET_POOL_OWNERS } from "api/restapi/actionTypes";
import Selector from "components/Selector";
import SelectorLoader from "components/SelectorLoader";
import { useApiState } from "hooks/useApiState";

const buildOwnerSelectorData = ({ poolOwners, selectedPoolId, pools = [], intl }) => {
  const { default_owner_id: poolDefaultOwnerId } = pools.find((pool) => pool.id === selectedPoolId) ?? {};

  return {
    items: poolOwners.map(({ id, name }) => ({
      name: id === poolDefaultOwnerId ? intl.formatMessage({ id: "value(default)" }, { value: name }) : name,
      value: id
    }))
  };
};

const LABEL_ID = "owner";

const AssignmentRuleFormOwnerSelector = ({
  name: fieldName,
  poolSelectorName,
  poolOwners,
  pools,
  isFormDataLoading = false,
  readOnly = false,
  classes = {}
}) => {
  const {
    control,
    watch,
    formState: { errors }
  } = useFormContext();
  const intl = useIntl();

  const { isLoading: isGetPoolOwnerLoading } = useApiState(GET_POOL_OWNERS);

  const watchSelectedPool = watch(poolSelectorName);

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
      render={({ field: { onChange, ...rest } }) =>
        isGetPoolOwnerLoading || isFormDataLoading ? (
          <SelectorLoader readOnly={readOnly} fullWidth labelId={LABEL_ID} isRequired />
        ) : (
          <Selector
            dataTestId="selector_owner"
            fullWidth
            readOnly={readOnly}
            required
            customClass={classes.customClass}
            error={!!errors[fieldName]}
            helperText={errors?.[fieldName]?.message}
            data={buildOwnerSelectorData({ poolOwners, selectedPoolId: watchSelectedPool, pools, intl })}
            labelId={LABEL_ID}
            onChange={(id) => {
              onChange(id);
            }}
            {...rest}
          />
        )
      }
    />
  );
};

export default AssignmentRuleFormOwnerSelector;
