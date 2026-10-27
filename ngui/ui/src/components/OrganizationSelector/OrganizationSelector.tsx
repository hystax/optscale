import { useState } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import ApartmentIcon from "@mui/icons-material/Apartment";
import ExpandMoreOutlinedIcon from "@mui/icons-material/ExpandMoreOutlined";
import VisibilityOutlinedIcon from "@mui/icons-material/VisibilityOutlined";
import { Box } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import Hidden from "components/Hidden";
import IconButton from "components/IconButton";
import Selector, { Button, Divider, Item, ItemContent } from "components/Selector";
import { CreateOrganizationModal } from "components/SideModalManager/SideModals";
import { ORGANIZATION_SETUP_MODE } from "containers/InitializeContainer/constants";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useIsDownMediaQuery } from "hooks/useMediaQueries";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { ORGANIZATIONS_OVERVIEW } from "urls";
import { getEnvironmentVariable } from "utils/env";
import { getOrganizationDisplayName } from "utils/organization";

const HIDDEN_SELECTOR_SX = { visibility: "hidden", maxWidth: 0, minWidth: 0 };

const MAX_ORGANIZATION_NAME_LENGTH = 24;

const SELECTOR_SX = {
  "&.MuiFormControl-root": {
    /**
     * Empirically selected minWidth to prevent selector width change when
     * switching between organizations with different name lengths
     */
    minWidth: 270,
    "& label": {
      color: (theme) => theme.palette.primary.main,
    },
    "& div": {
      color: (theme) => theme.palette.primary.main,
      "&.Mui-focused": {
        "& fieldset": {
          borderColor: (theme) => theme.palette.primary.main,
        },
      },
    },
    "& svg": {
      color: (theme) => theme.palette.primary.main,
    },
    "& fieldset": {
      borderColor: (theme) => theme.palette.primary.main,
    },
    "&:hover fieldset": {
      borderColor: (theme) => theme.palette.primary.main,
    },
  },
};

type OrganizationSelectorProps = {
  organizations: {
    id: string;
    name: string;
    disabled?: boolean;
  }[];
  organizationId?: string;
  onChange: (value: string) => void;
  isLoading?: boolean;
};

const OrganizationSelector = ({
  organizations,
  organizationId = "",
  onChange,
  isLoading = false,
}: OrganizationSelectorProps) => {
  const { isDemo } = useOrganizationInfo();
  const openSideModal = useOpenSideModal();
  const navigate = useNavigate();

  const isDownSm = useIsDownMediaQuery("sm");

  const [open, setOpen] = useState(false);
  const handleClose = () => setOpen(false);
  const handleOpen = () => setOpen(true);

  const isDeploymentAdmin = useIsAllowed({ requiredActions: ["DEPLOYMENT_ADMIN"] });
  const organizationSetupMode = getEnvironmentVariable("VITE_ON_INITIALIZE_ORGANIZATION_SETUP_MODE");

  const isCreateOrganizationEnabled = organizationSetupMode !== ORGANIZATION_SETUP_MODE.INVITE_ONLY || isDeploymentAdmin;

  return (
    <Box display="flex" alignItems="center">
      <Hidden mode="up" breakpoint="sm">
        <IconButton icon={<ExpandMoreOutlinedIcon />} onClick={handleOpen} />
      </Hidden>
      <Selector
        id="organization-selector"
        labelMessageId="organization"
        value={organizationId}
        onChange={onChange}
        compact
        open={open}
        onOpen={handleOpen}
        onClose={handleClose}
        isLoading={isLoading}
        sx={isDownSm ? HIDDEN_SELECTOR_SX : SELECTOR_SX}
      >
        {[...organizations]
          .sort(({ name: nameA }, { name: nameB }) => nameA.localeCompare(nameB))
          .map((organization) => {
            const { displayName, isNameLong, originalName } = getOrganizationDisplayName({
              name: organization.name,
              isInactive: organization.disabled,
              maxLength: MAX_ORGANIZATION_NAME_LENGTH,
            });

            const tooltip = isNameLong
              ? {
                  title: originalName,
                }
              : undefined;

            return (
              <Item key={organization.id} value={organization.id}>
                <ItemContent
                  icon={{
                    IconComponent: ApartmentIcon,
                  }}
                  tooltip={tooltip}
                >
                  {displayName}
                </ItemContent>
              </Item>
            );
          })}
        <Divider />
        <Button
          icon={{
            IconComponent: VisibilityOutlinedIcon,
          }}
          onClick={() => navigate(ORGANIZATIONS_OVERVIEW)}
          dataTestId="orgs_dashboard"
        >
          <FormattedMessage id="organizationsOverview" />
        </Button>
        {isCreateOrganizationEnabled && (
          <Button
            icon={{
              IconComponent: AddOutlinedIcon,
            }}
            onClick={() => openSideModal(CreateOrganizationModal, { onSuccess: onChange })}
            dataTestId="orgs_create_new"
            disabled={isDemo}
            tooltipTitle={isDemo ? <FormattedMessage id="notAvailableInLiveDemo" /> : null}
          >
            <FormattedMessage id="createNewOrganization" />
          </Button>
        )}
      </Selector>
    </Box>
  );
};

// NGUI-2198: selector is always visible and mounted with CoreDataContainer, organizations and organizationId can be undefined
// TODO - consider mounting those component at different levels

export default OrganizationSelector;
