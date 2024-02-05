import { useFormContext, Controller } from "react-hook-form";
import { useIntl } from "react-intl";
import PoolTypeIcon from "components/PoolTypeIcon";
import PoolTypeSelector from "components/PoolTypeSelector";
import QuestionMark from "components/QuestionMark";
import SelectorLoader from "components/SelectorLoader";
import {
  POOL_TYPE_BUDGET,
  POOL_TYPE_BUSINESS_UNIT,
  POOL_TYPE_TEAM,
  POOL_TYPE_PROJECT,
  POOL_TYPE_CICD,
  POOL_TYPE_MLAI,
  POOL_TYPE_ASSET_POOL
} from "utils/constants";

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
            endAdornment={
              <QuestionMark
                messageId="poolTypesDescription"
                messageValues={{
                  br: <br />,
                  budget: <PoolTypeIcon type={POOL_TYPE_BUDGET} />,
                  businessUnit: <PoolTypeIcon type={POOL_TYPE_BUSINESS_UNIT} />,
                  team: <PoolTypeIcon type={POOL_TYPE_TEAM} />,
                  project: <PoolTypeIcon type={POOL_TYPE_PROJECT} />,
                  cicd: <PoolTypeIcon type={POOL_TYPE_CICD} />,
                  mlai: <PoolTypeIcon type={POOL_TYPE_MLAI} />,
                  assetPool: <PoolTypeIcon type={POOL_TYPE_ASSET_POOL} />
                }}
                dataTestId="qmark_pool_types_description"
              />
            }
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
