import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import ButtonLoader from "components/ButtonLoader";
import CopyText from "components/CopyText";
import MailTo from "components/MailTo";
import { ConnectGoogleCalendarModal, DisconnectGoogleCalendarModal } from "components/SideModalManager/SideModals";
import TextBlock from "components/TextBlock";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import GoogleCalendarIcon from "icons/GoogleCalendarIcon";
import { EMAIL_SUPPORT } from "urls";
import { getTimeDistance } from "utils/datetime";
import { isEmpty } from "utils/objects";
import Integration from "../Integration";
import Title from "../Title";

export const GOOGLE_CALENDAR = "googleCalendar";

const GOOGLE_CALENDAR_STATUS = Object.freeze({
  ALL_DISABLED: "allDisabled",
  CAN_CONNECT: "canConnect",
  CAN_DISCONNECT: "canDisconnect"
});

const getBlocksDependingOnCalendarConnectionStatus = ({ googleCalendarStatus, isLoading, shareableLink, lastCompleted }) => {
  switch (googleCalendarStatus) {
    case GOOGLE_CALENDAR_STATUS.ALL_DISABLED:
    case GOOGLE_CALENDAR_STATUS.CAN_CONNECT:
      return [<TextBlock color="error" isLoading={isLoading} key="calendarNotConnected" messageId="calendarNotConnected" />];
    case GOOGLE_CALENDAR_STATUS.CAN_DISCONNECT: {
      const lastSync = lastCompleted ? getTimeDistance(lastCompleted) : 0;
      return [
        <TextBlock color="success" isLoading={isLoading} key="calendarConnected" messageId="calendarConnected" />,
        <TextBlock
          isLoading={isLoading}
          key="description2"
          messageId="integrationsGoogleCalendarDescription2"
          values={{
            link: <CopyText text={shareableLink}>{shareableLink}</CopyText>
          }}
        />,
        <TextBlock
          isLoading={isLoading}
          key="lastSyncAgo"
          messageId="lastSync"
          values={{
            value:
              lastSync === 0 ? <FormattedMessage id="never" /> : <FormattedMessage id="timeAgo" values={{ time: lastSync }} />
          }}
        />
      ];
    }
    default:
      return [];
  }
};

const getBlocks = (googleCalendarStatus, isLoading, { shareable_link: shareableLink, last_completed: lastCompleted }) => {
  const defaultBlocks = [
    <TextBlock isLoading={isLoading} key="description1" messageId="integrationsGoogleCalendarDescription1" />
  ];
  return [
    ...defaultBlocks,
    ...getBlocksDependingOnCalendarConnectionStatus({ googleCalendarStatus, isLoading, shareableLink, lastCompleted })
  ];
};

const getButton = ({ googleCalendarStatus, isLoading, canUpdate, canDelete, openConnectModal, openDisconnectModal }) => {
  switch (googleCalendarStatus) {
    case GOOGLE_CALENDAR_STATUS.ALL_DISABLED:
      return <ButtonLoader isLoading={isLoading} color="primary" variant="contained" messageId="connectCalendar" />;
    case GOOGLE_CALENDAR_STATUS.CAN_CONNECT:
      return (
        <ButtonLoader
          onClick={openConnectModal}
          isLoading={isLoading}
          disabled={!canUpdate}
          startIcon={<GoogleCalendarIcon />}
          tooltip={{
            show: !canUpdate,
            messageId: "onlyOrganizationManagersCanSetThisUp"
          }}
          color="primary"
          messageId="connectCalendar"
        />
      );
    case GOOGLE_CALENDAR_STATUS.CAN_DISCONNECT:
      return (
        <ButtonLoader
          onClick={openDisconnectModal}
          isLoading={isLoading}
          disabled={!canDelete}
          tooltip={{
            show: !canDelete,
            messageId: "onlyOrganizationManagersCanDisconnectThis"
          }}
          color="error"
          variant="contained"
          messageId="disconnectCalendar"
        />
      );
    default:
      return null;
  }
};

const getGoogleCalendarStatus = (serviceAccount, calendarSynchronization) => {
  let googleCalendarStatus = GOOGLE_CALENDAR_STATUS.ALL_DISABLED;

  if (serviceAccount && isEmpty(calendarSynchronization)) {
    googleCalendarStatus = GOOGLE_CALENDAR_STATUS.CAN_CONNECT;
  }
  if (!isEmpty(calendarSynchronization)) {
    googleCalendarStatus = GOOGLE_CALENDAR_STATUS.CAN_DISCONNECT;
  }
  return googleCalendarStatus;
};

const GoogleCalendar = ({ isLoading, serviceAccount, calendarSynchronization }) => {
  const openSideModal = useOpenSideModal();
  const openConnectModal = () => openSideModal(ConnectGoogleCalendarModal, { serviceAccount });
  const openDisconnectModal = () => openSideModal(DisconnectGoogleCalendarModal, calendarSynchronization);

  const googleCalendarStatus = getGoogleCalendarStatus(serviceAccount, calendarSynchronization);

  const canUpdate = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });
  const canDelete = useIsAllowed({ requiredActions: ["DELETE_PARTNER"] });

  return (
    <Integration
      id={GOOGLE_CALENDAR}
      title={<Title icon={<GoogleCalendarIcon />} label={<FormattedMessage id="googleCalendar" />} />}
      button={getButton({
        googleCalendarStatus,
        isLoading,
        canUpdate,
        canDelete,
        openConnectModal,
        openDisconnectModal
      })}
      withBackdrop={!serviceAccount && !isLoading}
      backdropMessage={{
        id: "notAvailableOnYourSetup",
        values: {
          email: <MailTo email={EMAIL_SUPPORT} text={EMAIL_SUPPORT} />,
          br: <br />
        }
      }}
      blocks={getBlocks(googleCalendarStatus, isLoading, calendarSynchronization)}
    />
  );
};

GoogleCalendar.propTypes = {
  isLoading: PropTypes.bool,
  serviceAccount: PropTypes.string,
  calendarSynchronization: PropTypes.object
};

export default GoogleCalendar;
