import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import SubTitle from "components/SubTitle";
import { ROLE_PURPOSES } from "utils/constants";

const InviteListElement = ({ message, variant }) => <Typography variant={variant}>●&nbsp;{message}</Typography>;

const InvitesToOrganizationList = ({ invites }) =>
  invites.map((el) => (
    <InviteListElement
      key={el.scope_id}
      message={
        <FormattedMessage
          id="roleOfOrganization"
          values={{
            role: <FormattedMessage id={ROLE_PURPOSES[el.purpose]} />,
            organization: el.scope_name,
            strong: (chunks) => <strong>{chunks}</strong>
          }}
        />
      }
    />
  ));

const InvitesToPoolsList = ({ invites }) =>
  invites.map((el) => (
    <InviteListElement
      key={el.scope_id}
      message={
        <FormattedMessage
          id="roleAtPool"
          values={{
            role: <FormattedMessage id={ROLE_PURPOSES[el.purpose]} />,
            pool: el.scope_name,
            strong: (chunks) => <strong>{chunks}</strong>
          }}
        />
      }
    />
  ));

const Invitation = ({ owner, organizationNameInvitedTo, invitesToOrganization, invitesToPools }) => {
  const { name: ownerName, email: ownerEmail } = owner;

  const shouldRenderTitle = ownerName && ownerEmail && organizationNameInvitedTo;

  return (
    <>
      {shouldRenderTitle && (
        <SubTitle>
          <FormattedMessage
            id="acceptInvitationTitle"
            values={{
              strong: (chunks) => <strong>{chunks}</strong>,
              ownerName,
              ownerEmail,
              organization: organizationNameInvitedTo
            }}
          />
        </SubTitle>
      )}
      <Typography gutterBottom>
        <FormattedMessage id="willGetFollowingRoles" />
      </Typography>
      <InvitesToOrganizationList invites={invitesToOrganization} />
      <InvitesToPoolsList invites={invitesToPools} />
    </>
  );
};

export default Invitation;
