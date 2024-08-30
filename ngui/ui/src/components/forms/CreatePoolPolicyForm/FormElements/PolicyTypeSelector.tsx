import { useIntl } from "react-intl";
import { Selector } from "components/forms/common/fields";
import { ItemContent } from "components/Selector";
import { useConstraints } from "hooks/useConstraints";
import { getDifference } from "utils/arrays";
import { CONSTRAINTS_TYPES } from "utils/constraints";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.POLICY_TYPE;

const PolicyTypeSelector = ({ selectedPool }) => {
  const intl = useIntl();
  const constraints = useConstraints();

  return (
    <Selector
      id="policy-type-selector"
      name={FIELD_NAME}
      items={
        selectedPool.id
          ? getDifference(
              constraints,
              selectedPool.policies.map(({ type }) => type)
            ).map((constraintType) => ({
              value: constraintType,
              content: (
                <ItemContent>
                  {intl.formatMessage({
                    id: CONSTRAINTS_TYPES[constraintType]
                  })}
                </ItemContent>
              )
            }))
          : []
      }
      disabled={!selectedPool.id}
      fullWidth
      labelMessageId="policyType"
      required
    />
  );
};

export default PolicyTypeSelector;
