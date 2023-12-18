import { useFormContext, Controller } from "react-hook-form";
import { useIntl } from "react-intl";
import PoolTypeSelector from "components/PoolTypeSelector";
import SelectorLoader from "components/SelectorLoader";
import { POOL_TYPE_BUDGET } from "utils/constants";

const PoolFormTypeSelector = ({ isLoading, InputProps }) => {
  const {
    control,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return isLoading ? (
    <SelectorLoader fullWidth labelId="type" isRequired />
  ) : (
    <>
      <Controller
        name="type"
        control={control}
        defaultValue={POOL_TYPE_BUDGET}
        rules={{
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          }
        }}
        render={({ field }) => (
          <PoolTypeSelector
            dataTestId="selector_type"
            {...InputProps}
            {...field}
            error={!!errors.type}
            helperText={errors.type && errors.type.message}
          />
        )}
      />
    </>
  );
};

export default PoolFormTypeSelector;
