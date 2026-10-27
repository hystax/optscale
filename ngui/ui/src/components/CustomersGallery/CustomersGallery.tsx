import { Box, Grid, Stack } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import bluebill from "assets/customers/bluebill.svg";
import dexory from "assets/customers/dexory.svg";
import luminance from "assets/customers/luminance.svg";
import nekoHealth from "assets/customers/neko-health.svg";
import nubephant from "assets/customers/nubephant.svg";
import osapiens from "assets/customers/osapiens.svg";
import physicsX from "assets/customers/physics-x.svg";
import secureData from "assets/customers/securedata.svg";
import softwareOne from "assets/customers/softwareone.svg";
import taktile from "assets/customers/taktile.svg";
import veesion from "assets/customers/veesion.svg";
import viadex from "assets/customers/viadex.svg";
import SubTitle from "components/SubTitle";
import { SPACING_1 } from "utils/layouts";

const logos = [
  {
    src: viadex,
    altMessageId: "viadex",
  },
  {
    src: bluebill,
    altMessageId: "bluebill",
  },
  {
    src: dexory,
    altMessageId: "dexory",
  },
  {
    src: luminance,
    altMessageId: "luminance",
  },
  {
    src: nekoHealth,
    altMessageId: "nekoHealth",
  },
  {
    src: nubephant,
    altMessageId: "nubephant",
  },
  {
    src: osapiens,
    altMessageId: "osapiens",
  },
  {
    src: secureData,
    altMessageId: "secureData",
  },
  {
    src: softwareOne,
    altMessageId: "softwareOne",
  },
  {
    src: taktile,
    altMessageId: "taktile",
  },
  {
    src: veesion,
    altMessageId: "veesion",
  },
  {
    src: physicsX,
    altMessageId: "physicsX",
  },
];

const CustomersGallery = () => {
  const intl = useIntl();

  return (
    <Stack data-test-id="div_meet_customer" spacing={SPACING_1}>
      <SubTitle>
        <FormattedMessage id="trustedBy" />
      </SubTitle>
      <Grid container columnSpacing={SPACING_1} rowSpacing={SPACING_1}>
        {logos.map((item) => (
          <Grid item key={item.altMessageId} xs={4} sm={3} md={3} lg={2}>
            <Box height={40} width="100%">
              <Box
                component="img"
                src={item.src}
                alt={intl.formatMessage({ id: item.altMessageId })}
                width="100%"
                height="100%"
                sx={{ objectFit: "contain", opacity: 0.55 }}
              />
            </Box>
          </Grid>
        ))}
      </Grid>
    </Stack>
  );
};

export default CustomersGallery;
