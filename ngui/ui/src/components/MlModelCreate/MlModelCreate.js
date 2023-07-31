import React from "react";
import { Box, Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import MlModelCreateFormContainer from "containers/MlModelCreateFormContainer";
import { ML_MODELS } from "urls";

const actionBarDefinition = {
  breadcrumbs: [
    <Link key={1} to={ML_MODELS} component={RouterLink}>
      <FormattedMessage id="models" />
    </Link>
  ],
  title: {
    messageId: "addModelTitle",
    dataTestId: "lbl_add_model"
  }
};

const MlModelCreate = () => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <Box
        sx={{
          width: { md: "50%" }
        }}
      >
        <MlModelCreateFormContainer />
      </Box>
    </PageContentWrapper>
  </>
);

export default MlModelCreate;
