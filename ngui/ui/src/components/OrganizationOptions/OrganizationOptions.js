import React, { useState } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import { CircularProgress } from "@mui/material";
import Box from "@mui/material/Box";
import FormHelperText from "@mui/material/FormHelperText";
import Grid from "@mui/material/Grid";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Accordion from "components/Accordion";
import ActionBar from "components/ActionBar";
import ButtonLoader from "components/ButtonLoader";
import DeleteOrganizationOption from "components/DeleteOrganizationOption";
import JsonView from "components/JsonView";
import PageContentWrapper from "components/PageContentWrapper";
import PanelLoader from "components/PanelLoader";
import { CreateOrganizationOptionModal } from "components/SideModalManager/SideModals";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { SPACING_4 } from "utils/layouts";

const OrganizationOptions = ({
  expandedOption,
  requestedOption,
  value,
  handleExpand,
  options,
  onSave,
  isLoadingProps = {}
}) => {
  const {
    isGetOrganizationOptionsLoading = false,
    isGetOrganizationOptionLoading = false,
    isUpdateOrganizationOptionLoading = false
  } = isLoadingProps;

  const [updatedValue, setUpdatedValue] = useState(value);
  const [isValidJson, setIsValidJson] = useState(true);

  const openSideModal = useOpenSideModal();

  const onJsonChange = ({ error, jsObject }) => {
    setUpdatedValue(jsObject);
    setIsValidJson(error === false);
  };

  const save = (option) => {
    if (isValidJson) {
      return onSave(option, updatedValue);
    }
    return setIsValidJson(false);
  };

  const onExpand = (optionName) => {
    handleExpand(optionName);
    setIsValidJson(true);
  };

  const actionBarDefinition = {
    title: {
      messageId: "organizationOptions",
      dataTestId: "lbl_organization_options"
    },
    items: [
      {
        key: "add",
        icon: <AddOutlinedIcon fontSize="small" />,
        messageId: "add",
        color: "success",
        variant: "contained",
        action: () => openSideModal(CreateOrganizationOptionModal),
        type: "button",
        requiredActions: ["EDIT_PARTNER"],
        dataTestId: "btn_add_organization_option"
      }
    ]
  };

  const isChangeSettingsAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Grid container>
          <Grid item xs={12}>
            {isGetOrganizationOptionsLoading ? (
              <PanelLoader />
            ) : (
              options.map((option) => (
                <Accordion
                  key={option}
                  actions={
                    isChangeSettingsAllowed ? (
                      <>
                        <ButtonLoader
                          messageId="save"
                          color="primary"
                          variant="outlined"
                          dataTestId="btn_save"
                          onClick={() => save(option)}
                          isLoading={isUpdateOrganizationOptionLoading}
                        />
                        <DeleteOrganizationOption name={option} />
                      </>
                    ) : null
                  }
                  expanded={expandedOption === option}
                  onChange={() => onExpand(option)}
                  disableExpandedSpacing
                >
                  <ListItem>
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center">
                          {option}
                          {isGetOrganizationOptionLoading && option === requestedOption && (
                            <CircularProgress size={20} style={{ marginLeft: SPACING_4 }} />
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                  <JsonView id={option} value={value} onChange={onJsonChange} viewOnly={!isChangeSettingsAllowed} />
                  {!isValidJson && (
                    <FormHelperText variant="outlined" error>
                      <FormattedMessage id="optionMustBeValidJsonObject" />
                    </FormHelperText>
                  )}
                </Accordion>
              ))
            )}
          </Grid>
        </Grid>
      </PageContentWrapper>
    </>
  );
};

OrganizationOptions.propTypes = {
  requestedOption: PropTypes.string,
  expandedOption: PropTypes.string,
  value: PropTypes.object.isRequired,
  handleExpand: PropTypes.func.isRequired,
  options: PropTypes.array.isRequired,
  onSave: PropTypes.func.isRequired,
  isLoadingProps: PropTypes.shape({
    isGetOrganizationOptionsLoading: PropTypes.bool,
    isGetOrganizationOptionLoading: PropTypes.bool,
    isUpdateOrganizationOptionLoading: PropTypes.bool
  })
};

export default OrganizationOptions;
