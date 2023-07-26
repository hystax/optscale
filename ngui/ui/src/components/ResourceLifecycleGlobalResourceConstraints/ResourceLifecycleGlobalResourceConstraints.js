import React, { useMemo, useState } from "react";
import CreateOutlinedIcon from "@mui/icons-material/CreateOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import Link from "@mui/material/Link";
import { Box } from "@mui/system";
import PropTypes from "prop-types";
import { FormattedMessage, useIntl } from "react-intl";
import { useDispatch } from "react-redux";
import { updateGlobalResourceConstraintLimit } from "api";
import { UPDATE_GLOBAL_RESOURCE_CONSTRAINT_LIMIT } from "api/restapi/actionTypes";
import CaptionedCell from "components/CaptionedCell";
import { useFormatConstraintLimitMessage } from "components/ConstraintMessage/ConstraintLimitMessage";
import EditResourceConstraintForm from "components/EditResourceConstraintForm";
import IconButton from "components/IconButton";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import PoolLabel from "components/PoolLabel";
import ResourceCell from "components/ResourceCell";
import { DeleteGlobalResourceConstraintModal } from "components/SideModalManager/SideModals";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import {
  useIsAllowedToManageAnyResourceConstraint,
  useIsAllowedToManageResourceConstraint
} from "hooks/useResourceConstraintPermissions";
import { RESOURCES } from "urls";
import { checkError } from "utils/api";
import { CONSTRAINTS_TYPES, CONSTRAINT_MESSAGE_FORMAT } from "utils/constraints";
import { getResourceDisplayedName } from "utils/resources";
import { RESOURCE_ID_COLUMN_CELL_STYLE } from "utils/tables";

const UpdateConstraintLimitContainer = ({ limit, formattedConstraintLimit, constraintId, type, employeeId, resourceId }) => {
  const dispatch = useDispatch();

  const [isEditModeOn, setIsEditModeOn] = useState(false);

  const [isLoading, setIsLoading] = useState(false);

  const isAllowedToEdit = useIsAllowedToManageResourceConstraint(employeeId, resourceId);

  const updateConstraint = (formData, { onSuccess }) => {
    setIsLoading(true);
    dispatch((_, getState) => {
      dispatch(updateGlobalResourceConstraintLimit(formData.policyId, formData.limit))
        .then(() => checkError(UPDATE_GLOBAL_RESOURCE_CONSTRAINT_LIMIT, getState()))
        .then(() => {
          setIsLoading(false);
          onSuccess();
        })
        .catch(() => {
          setIsLoading(false);
        });
    });
  };

  return isEditModeOn ? (
    <EditResourceConstraintForm
      constraintType={type}
      constraintLimit={limit}
      constraintId={constraintId}
      onSubmit={updateConstraint}
      onSuccess={() => setIsEditModeOn(false)}
      onCancel={() => setIsEditModeOn(false)}
      isLoading={isLoading}
    />
  ) : (
    <Box display="flex" alignItems="center">
      {formattedConstraintLimit}
      {isAllowedToEdit && (
        <IconButton
          dataTestId={`btn_edit_${type}`}
          icon={<CreateOutlinedIcon />}
          onClick={() => setIsEditModeOn(true)}
          tooltip={{
            show: true,
            messageId: "edit"
          }}
        />
      )}
    </Box>
  );
};

const DeleteResourceConstraintButton = ({ employeeId, resourceId, onClick }) => {
  const isAllowedToEdit = useIsAllowedToManageResourceConstraint(employeeId, resourceId);

  return (
    isAllowedToEdit && (
      <IconButton
        color="error"
        icon={<DeleteOutlinedIcon />}
        onClick={onClick}
        tooltip={{
          show: true,
          value: <FormattedMessage id="delete" />
        }}
      />
    )
  );
};

const ResourceLifecycleGlobalResourceConstraints = ({ constraints, isLoading = false }) => {
  const intl = useIntl();
  const openSideModal = useOpenSideModal();

  const formatConstraintLimitMessage = useFormatConstraintLimitMessage();

  const data = useMemo(
    () =>
      constraints.map((constraint) => ({
        ...constraint,
        // make fields searchable
        resource: [constraint.details?.cloud_resource_id, constraint.details?.cloud_resource_hash, constraint.details?.name]
          .filter(Boolean)
          .join(" "),
        "pool/owner": [constraint.details?.pool?.name, constraint.details?.owner?.name].filter(Boolean).join(" "),
        translatedType: intl.formatMessage({ id: CONSTRAINTS_TYPES[constraint.type] }),
        formattedConstraintLimit: formatConstraintLimitMessage({
          limit: constraint.limit,
          type: constraint.type,
          formats: { ttl: CONSTRAINT_MESSAGE_FORMAT.EXPIRES_AT_DATETIME }
        })
      })),
    [constraints, formatConstraintLimitMessage, intl]
  );

  const isAllowedToEditAnyResourcePolicy = useIsAllowedToManageAnyResourceConstraint([
    ...new Set(
      constraints.map(({ details: { employee_id: employeeId } = {}, resource_id: resourceId }) => ({ resourceId, employeeId }))
    )
  ]);

  const columns = useMemo(() => {
    const baseColumns = [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_resource">
            <FormattedMessage id="resource" />
          </TextWithDataTestId>
        ),
        accessorKey: "resource",
        style: RESOURCE_ID_COLUMN_CELL_STYLE,
        cell: ({ row: { original, id } }) => {
          const rowData = {
            resource_id: original.resource_id,
            cloud_resource_id: original.details.cloud_resource_id,
            cloud_resource_hash: original.details.cloud_resource_hash,
            resource_name: original.details.name,
            active: original.details.active,
            constraint_violated: original.details.constraint_violated
          };

          return (
            <ResourceCell
              rowData={rowData}
              dataTestIds={{ labelIds: { label: `resource_name_${id}` } }}
              disableConstraintViolationIcon
            />
          );
        },
        defaultSort: "asc",
        enableHiding: false
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_pool_owner">
            <FormattedMessage id="pool/owner" />
          </TextWithDataTestId>
        ),
        accessorKey: "pool/owner",
        style: {
          whiteSpace: "nowrap"
        },
        cell: ({ row: { original } }) => {
          const {
            details: {
              pool: { id: poolId, name: poolName, purpose: poolPurpose } = {},
              owner: { id: ownerId, name: ownerName } = {}
            } = {}
          } = original;

          return poolId || ownerId ? (
            <CaptionedCell caption={ownerId ? ownerName : ""}>
              {poolId && <PoolLabel id={poolId} name={poolName} type={poolPurpose} />}
            </CaptionedCell>
          ) : null;
        }
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
        accessorKey: "formattedConstraintLimit",
        style: {
          minWidth: "400px"
        },
        enableSorting: false,
        cell: ({ row: { original } }) => {
          const {
            formattedConstraintLimit,
            limit,
            type,
            id,
            resource_id: resourceId,
            details: { employee_id: employeeId } = {}
          } = original;

          return (
            <UpdateConstraintLimitContainer
              limit={limit}
              formattedConstraintLimit={formattedConstraintLimit}
              type={type}
              constraintId={id}
              resourceId={resourceId}
              employeeId={employeeId}
            />
          );
        }
      }
    ];

    return [
      ...baseColumns,
      ...(isAllowedToEditAnyResourcePolicy
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
                const {
                  id,
                  type,
                  resource_id: resourceId,
                  details: { name: resourceName, employee_id: employeeId } = {}
                } = original;

                return (
                  <DeleteResourceConstraintButton
                    resourceId={resourceId}
                    employeeId={employeeId}
                    onClick={() => {
                      openSideModal(DeleteGlobalResourceConstraintModal, {
                        id,
                        type,
                        resourceName,
                        resourceDisplayedName: getResourceDisplayedName(original.details)
                      });
                    }}
                  />
                );
              }
            }
          ]
        : [])
    ];
  }, [isAllowedToEditAnyResourcePolicy, openSideModal]);

  return (
    <>
      {isLoading ? (
        <TableLoader columnsCounter={columns.length} />
      ) : (
        <Table withSearch data={data} columns={columns} localization={{ emptyMessageId: "noResourceConstraints" }} />
      )}
      <InlineSeverityAlert
        messageId="globalResourceConstraintsDescription"
        messageValues={{
          link: (chunks) => (
            <Link href={RESOURCES} target="_blank" rel="noopener">
              {chunks}
            </Link>
          )
        }}
      />
    </>
  );
};

ResourceLifecycleGlobalResourceConstraints.propTypes = {
  constraints: PropTypes.array.isRequired,
  isLoading: PropTypes.bool
};

export default ResourceLifecycleGlobalResourceConstraints;
