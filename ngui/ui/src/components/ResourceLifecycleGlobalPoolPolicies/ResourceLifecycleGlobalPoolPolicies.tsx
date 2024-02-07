import { useMemo, useState } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import { CircularProgress, Stack } from "@mui/material";
import Switch from "@mui/material/Switch";
import { Box } from "@mui/system";
import { FormattedMessage, useIntl } from "react-intl";
import { useNavigate } from "react-router-dom";
import { useFormatConstraintLimitMessage } from "components/ConstraintMessage/ConstraintLimitMessage";
import EditablePoolPolicyLimit from "components/EditablePoolPolicyLimit";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import PoolLabel from "components/PoolLabel";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useIsAllowed, useIsAllowedForSome } from "hooks/useAllowedActions";
import PoolPolicyService from "services/PoolPolicyService";
import { RESOURCE_LIFECYCLE_CREATE_POOL_POLICY } from "urls";
import { SCOPE_TYPES } from "utils/constants";
import { CONSTRAINTS_TYPES, CONSTRAINT_MESSAGE_FORMAT } from "utils/constraints";
import { SPACING_2 } from "utils/layouts";

const UpdatePoolPolicyActivityContainer = ({ policyId, poolId, active }) => {
  const { useUpdateGlobalPoolPolicyActivity } = PoolPolicyService();

  const { update: updatePolicyActivity } = useUpdateGlobalPoolPolicyActivity();

  const [isUpdateActivityLoading, setIsUpdateActivityLoading] = useState(false);

  const isManagePoolAllowed = useIsAllowed({
    entityId: poolId,
    entityType: SCOPE_TYPES.POOL,
    requiredActions: ["MANAGE_POOLS"]
  });

  const onActivityChange = () => {
    setIsUpdateActivityLoading(true);
    updatePolicyActivity(
      {
        policyId,
        isActive: !active
      },
      {
        onSuccess: () => setIsUpdateActivityLoading(false),
        onError: () => setIsUpdateActivityLoading(false)
      }
    );
  };

  const isChecked = active;

  const renderSwitch = () => {
    const icon = (
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          width: 20,
          height: 20,
          borderRadius: "50%",
          backgroundColor: (theme) => (isChecked ? theme.palette.secondary.main : theme.palette.background.default),
          boxShadow: (theme) => theme.shadows[1]
        }}
      >
        {isUpdateActivityLoading && <CircularProgress size={14} thickness={6} />}
      </Box>
    );

    return (
      <Switch
        checkedIcon={icon}
        icon={icon}
        disabled={isUpdateActivityLoading}
        onChange={onActivityChange}
        checked={isChecked}
      />
    );
  };

  return isManagePoolAllowed ? renderSwitch() : null;
};

const UpdatePoolPolicyContainer = ({ policyId, policyLimit, policyType, poolId, formattedPolicyLimit }) => {
  const { useUpdateGlobalPoolPolicyLimit } = PoolPolicyService();
  const { update: updatePolicyLimit } = useUpdateGlobalPoolPolicyLimit();

  const isManagePoolAllowed = useIsAllowed({
    entityId: poolId,
    entityType: SCOPE_TYPES.POOL,
    requiredActions: ["MANAGE_POOLS"]
  });

  // Need to handle the loading state locally since it is possible dispatch multiple requests with the same API label
  // and entityId will be not enough to get a correct loading state
  const [isUpdateLimitLoading, setIsUpdateLimitLoading] = useState(false);

  const onUpdate = (_, data, { onSuccess }) => {
    setIsUpdateLimitLoading(true);

    updatePolicyLimit(
      { policyId: data.policyId, limit: data.limit },
      {
        onSuccess: () => {
          setIsUpdateLimitLoading(false);
          onSuccess();
        },
        onError: () => setIsUpdateLimitLoading(false)
      }
    );
  };

  return (
    <Box
      sx={{
        width: "250px",
        display: "flex"
      }}
    >
      <EditablePoolPolicyLimit
        isAllowedToEdit={isManagePoolAllowed}
        policyId={policyId}
        policyLimit={policyLimit}
        policyType={policyType}
        formattedPolicyLimit={formattedPolicyLimit}
        onSubmit={onUpdate}
        isLoading={isUpdateLimitLoading}
      />
    </Box>
  );
};

const ResourceLifecycleGlobalPoolPolicies = ({ poolPolicies, isLoading = false }) => {
  const intl = useIntl();

  const formatConstraintLimitMessage = useFormatConstraintLimitMessage();

  const data = useMemo(
    () =>
      poolPolicies.map((poolPolicy) => ({
        ...poolPolicy,
        translatedType: intl.formatMessage({ id: CONSTRAINTS_TYPES[poolPolicy.type] }),
        formattedPolicyLimit: formatConstraintLimitMessage({
          limit: poolPolicy.limit,
          type: poolPolicy.type,
          formats: { ttl: CONSTRAINT_MESSAGE_FORMAT.TEXT }
        })
      })),
    [poolPolicies, intl, formatConstraintLimitMessage]
  );

  const navigate = useNavigate();

  const isAllowedToManageAnyPool = useIsAllowedForSome(
    [...new Set(poolPolicies.map((policy) => policy.pool_id))].map((poolId) => ({
      entityId: poolId,
      entityType: SCOPE_TYPES.POOL,
      requiredActions: ["MANAGE_POOLS"]
    }))
  );

  const columns = useMemo(() => {
    const baseColumns = [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_pool">
            <FormattedMessage id="pool" />
          </TextWithDataTestId>
        ),
        accessorKey: "details.name",
        cell: ({ row: { original } }) => (
          <PoolLabel name={original.details.name} type={original.details.purpose} id={original.details.id} />
        ),
        defaultSort: "asc"
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_policy_type">
            <FormattedMessage id="policyType" />
          </TextWithDataTestId>
        ),
        accessorKey: "translatedType"
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_limit">
            <FormattedMessage id="limit" />
          </TextWithDataTestId>
        ),
        enableSorting: false,
        accessorKey: "formattedPolicyLimit",
        cell: ({ row: { original } }) => {
          const { id, limit, type, pool_id: poolId, formattedPolicyLimit } = original;
          return (
            <UpdatePoolPolicyContainer
              policyId={id}
              policyLimit={limit}
              formattedPolicyLimit={formattedPolicyLimit}
              policyType={type}
              poolId={poolId}
            />
          );
        }
      }
    ];
    return [
      ...baseColumns,
      ...(isAllowedToManageAnyPool
        ? [
            {
              header: (
                <TextWithDataTestId dataTestId="lbl_actions">
                  <FormattedMessage id="actions" />
                </TextWithDataTestId>
              ),
              enableSorting: false,
              id: "actions",
              cell: ({ row: { original } }) => {
                const { id, pool_id: poolId, active } = original;

                return <UpdatePoolPolicyActivityContainer policyId={id} poolId={poolId} active={active} />;
              }
            }
          ]
        : [])
    ];
  }, [isAllowedToManageAnyPool]);

  const actionBarDefinition = {
    items: [
      {
        key: "add",
        icon: <AddOutlinedIcon fontSize="small" />,
        messageId: "add",
        color: "success",
        variant: "contained",
        type: "button",
        dataTestId: "btn_add",
        action: () => navigate(RESOURCE_LIFECYCLE_CREATE_POOL_POLICY)
      }
    ]
  };

  return (
    <Stack spacing={SPACING_2}>
      <div>
        {isLoading ? (
          <TableLoader columnsCounter={columns.length} />
        ) : (
          <Table
            withSearch
            data={data}
            localization={{
              emptyMessageId: "noPoolPolicies"
            }}
            columns={columns}
            actionBar={{
              show: true,
              definition: actionBarDefinition
            }}
          />
        )}
      </div>
      <div>
        <InlineSeverityAlert messageId="globalPoolPoliciesDescription" />
      </div>
    </Stack>
  );
};

export default ResourceLifecycleGlobalPoolPolicies;
