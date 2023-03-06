import React from "react";
import PropTypes from "prop-types";
import { useIntl } from "react-intl";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import TabsWrapper from "components/TabsWrapper";
import MlEditApplicationFormContainer from "containers/MlEditApplicationFormContainer";
import MlEditApplicationParametersContainer from "containers/MlEditApplicationParametersContainer";

const SETTING_TABS = Object.freeze({
  COMMON: "common",
  PARAMETERS: "parameters"
});

const MlEditApplication = ({ application, isLoading = false }) => {
  const intl = useIntl();

  const { name } = application;

  const actionBarDefinition = {
    title: {
      text: intl.formatMessage({ id: "edit{}" }, { value: name }),
      isLoading,
      dataTestId: "lbl_edit_application"
    }
  };

  const tabs = [
    {
      title: SETTING_TABS.COMMON,
      dataTestId: "tab_common",
      node: <MlEditApplicationFormContainer application={application} />
    },
    {
      title: SETTING_TABS.PARAMETERS,
      dataTestId: "tab_parameters",
      node: <MlEditApplicationParametersContainer applicationParameters={application.goals ?? []} />
    }
  ];

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <TabsWrapper
          isLoading={isLoading}
          tabsProps={{
            tabs,
            defaultTab: SETTING_TABS.COMMON,
            name: "edit-application"
          }}
        />
      </PageContentWrapper>
    </>
  );
};

MlEditApplication.propTypes = {
  application: PropTypes.object.isRequired,
  isLoading: PropTypes.bool
};

export default MlEditApplication;
