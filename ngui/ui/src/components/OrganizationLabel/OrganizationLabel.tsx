import { forwardRef } from "react";
import ApartmentIcon from "@mui/icons-material/Apartment";
import Link from "@mui/material/Link";
import Icon from "components/Icon";
import Tooltip from "components/Tooltip";
import { useUpdateScope } from "hooks/useUpdateScope";
import { HOME } from "urls";
import { getOrganizationDisplayName } from "utils/organization";

const MAX_ORGANIZATION_NAME_LENGTH = 32;

type OrganizationLabelProps = {
  id: string;
  name: string;
  dataTestId?: string;
  disableLink?: boolean;
  isInactive?: boolean;
};

type LabelLinkProps = {
  organizationId: string;
  organizationName: string;
  dataTestId?: string;
};

const LabelLink = forwardRef<HTMLButtonElement, LabelLinkProps>(
  ({ organizationId, organizationName, dataTestId, ...rest }, ref) => {
    const updateScope = useUpdateScope();

    const link = (
      <Link
        ref={ref}
        data-test-id={dataTestId}
        color="primary"
        component="button"
        onClick={() =>
          updateScope({
            newScopeId: organizationId,
            redirectTo: HOME,
          })
        }
        {...rest}
      >
        {organizationName}
      </Link>
    );

    return link;
  }
);

const OrganizationLabel = ({ id, name, dataTestId, disableLink = false, isInactive = false }: OrganizationLabelProps) => {
  const { displayName, isNameLong, originalName } = getOrganizationDisplayName({
    name,
    isInactive,
    maxLength: MAX_ORGANIZATION_NAME_LENGTH,
  });

  return (
    <>
      <Icon icon={ApartmentIcon} hasRightMargin />
      <Tooltip title={isNameLong ? originalName : undefined} placement="top">
        {!disableLink ? (
          <LabelLink organizationId={id} organizationName={displayName} dataTestId={dataTestId} />
        ) : (
          <span data-test-id={dataTestId}>{displayName}</span>
        )}
      </Tooltip>
    </>
  );
};

export default OrganizationLabel;
