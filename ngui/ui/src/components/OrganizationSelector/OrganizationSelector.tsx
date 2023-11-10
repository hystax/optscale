import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import ApartmentIcon from "@mui/icons-material/Apartment";
import VisibilityOutlinedIcon from "@mui/icons-material/VisibilityOutlined";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import Icon from "components/Icon";
import SelectorComponent from "components/Selector";
import SelectorLoader from "components/SelectorLoader";
import { CreateOrganizationModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { ORGANIZATIONS_OVERVIEW } from "urls";
import useStyles from "./OrganizationSelector.styles";

const prepareSelectorData = (organizationId, organizations) => ({
  selected: organizationId,
  items: organizations
    .map((obj, index) => ({
      name: obj.name,
      value: obj.id,
      dataTestId: `org_${index}`
    }))
    .sort(({ name: nameA }, { name: nameB }) => nameA.localeCompare(nameB))
});

const Selector = ({ organizations = [], organizationId, onChange }) => {
  const { isDemo } = useOrganizationInfo();
  const openSideModal = useOpenSideModal();
  const navigate = useNavigate();
  const { classes } = useStyles();

  const selectorDefinition = prepareSelectorData(organizationId, organizations);

  const organizationOverviewItem = {
    key: "organizationsOverview",
    render: ({ button }) =>
      button({
        children: (
          <>
            <Icon color="inherit" hasRightMargin icon={VisibilityOutlinedIcon} />
            <FormattedMessage id="organizationsOverview" />
          </>
        ),
        onClick: () => navigate(ORGANIZATIONS_OVERVIEW),
        dataTestId: "orgs_dashboard"
      })
  };

  const createOrganizationItem = {
    key: "creteOrganization",
    render: ({ button }) =>
      button({
        children: (
          <>
            <Icon color="inherit" hasRightMargin icon={AddOutlinedIcon} />
            <FormattedMessage id="createNewOrganization" />
          </>
        ),
        onClick: () => openSideModal(CreateOrganizationModal, { onSuccess: onChange }),
        dataTestId: "orgs_create_new",
        disabled: isDemo,
        tooltip: {
          content: <FormattedMessage id="notAvailableInLiveDemo" />,
          show: isDemo
        }
      })
  };

  const data = {
    ...selectorDefinition,
    items: [
      ...selectorDefinition.items,
      {
        key: "divider",
        render: ({ divider }) => divider()
      },
      organizationOverviewItem,
      createOrganizationItem
    ]
  };

  return (
    <SelectorComponent
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

  return isLoading ? (
    <SelectorLoader customClass={classes.organizationSelector} labelId="organization" />
  ) : (
    <Selector organizations={organizations} organizationId={organizationId} onChange={onChange} />
  );
};

// NGUI-2198: selector is always visible and mounted with MainLayoutContainer, organizations and organizationId can be undefined
// TODO - consider mounting those component at different levels

export default OrganizationSelector;
