import ActionBar from "components/ActionBar";
import OrganizationSettings from "components/OrganizationSettings";
import PageContentWrapper from "components/PageContentWrapper";
import TabsWrapper from "components/TabsWrapper";
import InvitationsContainer from "containers/InvitationsContainer";
import ModeContainer from "containers/ModeContainer";
import SshSettingsContainer from "containers/SshSettingsContainer";

const actionBarDefinition = {
  title: {
    messageId: "settings"
  }
};

export const SETTINGS_TABS = Object.freeze({
  ORGANIZATION: "organization",
  INVITATIONS: "invitations",
  MODE: "mode",
  SSH: "sshKeys"
});

const tabs = [
  {
    title: SETTINGS_TABS.ORGANIZATION,
    dataTestId: `tab_${SETTINGS_TABS.ORGANIZATION}`,
    node: <OrganizationSettings />
  },
  {
    title: SETTINGS_TABS.INVITATIONS,
    dataTestId: `tab_${SETTINGS_TABS.INVITATIONS}`,
    node: <InvitationsContainer />
  },
  {
    title: SETTINGS_TABS.MODE,
    dataTestId: `tab_${SETTINGS_TABS.MODE}`,
    node: <ModeContainer />
  },
  {
    title: SETTINGS_TABS.SSH,
    dataTestId: `tab_${SETTINGS_TABS.SSH}`,
    node: <SshSettingsContainer />
  }
];

const Settings = () => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <TabsWrapper
        tabsProps={{
          name: "settings",
          tabs,
          defaultTab: SETTINGS_TABS.ORGANIZATION
        }}
      />
    </PageContentWrapper>
  </>
);

export default Settings;
