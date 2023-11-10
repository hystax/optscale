import { useState } from "react";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import { deleteOrganization } from "api";
import { DELETE_ORGANIZATION } from "api/restapi/actionTypes";
import DeleteEntity from "components/DeleteEntity";
import Input from "components/Input";
import OrganizationLabel from "components/OrganizationLabel";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { useSignOut } from "hooks/useSignOut";
import { isError } from "utils/api";

const CONFIRMATION_TEXT = "delete";

const DeleteOrganizationContainer = ({ onCancel }) => {
  const dispatch = useDispatch();

  const { name: organizationName, organizationId } = useOrganizationInfo();

  const [confirmationTextInputValue, setConfirmationTextInputValue] = useState("");

  const { isLoading } = useApiState(DELETE_ORGANIZATION);

  const signOut = useSignOut();

  const onDelete = () => {
    dispatch((_, getState) => {
      dispatch(deleteOrganization(organizationId)).then(() => {
        if (!isError(DELETE_ORGANIZATION, getState())) {
          onCancel();
          signOut();
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

export default DeleteOrganizationContainer;
