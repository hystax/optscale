import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
import ButtonLoader from "components/ButtonLoader";
import { useCreateStripeBillingPortalSessionMutation } from "graphql/__generated__/hooks/restapi";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const ManageSubscriptionButton = () => {
  const { organizationId } = useOrganizationInfo();

  const [createStripeBillingPortalSession, { loading: createStripeBillingPortalSessionLoading }] =
    useCreateStripeBillingPortalSessionMutation();

  const handleManageSubscription = async () => {
    const { data } = await createStripeBillingPortalSession({
      variables: {
        organizationId,
      },
    });

    if (data?.createStripeBillingPortalSession?.url) {
      window.open(data.createStripeBillingPortalSession.url, "_blank", "noopener,noreferrer");
    }
  };

  return (
    <ButtonLoader
      messageId="manage"
      fullWidth
      color="primary"
      startIcon={<SettingsOutlinedIcon />}
      onClick={handleManageSubscription}
      isLoading={createStripeBillingPortalSessionLoading}
    />
  );
};

export default ManageSubscriptionButton;
