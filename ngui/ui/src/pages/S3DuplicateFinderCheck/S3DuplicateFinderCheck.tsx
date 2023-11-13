import Mocked, { MESSAGE_TYPES } from "components/Mocked";
import { S3DuplicateFinderCheckMocked } from "components/S3DuplicateFinderCheck";
import S3DuplicateFinderCheckContainer from "containers/S3DuplicateFinderCheckContainer";
import { useShouldRenderConnectCloudAccountMock } from "hooks/useShouldRenderConnectCloudAccountMock";
import { AWS_CNR } from "utils/constants";

const S3DuplicateFinderCheck = () => {
  const shouldRenderConnectCloudAccountMock = useShouldRenderConnectCloudAccountMock(AWS_CNR);

  return (
    <Mocked
      mockCondition={shouldRenderConnectCloudAccountMock}
      backdropMessageType={MESSAGE_TYPES.AWS_CLOUD_ACCOUNTS}
      mock={<S3DuplicateFinderCheckMocked />}
    >
      <S3DuplicateFinderCheckContainer />
    </Mocked>
  );
};

export default S3DuplicateFinderCheck;
