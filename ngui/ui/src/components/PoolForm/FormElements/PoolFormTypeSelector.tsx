import { useFormContext, Controller } from "react-hook-form";
import { useIntl } from "react-intl";
import PoolTypeIcon from "components/PoolTypeIcon";
import QuestionMark from "components/QuestionMark";
import Selector, { Item, ItemContentWithPoolIcon } from "components/Selector";
import {
  POOL_TYPE_BUDGET,
  POOL_TYPE_BUSINESS_UNIT,
  POOL_TYPE_TEAM,
  POOL_TYPE_PROJECT,
  POOL_TYPE_CICD,
  POOL_TYPE_MLAI,
  POOL_TYPE_ASSET_POOL,
  POOL_TYPES
} from "utils/constants";

const PoolFormTypeSelector = ({ isLoading = false, readOnly = false }) => {
  const {
    control,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return (
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
        <Selector
          id="pool-type-selector"
          error={!!errors.type}
          helperText={errors.type && errors.type.message}
          labelMessageId="type"
          isLoading={isLoading}
          fullWidth
          readOnly={readOnly}
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
          {...field}
        >
          {Object.entries(POOL_TYPES).map(([type, messageId]) => (
            <Item key={type} value={type}>
              <ItemContentWithPoolIcon key={type} poolType={type}>
                {intl.formatMessage({ id: messageId })}
              </ItemContentWithPoolIcon>
            </Item>
          ))}
        </Selector>
      )}
    />
  );
};

export default PoolFormTypeSelector;
