import ConnectCloudAccountForm from "components/ConnectCloudAccountForm";

export default {
  component: ConnectCloudAccountForm
};

export const basic = () => (
  <ConnectCloudAccountForm organizationId="test" onSubmit={() => {}} isLoading={false} sendState="test" />
);
