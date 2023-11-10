import ContentBackdrop from "components/ContentBackdrop";
import { TOURS } from "components/Tour";
import { useRootData } from "hooks/useRootData";
import { useShouldRenderConnectCloudAccountMock } from "hooks/useShouldRenderConnectCloudAccountMock";
import BannerContent, { getBannerIcon } from "./BannerContent";

const MESSAGE_TYPES = Object.freeze({
  ASSIGNMENT_RULES: "assignmentRules",
  CLOUD_ACCOUNTS: "cloudAccounts",
  AWS_CLOUD_ACCOUNTS: "awsCloudAccounts",
  K8S_RIGHTSIZING: "k8sRightsizing",
  RECOMMENDATIONS: "recommendations",
  POOLS: "pools",
  ENVIRONMENTS: "environments",
  DASHBOARD: "dashboard",
  ANOMALY_DETECTION_POLICY: "anomalyDetectionPolicy",
  QUOTAS_AND_BUDGETS_POLICY: "quotasAndBudgetsPolicy",
  TAGGING_POLICY: "taggingPolicy"
});

const renderMock = (backdropCondition, mock, backdropMessageType) =>
  backdropCondition ? (
    <ContentBackdrop
      icon={getBannerIcon(backdropMessageType)}
      bannerContent={<BannerContent messageType={backdropMessageType} />}
    >
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
  mock = children,
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

export default Mocked;
export { MESSAGE_TYPES };
