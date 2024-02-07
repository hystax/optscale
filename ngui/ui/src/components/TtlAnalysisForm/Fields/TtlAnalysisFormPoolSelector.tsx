import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector, { Item, ItemContentWithPoolIcon } from "components/Selector";

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
      render={({ field }) => (
        <Selector
          id="pool-selector"
          shrinkLabel
          required
          readOnly={isReadOnly}
          fullWidth
          error={!!errors[name]}
          helperText={errors?.[name]?.message}
          labelMessageId="pool"
          isLoading={isLoading}
          {...field}
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

export default TtlAnalysisFormPoolSelector;
