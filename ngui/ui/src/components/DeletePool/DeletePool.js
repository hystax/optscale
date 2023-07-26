import React from "react";
import PropTypes from "prop-types";
import Button from "components/Button";
import { DeletePoolModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";

const DeletePool = ({ poolId }) => {
  const openSideModal = useOpenSideModal();

  return (
    <Button
      dataTestId="btn_delete"
      variant="contained"
      color="error"
      messageId="delete"
      onClick={() => openSideModal(DeletePoolModal, { poolId })}
    />
  );
};

DeletePool.propTypes = {
  poolId: PropTypes.string.isRequired
};

export default DeletePool;
