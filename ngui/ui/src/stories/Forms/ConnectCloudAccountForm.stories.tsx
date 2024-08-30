import ConnectCloudAccountForm from "components/forms/ConnectCloudAccountForm";

export default {
  component: ConnectCloudAccountForm
};

export const basic = () => (
  <ConnectCloudAccountForm organizationId="test" onSubmit={() => {}} isLoading={false} sendState="test" />
);
