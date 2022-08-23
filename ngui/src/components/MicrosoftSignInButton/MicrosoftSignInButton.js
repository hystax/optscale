import React from "react";
import { useMsal } from "@azure/msal-react";
import ButtonLoader from "components/ButtonLoader";
import { useNewAuthorization, PROVIDERS } from "hooks/useNewAuthorization";
import MicrosoftIcon from "icons/MicrosoftIcon";

const handleClick = async (instance, callback) => {
  try {
    const { tenantId, idToken } = await instance.loginPopup({ prompt: "select_account" });
    callback(PROVIDERS.MICROSOFT, { token: idToken, tenant_id: tenantId });
  } catch (error) {
    console.log(error);
  }
};

const MicrosoftSignInButton = () => {
  const { instance, inProgress } = useMsal();

  const {
    thirdPartySignIn,
    isGetTokenLoading,
    isGetOrganizationsLoading,
    isGetInvitationsLoading,
    isCreateOrganizationLoading,
    isSignInLoading
  } = useNewAuthorization();

  const isLoading =
    isGetTokenLoading || isGetOrganizationsLoading || isGetInvitationsLoading || isSignInLoading || isCreateOrganizationLoading;

  const renderMicrosoftLogin = () => (
    <ButtonLoader
      variant="outlined"
      messageId="microsoft"
      size="medium"
      onClick={() => handleClick(instance, thirdPartySignIn)}
      startIcon={<MicrosoftIcon />}
      disabled={inProgress === "startup"}
      fullWidth
      isLoading={isLoading}
    />
  );

  return renderMicrosoftLogin();
};
export default MicrosoftSignInButton;
