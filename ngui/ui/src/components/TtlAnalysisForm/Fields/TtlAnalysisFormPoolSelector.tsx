import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import PoolTypeIcon from "components/PoolTypeIcon";
import Selector from "components/Selector";
import SelectorLoader from "components/SelectorLoader";

const buildPoolSelectorData = (pools) => ({
  items: pools.map(({ id, name, pool_purpose: poolPurpose }) => ({
    name,
    value: id,
    type: poolPurpose
  }))
});

const TtlAnalysisFormPoolSelector = ({ name, pools, fullWidth = false, isLoading = false, isReadOnly = false }) => {
  const intl = useIntl();
  const {
    control,
    formState: { errors }
  } = useFormContext();

  return (
    <Controller
      name={name}
      control={control}
      fullWidth={fullWidth}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        }
      }}
      render={({ field: { onChange, ...rest } }) =>
        isLoading ? (
          <SelectorLoader readOnly={isReadOnly} fullWidth={fullWidth} labelId="pool" isRequired />
        ) : (
          <Selector
            shrinkLabel
            required
            dataTestId="selector_pool"
            readOnly={isReadOnly}
            fullWidth={fullWidth}
            error={!!errors[name]}
            menuItemIcon={{
              component: PoolTypeIcon,
              getComponentProps: ({ type }) => ({
                type
              })
            }}
            helperText={errors?.[name]?.message}
            data={buildPoolSelectorData(pools)}
            labelId="pool"
            onChange={onChange}
            {...rest}
          />
        )
      }
    />
  );
};

export default TtlAnalysisFormPoolSelector;
