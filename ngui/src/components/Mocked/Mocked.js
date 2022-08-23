import React from "react";
import PropTypes from "prop-types";
import ContentBackdrop, { MESSAGE_TYPES } from "components/ContentBackdrop";
import { TOURS } from "components/ProductTour";
import { useRootData } from "hooks/useRootData";
import { useShouldRenderConnectCloudAccountMock } from "hooks/useShouldRenderConnectCloudAccountMock";

const renderMock = (backdropCondition, mock, backdropMessageType) =>
  backdropCondition ? (
    <ContentBackdrop isFixed messageType={backdropMessageType}>
      {mock}
    </ContentBackdrop>
  ) : (
    mock
  );

const connectCloudAccountMocksTypes = [
  MESSAGE_TYPES.CLOUD_ACCOUNTS,
  MESSAGE_TYPES.DASHBOARD,
  MESSAGE_TYPES.RECOMMENDATIONS,
  MESSAGE_TYPES.K8S_RIGHTSIZING
];

const Mocked = ({
  children,
  mock,
  backdropMessageType = MESSAGE_TYPES.CLOUD_ACCOUNTS,
  backdropCondition = true,
  mockCondition = false
}) => {
  const { rootData: tours = {} } = useRootData(TOURS);

  const isTourOpen = Object.values(tours).some((el) => el.isOpen);

  const shouldRenderConnectCloudAccountMock = useShouldRenderConnectCloudAccountMock();

  const shouldRenderMock =
    mockCondition || (shouldRenderConnectCloudAccountMock && connectCloudAccountMocksTypes.indexOf(backdropMessageType) !== -1);
  const shouldRenderBackdrop = backdropCondition && !isTourOpen;

  return shouldRenderMock ? renderMock(shouldRenderBackdrop, mock, backdropMessageType) : children;
};

Mocked.propTypes = {
  children: PropTypes.node.isRequired,
  mock: PropTypes.node.isRequired,
  backdropMessageType: PropTypes.string,
  backdropCondition: PropTypes.bool,
  mockCondition: PropTypes.bool
};

export default Mocked;
