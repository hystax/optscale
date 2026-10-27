import { useState } from "react";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import DeleteEntity from "components/DeleteEntity";
import Input from "components/Input";
import OrganizationLabel from "components/OrganizationLabel";
import { useDeleteOrganizationMutation } from "graphql/__generated__/hooks/restapi";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { useSignOut } from "hooks/useSignOut";

const CONFIRMATION_TEXT = "delete";

const DeleteOrganizationContainer = ({ onCancel }) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  const { name: organizationName, organizationId } = useOrganizationInfo();

  const [confirmationTextInputValue, setConfirmationTextInputValue] = useState("");

  const signOut = useSignOut();

  const [deleteOrganization, { loading }] = useDeleteOrganizationMutation();

  const onDelete = () => {
    deleteOrganization({
      variables: {
        organizationId,
      },
    }).then(() => {
      onCancel();
      signOut();
    });
  };

  return (
    <DeleteEntity
      message={{
        messageId: "deleteOrganizationQuestion",
        values: {
          organizationName: <OrganizationLabel name={organizationName} disableLink />,
        },
      }}
      deleteButtonProps={{
        onDelete,
        disabled: isRestricted || confirmationTextInputValue !== CONFIRMATION_TEXT,
        tooltip: {
          show: isRestricted,
          value: restrictionReasonMessage,
        },
      }}
      onCancel={onCancel}
      isLoading={loading}
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
