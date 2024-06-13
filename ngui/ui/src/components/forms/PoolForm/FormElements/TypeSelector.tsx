import { useIntl } from "react-intl";
import { Selector } from "components/forms/common/fields";
import PoolTypeIcon from "components/PoolTypeIcon";
import QuestionMark from "components/QuestionMark";
import { ItemContentWithPoolIcon } from "components/Selector";
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
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.TYPE;

const TypeSelector = ({ isLoading = false, readOnly = false }) => {
  const intl = useIntl();

  return (
    <Selector
      name={FIELD_NAME}
      id="pool-type-selector"
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
      items={Object.entries(POOL_TYPES).map(([type, messageId]) => ({
        value: type,
        content: (
          <ItemContentWithPoolIcon key={type} poolType={type}>
            {intl.formatMessage({ id: messageId })}
          </ItemContentWithPoolIcon>
        )
      }))}
    />
  );
};

export default TypeSelector;
