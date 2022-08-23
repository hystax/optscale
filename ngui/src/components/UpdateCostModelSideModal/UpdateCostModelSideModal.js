import React from "react";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";
import SideModal from "components/SideModal";

const UpdateCostModelSideModal = ({ isOpen, setIsOpen, children }) => (
  <SideModal
    isOpen={isOpen}
    headerProps={{
      messageId: "updateCostModelTitle",
      color: "primary",
      dataTestIds: {
        title: "lbl_update_cost_model",
        closeButton: "btn_close"
      }
    }}
    closeHandler={setIsOpen}
    dataTestId="smodal_update_cost_model"
  >
    <Box pl={2} pr={2}>
      {children}
    </Box>
  </SideModal>
);

UpdateCostModelSideModal.propTypes = {
  children: PropTypes.node.isRequired,
  isOpen: PropTypes.bool.isRequired,
  setIsOpen: PropTypes.func.isRequired
};

export default UpdateCostModelSideModal;
