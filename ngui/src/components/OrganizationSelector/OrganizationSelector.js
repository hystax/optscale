import React from "react";
import ApartmentIcon from "@mui/icons-material/Apartment";
import ListItemText from "@mui/material/ListItemText";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import Icon from "components/Icon";
import Selector from "components/Selector";
import SelectorLoader from "components/SelectorLoader";
import { ORGANIZATIONS_OVERVIEW } from "urls";
import useStyles from "./OrganizationSelector.styles";

const prepareSelectorData = (organizationId, organizations) => ({
  selected: organizationId,
  items: organizations
    .map((obj, index) => ({
      name: obj.name,
      value: obj.id,
      type: obj.purpose,
      dataTestId: `org_${index}`
    }))
    .sort(({ name: nameA }, { name: nameB }) => nameA.localeCompare(nameB))
});

const renderSelector = ({ organizations = [], organizationId, onChange, navigate, classes }) => {
  const selectorDefinition = prepareSelectorData(organizationId, organizations);

  const organizationOverviewItem = {
    customItem: <ListItemText primary={<FormattedMessage id="organizationsOverview" />} />,
    onClick: () => navigate(ORGANIZATIONS_OVERVIEW),
    key: "organizationsOverview",
    dataTestId: "orgs_dashboard"
  };

  const data = { ...selectorDefinition, items: [...selectorDefinition.items, organizationOverviewItem] };

  return (
    <Selector
      data={data}
      labelId="organization"
      dataTestId="select_org"
      onChange={onChange}
      customClass={classes.organizationSelector}
      isMobile
      menuItemIcon={{
        component: Icon,
        getComponentProps: () => ({
          icon: ApartmentIcon,
          hasRightMargin: true
        })
      }}
    />
  );
};

const OrganizationSelector = ({ organizations = [], organizationId, onChange, isLoading }) => {
  const { classes } = useStyles();

  const navigate = useNavigate();

  return isLoading ? (
    <SelectorLoader customClass={classes.organizationSelector} labelId="organization" />
  ) : (
    renderSelector({ organizations, organizationId, onChange, navigate, classes })
  );
};

// NGUI-2198: selector is always visible and mounted with MainLayoutContainer, organizations and organizationId can be undefined
// TODO - consider mounting those component at different levels
OrganizationSelector.propTypes = {
  organizations: PropTypes.array,
  organizationId: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default OrganizationSelector;
