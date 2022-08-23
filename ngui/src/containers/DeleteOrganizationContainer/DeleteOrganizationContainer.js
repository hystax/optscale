import React, { useState } from "react";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { deleteOrganization } from "api";
import { DELETE_ORGANIZATION } from "api/restapi/actionTypes";
import DeleteEntity from "components/DeleteEntity";
import Input from "components/Input";
import OrganizationLabel from "components/OrganizationLabel";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { SIGNOUT } from "urls";
import { isError } from "utils/api";

const CONFIRMATION_TEXT = "delete";

const DeleteOrganizationContainer = ({ onCancel }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const { name: organizationName, organizationId } = useOrganizationInfo();

  const [confirmationTextInputValue, setConfirmationTextInputValue] = useState("");

  const { isLoading } = useApiState(DELETE_ORGANIZATION);

  const onDelete = () => {
    dispatch((_, getState) => {
      dispatch(deleteOrganization(organizationId)).then(() => {
        if (!isError(DELETE_ORGANIZATION, getState())) {
          onCancel();
          navigate(SIGNOUT);
        }
      });
    });
  };

  return (
    <DeleteEntity
      message={{
        messageId: "deleteOrganizationQuestion",
        values: {
          organizationName: <OrganizationLabel name={organizationName} disableLink />
        }
      }}
      deleteButtonProps={{
        disabled: confirmationTextInputValue !== CONFIRMATION_TEXT,
        onDelete
      }}
      onCancel={onCancel}
      isLoading={isLoading}
    >
      <Typography>
        <FormattedMessage id="youWillBeForcedToSignOut" />
      </Typography>
      <Typography>
        <FormattedMessage
          id="toConfirmTheDeletionOfOrganization"
          values={{ confirmationText: CONFIRMATION_TEXT, i: (chunks) => <i>{chunks}</i> }}
        />
      </Typography>
      <Input value={confirmationTextInputValue} onChange={(e) => setConfirmationTextInputValue(e.target.value)} />
    </DeleteEntity>
  );
};

DeleteOrganizationContainer.propTypes = {
  onCancel: PropTypes.func.isRequired
};

export default DeleteOrganizationContainer;
