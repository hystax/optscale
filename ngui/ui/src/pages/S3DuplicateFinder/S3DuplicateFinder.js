import React from "react";
import Mocked, { MESSAGE_TYPES } from "components/Mocked";
import { S3DuplicateFinderMocked } from "components/S3DuplicateFinder";
import S3DuplicateFinderContainer from "containers/S3DuplicatesContainer";
import { useShouldRenderConnectCloudAccountMock } from "hooks/useShouldRenderConnectCloudAccountMock";
import { AWS_CNR } from "utils/constants";

const S3DuplicateFinder = () => {
  const shouldRenderConnectCloudAccountMock = useShouldRenderConnectCloudAccountMock(AWS_CNR);

  return (
    <Mocked
      mockCondition={shouldRenderConnectCloudAccountMock}
      backdropMessageType={MESSAGE_TYPES.AWS_CLOUD_ACCOUNTS}
      mock={<S3DuplicateFinderMocked />}
    >
      <S3DuplicateFinderContainer />
    </Mocked>
  );
};

export default S3DuplicateFinder;
