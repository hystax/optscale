import { useSearchParams } from "react-router-dom";
import ActionBar from "components/ActionBar";
import BillingSubscription from "components/BillingSubscription";
import OrganizationSettings from "components/OrganizationSettings";
import PageContentWrapper from "components/PageContentWrapper";
import TabsWrapper from "components/TabsWrapper";
import InvitationsContainer from "containers/InvitationsContainer";
import SshSettingsContainer from "containers/SshSettingsContainer";
import UserEmailNotificationSettingsContainer from "containers/UserEmailNotificationSettingsContainer";
import { useIsOptScaleCapabilityEnabled } from "hooks/useIsOptScaleCapabilityEnabled";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { OPTSCALE_CAPABILITY, SETTINGS_TABS } from "utils/constants";
import { getEnvironmentVariable } from "utils/env";

const actionBarDefinition = {
  title: {
    messageId: "settings",
  },
};

const TAB_SEARCH_PARAM_NAME = "tab";

const Settings = () => {
  const isFinOpsCapabilityEnabled = useIsOptScaleCapabilityEnabled(OPTSCALE_CAPABILITY.FINOPS);

  const [searchParams, setSearchParams] = useSearchParams();

  const { isDemo } = useOrganizationInfo();

  const isBillingIntegrationEnabled = getEnvironmentVariable("VITE_BILLING_INTEGRATION") === "enabled";

  const tabs = [
    {
      title: SETTINGS_TABS.ORGANIZATION,
      dataTestId: `tab_${SETTINGS_TABS.ORGANIZATION}`,
      node: <OrganizationSettings />,
    },
    ...(isDemo || !isBillingIntegrationEnabled
      ? []
      : [
          {
            title: SETTINGS_TABS.SUBSCRIPTION,
            dataTestId: `tab_${SETTINGS_TABS.SUBSCRIPTION}`,
            node: <BillingSubscription />,
          },
        ]),
    {
      title: SETTINGS_TABS.INVITATIONS,
      dataTestId: `tab_${SETTINGS_TABS.INVITATIONS}`,
      node: <InvitationsContainer />,
    },
    ...(isFinOpsCapabilityEnabled
      ? [
          {
            title: SETTINGS_TABS.SSH,
            dataTestId: `tab_${SETTINGS_TABS.SSH}`,
            node: <SshSettingsContainer />,
          },
        ]
      : []),
    {
      title: SETTINGS_TABS.EMAIL_NOTIFICATIONS,
      dataTestId: `tab_${SETTINGS_TABS.EMAIL_NOTIFICATIONS}`,
      node: <UserEmailNotificationSettingsContainer />,
    },
  ];

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <TabsWrapper
          tabsProps={{
            name: "settings",
            tabs,
            defaultTab: SETTINGS_TABS.ORGANIZATION,
            activeTab: searchParams.get(TAB_SEARCH_PARAM_NAME),
            handleChange: (event, value) => {
              setSearchParams({ [TAB_SEARCH_PARAM_NAME]: value });
            },
          }}
        />
      </PageContentWrapper>
    </>
  );
};

export default Settings;
