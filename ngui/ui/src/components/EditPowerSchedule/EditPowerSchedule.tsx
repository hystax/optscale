import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import { EditPowerScheduleForm, type FormValues } from "components/PowerScheduleForm";
import { type PowerScheduleResponse } from "services/PowerScheduleService";
import { POWER_SCHEDULES, getPowerScheduleDetailsUrl } from "urls";

type EditPowerScheduleProps = {
  powerSchedule: PowerScheduleResponse;
  onSubmit: (formData: FormValues) => void;
  onCancel: () => void;
  isLoadingProps?: {
    isSubmitLoading?: boolean;
    isGetDataLoading?: boolean;
  };
};

const EditPowerSchedule = ({ powerSchedule, onSubmit, onCancel, isLoadingProps = {} }: EditPowerScheduleProps) => {
  const { isGetDataLoading = false, isSubmitLoading = false } = isLoadingProps;

  return (
    <>
      <ActionBar
        data={{
          breadcrumbs: [
            <Link key={1} to={POWER_SCHEDULES} component={RouterLink}>
              <FormattedMessage id="powerSchedulesTitle" />
            </Link>,
            <Link key={2} to={getPowerScheduleDetailsUrl(powerSchedule.id)} component={RouterLink}>
              {powerSchedule.name}
            </Link>
          ],
          title: {
            isLoading: isGetDataLoading,
            messageId: "edit",
            dataTestId: "lbl_create_power_schedule_title"
          }
        }}
      />
      <PageContentWrapper>
        <EditPowerScheduleForm
          powerSchedule={powerSchedule}
          onSubmit={onSubmit}
          onCancel={onCancel}
          isLoadingProps={{
            isGetDataLoading,
            isSubmitLoading
          }}
        />
      </PageContentWrapper>
    </>
  );
};

export default EditPowerSchedule;
