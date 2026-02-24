import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { NOT_SET_REGION_FILTER_NAME } from "components/forms/AssignmentRuleForm/FormElements/ConditionsFieldArray";
import HtmlSymbol from "components/HtmlSymbol";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { intl } from "translations/react-intl-config";
import {
  CONDITION_TYPES,
  TAG_IS,
  CLOUD_IS,
  TAG_VALUE_STARTS_WITH,
  REGION_IS,
  ASSIGNMENT_RULE_OPERATORS,
} from "utils/constants";

const ConditionHeaderMessage = ({ operator = ASSIGNMENT_RULE_OPERATORS.AND }) => {
  const messageId = operator === ASSIGNMENT_RULE_OPERATORS.AND ? "allConditionsMustBeMet" : "atLeastOneConditionMustBeMet";

  return (
    <Typography gutterBottom>
      <FormattedMessage id={messageId} values={{ strong: (chunks) => <strong>{chunks}</strong> }} />
      <HtmlSymbol symbol="colon" />
    </Typography>
  );
};

const prepareData = ({ assignmentRules, entities }) => {
  const translateType = (type) =>
    intl.formatMessage({
      id: CONDITION_TYPES[type],
    });

  const getConditionsObject = (conditions, operator = ASSIGNMENT_RULE_OPERATORS.AND) =>
    [...conditions]
      // sort by translated values in asc order: "name_ends_with" -> "name ends with"
      .sort((a, b) => {
        const aTranslatedTypeInLowerCase = translateType(a.type).toLowerCase();
        const bTranslatedTypeInLowerCase = translateType(b.type).toLowerCase();
        if (aTranslatedTypeInLowerCase > bTranslatedTypeInLowerCase) {
          return 1;
        }
        if (aTranslatedTypeInLowerCase < bTranslatedTypeInLowerCase) {
          return -1;
        }
        return 0;
      })
      .reduce(
        (resultObject, { id, type, meta_info: metaInfo }) => {
          let value = metaInfo;

          if ([TAG_VALUE_STARTS_WITH, TAG_IS].includes(type)) {
            try {
              const metaObj = JSON.parse(metaInfo);
              value = JSON.stringify({ [metaObj.key]: metaObj.value });
            } catch (err) {
              console.log(err);
            }
          }

          if (type === CLOUD_IS) {
            value = entities?.[metaInfo]?.name;
          }

          if (type === REGION_IS) {
            value = metaInfo === null ? NOT_SET_REGION_FILTER_NAME : metaInfo;
          }

          return {
            ...resultObject,
            conditionsString: `${resultObject.conditionsString ? `${resultObject.conditionsString},` : ""}${translateType(
              type
            )}: ${value}`,
            conditionsRender: [
              ...resultObject.conditionsRender,
              <KeyValueLabel key={id} keyMessageId={CONDITION_TYPES[type]} value={value} />,
            ],
          };
        },
        {
          conditionsString: "",
          conditionsRender: conditions.length > 1 ? [<ConditionHeaderMessage key="header" operator={operator} />] : [],
        }
      );

  return assignmentRules.map(({ conditions = {}, operator = ASSIGNMENT_RULE_OPERATORS.AND, ...rest }) => ({
    ...rest,
    "pool/owner": `${rest.pool_name} ${rest.owner_name}`,
    conditionsObject: getConditionsObject(conditions, operator),
  }));
};

export default prepareData;
