import React, { useState } from "react";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import DeleteEntity from "components/DeleteEntity";
import PoolLabel from "components/PoolLabel";
import PoolsService from "services/PoolsService";
import { getPoolUrl } from "urls";

const DeletePoolContainer = ({ id, onCancel }) => {
  const [isConfirmed, setIsConfirmed] = useState(false);
  const navigate = useNavigate();

  const { useGetAvailablePools, useDelete } = PoolsService();
  const { deletePool, isDeletePoolLoading } = useDelete();
  const { data: pools } = useGetAvailablePools();

  const { name, pool_purpose: type, parent_id: parentPoolId } = pools.find((pool) => pool.id === id) || {};

  const onSuccess = () => navigate(getPoolUrl(parentPoolId));
  const onSubmit = () => deletePool(id, onSuccess);

  return (
    <DeleteEntity
      onDelete={onSubmit}
      onCancel={onCancel}
      isLoading={isDeletePoolLoading}
      deleteButtonProps={{
        color: "error",
        variant: "contained",
        disabled: !isConfirmed,
        onDelete: onSubmit
      }}
      dataTestIds={{
        text: "p_delete_pool",
        deleteButton: "btn_sm_delete",
        cancelButton: "btn_sm_cancel"
      }}
      message={{
        messageId: "deletePoolQuestion",
        values: {
          strong: (chunks) => <strong>{chunks}</strong>,
          pool: <PoolLabel name={name} type={type} disableLink />
        }
      }}
    >
      <>
        <Typography data-test-id="p_action_description">
          <FormattedMessage
            id="deletePoolNotice"
            values={{
              strong: (chunks) => <strong>{chunks}</strong>,
              break: <br />
            }}
          />
        </Typography>
        <FormControlLabel
          control={
            <Checkbox data-test-id="checkbox_delete" checked={isConfirmed} onChange={() => setIsConfirmed(!isConfirmed)} />
          }
          label={
            <Typography>
              <FormattedMessage id="deletePoolConfirmText" />
            </Typography>
          }
        />
      </>
    </DeleteEntity>
  );
};

DeletePoolContainer.propTypes = {
  id: PropTypes.string.isRequired,
  onCancel: PropTypes.func.isRequired
};

export default DeletePoolContainer;
