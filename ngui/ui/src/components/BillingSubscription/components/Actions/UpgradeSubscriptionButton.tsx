import { ReactNode } from "react";
import RocketLaunchOutlinedIcon from "@mui/icons-material/RocketLaunchOutlined";
import ButtonLoader from "components/ButtonLoader";
import { useCreateStripeCheckoutSessionMutation } from "graphql/__generated__/hooks/restapi";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

type UpgradeSubscriptionButtonProps = {
  text: ReactNode;
  billingSubscriptionPlanId: string;
};

const UpgradeSubscriptionButton = ({ text, billingSubscriptionPlanId }: UpgradeSubscriptionButtonProps) => {
  const { organizationId } = useOrganizationInfo();

  const [createStripeCheckoutSession, { loading: createStripeCheckoutSessionLoading }] =
    useCreateStripeCheckoutSessionMutation();

  const handleUpgrade = async () => {
    const { data } = await createStripeCheckoutSession({
      variables: {
        organizationId,
        params: {
          plan_id: billingSubscriptionPlanId,
        },
      },
    });

    if (data?.createStripeCheckoutSession?.url) {
      window.open(data.createStripeCheckoutSession.url, "_blank", "noopener,noreferrer");
    }
  };

  return (
    <ButtonLoader
      color="primary"
      onClick={handleUpgrade}
      text={text}
      size="small"
      variant="contained"
      fullWidth
      isLoading={createStripeCheckoutSessionLoading}
      startIcon={<RocketLaunchOutlinedIcon />}
    />
  );
};

export default UpgradeSubscriptionButton;
