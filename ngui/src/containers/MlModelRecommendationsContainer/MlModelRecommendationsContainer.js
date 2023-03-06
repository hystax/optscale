import React from "react";
import AccessTimeOutlinedIcon from "@mui/icons-material/AccessTimeOutlined";
import { Box, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { useParams } from "react-router-dom";
import ContentBackdrop from "components/ContentBackdrop";
import MlModelRecommendations from "components/MlModelRecommendations";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlApplicationsService from "services/MlApplicationsService";

const MlModelRecommendationsContainer = () => {
  const { isDemo } = useOrganizationInfo();

  const { useGetModelRecommendation } = MlApplicationsService();

  const { modelId } = useParams();

  const { isLoading, data: recommendations } = useGetModelRecommendation(modelId);

  const mlModelRecommendations = <MlModelRecommendations isLoading={isLoading} recommendations={recommendations} />;

  return (
    <Box position="relative">
      {isDemo ? (
        mlModelRecommendations
      ) : (
        <ContentBackdrop
          bannerMaxWidth="300px"
          bannerContent={
            <Typography paragraph variant="body1" fontWeight="bold">
              <FormattedMessage id="comingSoon" />
            </Typography>
          }
          icon={{ Component: ({ className }) => <AccessTimeOutlinedIcon color="primary" className={className} /> }}
        >
          {mlModelRecommendations}
        </ContentBackdrop>
      )}
    </Box>
  );
};

export default MlModelRecommendationsContainer;
