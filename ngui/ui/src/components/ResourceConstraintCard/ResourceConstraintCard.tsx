import { useState } from "react";
import CreateOutlinedIcon from "@mui/icons-material/CreateOutlined";
import PriorityHighOutlinedIcon from "@mui/icons-material/PriorityHighOutlined";
import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Skeleton from "@mui/material/Skeleton";
import Switch from "@mui/material/Switch";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import { ConstraintLimitMessage } from "components/ConstraintMessage";
import EditResourceConstraintForm from "components/forms/EditResourceConstraintForm";
import Icon from "components/Icon";
import IconButton from "components/IconButton";
import Tooltip from "components/Tooltip";
import WidgetTitle from "components/WidgetTitle";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import { useToggle } from "hooks/useToggle";
import { getPoolUrl } from "urls";
import { TAB_QUERY_PARAM_NAME, ORGANIZATION_OVERVIEW_TABS, RESOURCE_LIMIT_HIT_STATE } from "utils/constants";
import { CONSTRAINTS_TYPES, CONSTRAINT_MESSAGE_FORMAT, isExpensesLimit, isTtlLimit } from "utils/constraints";
import { format, EN_FULL_FORMAT, secondsToMilliseconds, millisecondsToSeconds, addHours } from "utils/datetime";
import { isEmptyObject } from "utils/objects";
import useStyles from "./ResourceConstraintCard.styles";

const CONSTRAINT_STATUS = Object.freeze({
  RESOURCE_SPECIFIC: "resource_specific",
  POOL_POLICY: "pool_policy",
});

const getStatus = (constraintStatus, { classes, constraintType, poolId }) => {
  if (constraintStatus) {
    return (
      <Box display="flex">
        {constraintStatus === CONSTRAINT_STATUS.RESOURCE_SPECIFIC && (
          <Typography
            data-test-id={`span_${constraintType}_resource_specific`}
            variant="caption"
            className={classes.resourceSpecific}
          >
            <FormattedMessage id="resourceSpecific" />
          </Typography>
        )}
        {constraintStatus === CONSTRAINT_STATUS.POOL_POLICY && (
          <Typography data-test-id={`span_${constraintType}_pool_policy`} variant="caption">
            <FormattedMessage
              id="linkedText"
              values={{
                text: <FormattedMessage id="poolPolicy" />,
                link: (chunks) => (
                  <Link
                    to={`${getPoolUrl(poolId)}?${TAB_QUERY_PARAM_NAME}=${ORGANIZATION_OVERVIEW_TABS.CONSTRAINTS}`}
                    component={RouterLink}
                  >
                    {chunks}
                  </Link>
                ),
              }}
            />
          </Typography>
        )}
      </Box>
    );
  }
  return null;
};

const ResourceConstraintCard = ({
  updateConstraint,
  createConstraint,
  deleteConstraint,
  constraint = {},
  constraintType,
  poolPolicy = {},
  limitHit,
  canEdit,
  poolId,
  isLoadingProps = {},
}) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  const {
    isGetDataLoading = false,
    isUpdateLoading = false,
    isCreateLoading = false,
    isDeleteLoading = false,
  } = isLoadingProps;

  const { classes } = useStyles();

  const getConstraintStatus = () => {
    if (!isEmptyObject(poolPolicy) && poolPolicy.active) {
      if (isEmptyObject(constraint)) {
        return CONSTRAINT_STATUS.POOL_POLICY;
      }
      return CONSTRAINT_STATUS.RESOURCE_SPECIFIC;
    }
    return undefined;
  };

  const constraintStatus = getConstraintStatus();

  const getLimit = () => {
    if (constraintStatus === CONSTRAINT_STATUS.POOL_POLICY) {
      return poolPolicy.limit;
    }
    if (!isEmptyObject(constraint)) {
      return constraint.limit;
    }
    return undefined;
  };

  const limit = getLimit();

  const [isSwitchEnabled, setIsSwitchEnabled] = useToggle(!isEmptyObject(constraint));
  const [editMode, setEditMode] = useState(false);

  const onEditMode = () => {
    setEditMode(true);
  };

  const offEditMode = () => {
    setEditMode(false);
  };

  const changeSwitch = () => {
    const changeConstraint = () => {
      if (isSwitchEnabled) {
        return deleteConstraint(constraint.id);
      }

      if (isEmptyObject(poolPolicy)) {
        return createConstraint(0);
      }

      const getModifiedPoolLimit = () => {
        if (isExpensesLimit(constraintType)) {
          return poolPolicy.limit;
        }
        if (isTtlLimit(constraintType)) {
          const currentTimeMS = +new Date();

          if (poolPolicy.limit > millisecondsToSeconds(currentTimeMS)) {
            return poolPolicy.limit;
          }

          return millisecondsToSeconds(+addHours(currentTimeMS, 1));
        }
        return undefined;
      };

      return createConstraint(getModifiedPoolLimit());
    };

    changeConstraint();
    setEditMode(false);
    setIsSwitchEnabled();
  };

  const renderPolicy = () =>
    editMode ? (
      <EditResourceConstraintForm
        constraintType={constraintType}
        constraintLimit={limit}
        constraintId={constraint.id}
        onSubmit={updateConstraint}
        onSuccess={offEditMode}
        onCancel={offEditMode}
        isLoading={isUpdateLoading}
      />
    ) : (
      <Box display="flex" alignItems="center">
        <Typography component="span">
          {Number.isInteger(limit) ? (
            <ConstraintLimitMessage
              formats={{ ttl: CONSTRAINT_MESSAGE_FORMAT.EXPIRES_AT_DATETIME }}
              limit={limit}
              type={constraintType}
            />
          ) : (
            <span data-test-id={`p_${constraintType}_value`}>
              <FormattedMessage id="notSet" />
            </span>
          )}
        </Typography>
        {canEdit && isSwitchEnabled && (
          <IconButton
            dataTestId={`btn_edit_${constraintType}`}
            icon={<CreateOutlinedIcon />}
            onClick={() => onEditMode()}
            disabled={isRestricted}
            tooltip={{
              show: true,
              value: isRestricted ? restrictionReasonMessage : <FormattedMessage id="edit" />,
            }}
          />
        )}
        {limitHit && limitHit.constraint_limit === limit && limitHit.time && limitHit.state === RESOURCE_LIMIT_HIT_STATE.RED ? (
          <Icon
            dataTestId={`svg_${constraintType}_hint`}
            icon={PriorityHighOutlinedIcon}
            color="error"
            tooltip={{
              show: true,
              value: format(secondsToMilliseconds(limitHit.time), EN_FULL_FORMAT),
              messageId: "violatedAt",
              placement: "right",
            }}
          />
        ) : null}
      </Box>
    );

  const card = (
    <div data-test-id={`block_${constraintType}`}>
      <Box display="flex" alignItems="center">
        <WidgetTitle dataTestId={`p_${constraintType}`}>
          <FormattedMessage id={CONSTRAINTS_TYPES[constraintType]} />
        </WidgetTitle>

        {canEdit && (
          <Tooltip title={restrictionReasonMessage}>
            <div>
              <Switch
                data-test-id={`checkbox_${constraintType}`}
                checked={isSwitchEnabled}
                onChange={() => changeSwitch()}
                disabled={isRestricted}
              />
            </div>
          </Tooltip>
        )}
        {getStatus(constraintStatus, { classes, constraintType, poolId })}
      </Box>
      <Typography variant="caption">
        <FormattedMessage id={`${CONSTRAINTS_TYPES[constraintType]}ExplanatoryText`} />
      </Typography>
      {isCreateLoading || isDeleteLoading ? <Skeleton width="100%">{renderPolicy()}</Skeleton> : renderPolicy()}
    </div>
  );

  return isGetDataLoading ? <Skeleton width="100%">{card}</Skeleton> : card;
};

export default ResourceConstraintCard;
