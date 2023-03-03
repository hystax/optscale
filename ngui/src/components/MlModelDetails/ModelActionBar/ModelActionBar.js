import React from "react";
import SettingsIcon from "@mui/icons-material/Settings";
import PropTypes from "prop-types";
import { useIntl } from "react-intl";
import ActionBar from "components/ActionBar";
import { getEditMlUrl } from "urls";

const ModelActionBar = ({ isLoading, name, applicationId }) => {
  const intl = useIntl();

  const baseActionBarItems = [
    {
      key: "edit",
      icon: <SettingsIcon fontSize="small" />,
      messageId: "configure",
      link: getEditMlUrl(applicationId),
      type: "button",
      isLoading,
      requiredActions: ["EDIT_PARTNER"],
      dataTestId: "btn_edit"
    }
  ];

  const actionBarDefinition = {
    title: {
      /**
       * TODO ML
       * - How can it be that the model doesn't have a name?
       * - Rename MlModel to Application?
       */
      text: name || intl.formatMessage({ id: "untitledMlModelTitle" }),
      isLoading,
      dataTestId: "lbl_pool_name"
    },
    items: baseActionBarItems
  };

  return <ActionBar data={actionBarDefinition} />;
};

ModelActionBar.propTypes = {
  isLoading: PropTypes.bool,
  name: PropTypes.string,
  applicationId: PropTypes.string
};

export default ModelActionBar;
