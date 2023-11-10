import Box from "@mui/material/Box";
import Skeleton from "@mui/material/Skeleton";
import Switch from "@mui/material/Switch";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import EditablePoolPolicyLimit, { MODE } from "components/EditablePoolPolicyLimit";
import WidgetTitle from "components/WidgetTitle";
import { useIsAllowed } from "hooks/useAllowedActions";
import { SCOPE_TYPES } from "utils/constants";
import {
  CONSTRAINTS_TYPES,
  DAILY_EXPENSE_LIMIT,
  isExpensesLimit,
  isTtlLimit,
  TOTAL_EXPENSE_LIMIT,
  TTL
} from "utils/constraints";
import { isEmpty } from "utils/objects";
import useStyles from "./PoolConstraintForm.styles";

const getDataTestIds = (type) =>
  ({
    [TOTAL_EXPENSE_LIMIT]: {
      card: "block_total_expense_limit",
      subheaderText: "p_total_expense_limit",
      switch: "switch_total_expense_limit",
      editButton: "btn_total_expense_edit",
      constraintLimitMessage: "lbl_total_expense_value"
    },
    [DAILY_EXPENSE_LIMIT]: {
      card: "block_daily_total_expense_limit",
      subheaderText: "p_daily_total_expense_limit",
      switch: "switch_daily_total_expense_limit",
      editButton: "btn_daily_total_expense_edit",
      constraintLimitMessage: "lbl_daily_total_expense_value"
    },
    [TTL]: {
      card: "block_ttl",
      subheaderText: "p_ttl",
      switch: "switch_ttl",
      editButton: "btn_ttl_edit",
      constraintLimitMessage: "lbl_ttl_value"
    }
  })[type];

const PoolConstraintForm = ({ update, create, updateActivity, policy = {}, policyType, poolId, isLoadingProps = {} }) => {
  const { classes } = useStyles();

  const { isGetDataLoading, isUpdateLoading, isCreateLoading, isUpdateActivityLoading } = isLoadingProps;

  const {
    card: cardDataTestId,
    subheaderText: subheaderTextDataTestId,
    switch: switchDataTestId,
    editButton: editButtonDataTestId,
    constraintLimitMessage: constraintLimitMessageDataTestId
  } = getDataTestIds(policyType);

  const isManagePoolsAllowed = useIsAllowed({ requiredActions: ["MANAGE_POOLS"] });

  const isManagePoolAllowed = useIsAllowed({
    entityId: poolId,
    entityType: SCOPE_TYPES.POOL,
    requiredActions: ["MANAGE_POOLS"]
  });

  const renderPolicy = () => (
    <EditablePoolPolicyLimit
      isAllowedToEdit={isManagePoolAllowed}
      policyId={policy.id}
      policyLimit={policy.limit}
      policyType={policyType}
      onSubmit={(mode, data, { onSuccess }) => {
        if (mode === MODE.UPDATE) {
          update(data, { onSuccess });
        }
        if (mode === MODE.CREATE) {
          create(data, { onSuccess });
        }
      }}
      isLoading={isUpdateLoading || isCreateLoading}
      dataTestIds={{
        constraintLimitMessageDataTestId,
        editButtonDataTestId
      }}
    />
  );

  const renderCardTitleText = () => (
    <WidgetTitle>
      <FormattedMessage id={CONSTRAINTS_TYPES[policyType]} />
    </WidgetTitle>
  );

  const renderCardTitleSwitch = () =>
    isManagePoolsAllowed ? (
      <div className={classes.switchWrapper}>
        <Switch
          className={classes.absoluteSwitch}
          key="switch"
          onChange={() => updateActivity(policy.id, !policy.active)}
          checked={!isEmpty(policy) && policy.active}
          data-test-id={switchDataTestId}
        />
      </div>
    ) : null;

  const renderCardTitle = () => {
    if (isExpensesLimit(policyType)) {
      return (
        <Box display="flex" alignItems="center">
          {renderCardTitleText()}
          {!isEmpty(policy) && renderCardTitleSwitch()}
        </Box>
      );
    }
    if (isTtlLimit(policyType)) {
      return (
        <Box display="flex" alignItems="center">
          <Box mr={1} display="flex" alignItems="center">
            {renderCardTitleText()}
            {!isEmpty(policy) && renderCardTitleSwitch()}
          </Box>
          {/* This was hidden as part of this task-https://datatrendstech.atlassian.net/browse/NGUI-2412. It will be redone and returned in the future.
              <Typography variant="body2">
                <Link color="primary" to={getPoolTtlAnalysis(poolId)} component={RouterLink}>
                  <FormattedMessage id="runAnalysis" />
                </Link>
              </Typography> */}
        </Box>
      );
    }
    return null;
  };

  const renderCard = (
    <div data-test-id={cardDataTestId}>
      {renderCardTitle()}
      <Typography variant="caption" data-test-id={subheaderTextDataTestId}>
        <FormattedMessage id={`${CONSTRAINTS_TYPES[policyType]}ExplanatoryText`} />
      </Typography>
      {isUpdateActivityLoading ? <Skeleton width="100%">{renderPolicy()}</Skeleton> : renderPolicy()}
    </div>
  );

  return isGetDataLoading ? <Skeleton width="100%">{renderCard}</Skeleton> : renderCard;
};

export default PoolConstraintForm;
