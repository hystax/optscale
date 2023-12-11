import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import CreatePowerScheduleFormContainer from "containers/CreatePowerScheduleFormContainer";
import { POWER_SCHEDULES } from "urls";

const actionBarDefinition = {
  breadcrumbs: [
    <Link key={1} to={POWER_SCHEDULES} component={RouterLink}>
      <FormattedMessage id="powerSchedulesTitle" />
    </Link>
  ],
  title: {
    messageId: "createPowerScheduleTitle",
    dataTestId: "lbl_create_power_schedule_title"
  }
};

const CreatePowerSchedule = () => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <CreatePowerScheduleFormContainer />
    </PageContentWrapper>
  </>
);

export default CreatePowerSchedule;
