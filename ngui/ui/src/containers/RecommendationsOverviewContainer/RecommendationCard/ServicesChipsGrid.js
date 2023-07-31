import React from "react";
import { Box } from "@mui/system";
import { useIntl } from "react-intl";
import Chip from "components/Chip";
import CloudLabel from "components/CloudLabel";
import { useRecommendationServices } from "hooks/useRecommendationServices";

const ServiceChip = ({ name, type }) => {
  const intl = useIntl();
  return (
    <Chip
      label={<CloudLabel name={intl.formatMessage({ id: name })} type={type} disableLink />}
      color="info"
      size="small"
      variant="outlined"
    />
  );
};

const ServicesChipsGrid = ({ services }) => {
  const recommendationServices = useRecommendationServices();

  return (
    <Box display="flex" flexWrap="wrap" gap={1}>
      {services
        .filter((service) => !!recommendationServices[service])
        .sort()
        .map((service) => (
          <ServiceChip key={service} {...recommendationServices[service]} />
        ))}
    </Box>
  );
};

export default ServicesChipsGrid;
