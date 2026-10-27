import { ReactNode } from "react";
import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import SubTitle from "components/SubTitle";
import Tooltip from "components/Tooltip";
import { ROLE_PURPOSES } from "utils/constants";
import { sliceByLimitWithEllipsis } from "utils/strings";
import { TODO } from "utils/types";

type InviteListElementProps = {
  message: ReactNode;
};

type PermissionsListProps = {
  roleTargetMessageId: string;
  invites: TODO[];
};

type AcceptInvitationTitleProps = {
  ownerName: string;
  ownerEmail: string;
  organizationNameInvitedTo: string;
};

type InvitationProps = {
  owner: {
    name: string;
    email: string;
  };
  organizationNameInvitedTo: string;
  invitesToOrganization: TODO[];
  invitesToPools: TODO[];
};

const MAX_ROLE_TARGET_LENGTH = 64;

const InviteListElement = ({ message }: InviteListElementProps) => <Typography>●&nbsp;{message}</Typography>;

const PermissionsList = ({ roleTargetMessageId, invites }: PermissionsListProps) =>
  invites.map((invite) => {
    const isNameLong = invite.scope_name.length > MAX_ROLE_TARGET_LENGTH;

    return (
      <InviteListElement
        key={invite.scope_id}
        message={
          <FormattedMessage
            id={roleTargetMessageId}
            values={{
              role: <FormattedMessage id={ROLE_PURPOSES[invite.purpose]} />,
              target: (
                <Tooltip title={isNameLong ? invite.scope_name : undefined}>
                  <span>
                    {isNameLong ? sliceByLimitWithEllipsis(invite.scope_name, MAX_ROLE_TARGET_LENGTH) : invite.scope_name}
                  </span>
                </Tooltip>
              ),
              strong: (chunks) => <strong>{chunks}</strong>,
            }}
          />
        }
      />
    );
  });

const AcceptInvitationTitle = ({ ownerName, ownerEmail, organizationNameInvitedTo }: AcceptInvitationTitleProps) => {
  const isNameLong = organizationNameInvitedTo.length > MAX_ROLE_TARGET_LENGTH;

  return (
    <SubTitle>
      <FormattedMessage
        id="acceptInvitationTitle"
        values={{
          strong: (chunks) => <strong>{chunks}</strong>,
          ownerName,
          ownerEmail,
          organization: (
            <Tooltip title={isNameLong ? organizationNameInvitedTo : undefined}>
              <span>
                {isNameLong
                  ? sliceByLimitWithEllipsis(organizationNameInvitedTo, MAX_ROLE_TARGET_LENGTH)
                  : organizationNameInvitedTo}
              </span>
            </Tooltip>
          ),
        }}
      />
    </SubTitle>
  );
};

const Invitation = ({ owner, organizationNameInvitedTo, invitesToOrganization, invitesToPools }: InvitationProps) => {
  const { name: ownerName, email: ownerEmail } = owner;

  const shouldRenderTitle = ownerName && ownerEmail && organizationNameInvitedTo;

  return (
    <>
      {shouldRenderTitle && (
        <AcceptInvitationTitle
          ownerName={ownerName}
          ownerEmail={ownerEmail}
          organizationNameInvitedTo={organizationNameInvitedTo}
        />
      )}
      <Typography gutterBottom>
        <FormattedMessage id="willGetFollowingRoles" />
      </Typography>
      <PermissionsList roleTargetMessageId="roleOfOrganization" invites={invitesToOrganization} />
      <PermissionsList roleTargetMessageId="roleAtPool" invites={invitesToPools} />
    </>
  );
};

export default Invitation;
