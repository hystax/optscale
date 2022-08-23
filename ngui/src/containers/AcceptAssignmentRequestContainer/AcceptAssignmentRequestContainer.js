import React from "react";
import CheckCircleOutlineOutlinedIcon from "@mui/icons-material/CheckCircleOutlineOutlined";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { ASSIGNMENT_REQUEST_UPDATE } from "api/restapi/actionTypes";
import IconButton from "components/IconButton";
import { AcceptAssignmentRequestModal } from "components/SideModalManager/SideModals";
import { useApiState } from "hooks/useApiState";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { ACCEPT } from "utils/constants";

// TODO: We will remove this component when we can add the AvailablePoolSelectorContainer to the table row.
const AcceptAssignmentRequestContainer = ({ assignmentRequestId, resourceName }) => {
  const { isLoading, entityId } = useApiState(ASSIGNMENT_REQUEST_UPDATE, assignmentRequestId);
  const openSideModal = useOpenSideModal();

  return (
    <IconButton
      isLoading={assignmentRequestId === entityId ? isLoading : false}
      color="success"
      icon={<CheckCircleOutlineOutlinedIcon />}
      onClick={() =>
        openSideModal(AcceptAssignmentRequestModal, {
          assignmentRequestId,
          resourceName
        })
      }
      tooltip={{
        show: true,
        value: <FormattedMessage id={ACCEPT} />
      }}
    />
  );
};

AcceptAssignmentRequestContainer.propTypes = {
  assignmentRequestId: PropTypes.string.isRequired,
  resourceName: PropTypes.string
};

export default AcceptAssignmentRequestContainer;
