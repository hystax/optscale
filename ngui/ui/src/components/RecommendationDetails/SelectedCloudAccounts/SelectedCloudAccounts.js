import React from "react";
import { Box } from "@mui/material";
import { GET_DATA_SOURCES } from "api/restapi/actionTypes";
import CloudLabel from "components/CloudLabel";
import { useApiData } from "hooks/useApiData";
import { SPACING_1 } from "utils/layouts";

const SelectedCloudAccounts = ({ cloudAccountIds }) => {
  const {
    apiData: { cloudAccounts = [] }
  } = useApiData(GET_DATA_SOURCES);

  return (
    <Box display="flex" flexWrap="wrap" gap={SPACING_1}>
      {cloudAccounts
        .map(({ name, id, type: cloudType }) => {
          if (cloudAccountIds.indexOf(id) > -1) {
            return <CloudLabel key={id} name={name} type={cloudType} disableLink />;
          }

          return false;
        })
        .filter(Boolean)}
    </Box>
  );
};

export default SelectedCloudAccounts;
