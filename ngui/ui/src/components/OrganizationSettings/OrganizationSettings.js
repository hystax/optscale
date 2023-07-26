import React from "react";
import Box from "@mui/material/Box";
import DeleteOrganization from "components/DeleteOrganization";
import OrganizationInfoSetting from "components/OrganizationInfoSetting";
import { useIsAllowed } from "hooks/useAllowedActions";

const OrganizationSettings = () => {
  const isDeleteOrganizationAllowed = useIsAllowed({ requiredActions: ["DELETE_PARTNER"] });

  return (
    <>
      <Box mb={isDeleteOrganizationAllowed ? 2 : 0}>
        <OrganizationInfoSetting />
      </Box>
      {isDeleteOrganizationAllowed && <DeleteOrganization />}
    </>
  );
};

export default OrganizationSettings;
