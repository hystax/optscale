import { Box, Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import MlTaskCreateFormContainer from "containers/MlTaskCreateFormContainer";
import { ML_TASKS } from "urls";

const actionBarDefinition = {
  breadcrumbs: [
    <Link key={1} to={ML_TASKS} component={RouterLink}>
      <FormattedMessage id="tasks" />
    </Link>
  ],
  title: {
    messageId: "addTaskTitle",
    dataTestId: "lbl_add_task"
  }
};

const MlTaskCreate = () => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <Box
        sx={{
          width: { md: "50%" }
        }}
      >
        <MlTaskCreateFormContainer />
      </Box>
    </PageContentWrapper>
  </>
);

export default MlTaskCreate;
