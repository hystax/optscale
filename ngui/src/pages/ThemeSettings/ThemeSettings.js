import React from "react";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import ThemeSettingsComponent from "components/ThemeSettings";

const actionBarDefinition = {
  title: {
    messageId: "themeSettings",
    dataTestId: "lbl_theme_settings"
  }
};

const ThemeSettings = () => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <ThemeSettingsComponent />
    </PageContentWrapper>
  </>
);

export default ThemeSettings;
