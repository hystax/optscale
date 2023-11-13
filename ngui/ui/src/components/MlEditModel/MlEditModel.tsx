import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import TabsWrapper from "components/TabsWrapper";
import MlEditModelFormContainer from "containers/MlEditModelFormContainer";
import MlEditModelParametersContainer from "containers/MlEditModelParametersContainer";
import { ML_MODELS, getMlModelDetailsUrl } from "urls";

const SETTING_TABS = Object.freeze({
  COMMON: "common",
  PARAMETERS: "parameters"
});

const MlEditModel = ({ model, isLoading = false }) => {
  const { id, name } = model;

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={ML_MODELS} component={RouterLink}>
        <FormattedMessage id="models" />
      </Link>,
      <Link key={2} to={getMlModelDetailsUrl(id)} component={RouterLink}>
        {name}
      </Link>
    ],
    title: {
      messageId: "editModelTitle",
      isLoading,
      dataTestId: "lbl_edit_model"
    }
  };

  const tabs = [
    {
      title: SETTING_TABS.COMMON,
      dataTestId: "tab_common",
      node: <MlEditModelFormContainer model={model} />
    },
    {
      title: SETTING_TABS.PARAMETERS,
      dataTestId: "tab_parameters",
      node: <MlEditModelParametersContainer modelParameters={model.goals ?? []} />
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
            name: "edit-model"
          }}
        />
      </PageContentWrapper>
    </>
  );
};

export default MlEditModel;
