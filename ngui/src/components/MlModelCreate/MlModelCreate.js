import React from "react";
import { Box } from "@mui/material";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import MlModelCreateFormContainer from "containers/MlModelCreateFormContainer";

const actionBarDefinition = {
  title: {
    messageId: "addApplicationTitle",
    dataTestId: "lbl_add_application"
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
