import { useEffect } from "react";
import { Box } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { type PowerScheduleResponse } from "services/PowerScheduleService";
import { MERIDIEM_NAMES, formatTimeString, moveDateToUTC, secondsToMilliseconds } from "utils/datetime";
import { FIELD_NAMES } from "./constants";
import {
  ExpirationDateField,
  FormButtons,
  InitiationDateField,
  NameField,
  PowerOnField,
  PowerOffField,
  TimeZoneField
} from "./FormElements";
import { type FormValues } from "./types";

type EditPowerScheduleFormProps = {
  powerSchedule: PowerScheduleResponse;
  onSubmit: (formData: FormValues) => void;
  onCancel: () => void;
  isLoadingProps?: {
    isSubmitLoading?: boolean;
    isGetDataLoading?: boolean;
  };
};

const getPowerSwitchTimeFormValues = (powerSwitchTime: string) =>
  formatTimeString({
    timeString: powerSwitchTime,
    timeStringFormat: "HH:mm",
    parsedTimeStringFormat: "hh:mm a"
  }).split(" ") as [string, "AM" | "PM"];

const getDefaultFormValues = (powerSchedule: EditPowerScheduleFormProps["powerSchedule"]): FormValues => {
  const [powerOnTime, powerOnTimeOfDay] = powerSchedule.power_on
    ? getPowerSwitchTimeFormValues(powerSchedule.power_on)
    : ["", MERIDIEM_NAMES.AM];
  const [powerOffTime, powerOffTimeOfDay] = powerSchedule.power_off
    ? getPowerSwitchTimeFormValues(powerSchedule.power_off)
    : ["", MERIDIEM_NAMES.AM];

  return {
    [FIELD_NAMES.NAME]: powerSchedule.name ?? "",
    [FIELD_NAMES.POWER_ON.FIELD]: {
      [FIELD_NAMES.POWER_ON.TIME]: powerOnTime,
      [FIELD_NAMES.POWER_ON.TIME_OF_DAY]: powerOnTimeOfDay
    },
    [FIELD_NAMES.POWER_OFF.FIELD]: {
      [FIELD_NAMES.POWER_OFF.TIME]: powerOffTime,
      [FIELD_NAMES.POWER_OFF.TIME_OF_DAY]: powerOffTimeOfDay
    },
    [FIELD_NAMES.TIME_ZONE]: powerSchedule.timezone ?? "",
    [FIELD_NAMES.INITIATION_DATE]: powerSchedule.start_date
      ? new Date(moveDateToUTC(secondsToMilliseconds(powerSchedule.start_date)))
      : undefined,
    [FIELD_NAMES.EXPIRATION_DATE]: powerSchedule.end_date
      ? new Date(moveDateToUTC(secondsToMilliseconds(powerSchedule.end_date)))
      : undefined
  };
};

const EditPowerScheduleForm = ({ powerSchedule, onSubmit, onCancel, isLoadingProps = {} }: EditPowerScheduleFormProps) => {
  const { isSubmitLoading = false, isGetDataLoading = false } = isLoadingProps;

  const methods = useForm<FormValues>({
    defaultValues: getDefaultFormValues(powerSchedule)
  });

  const { handleSubmit, reset } = methods;

  useEffect(() => {
    reset((formValues) => ({
      ...formValues,
      ...getDefaultFormValues(powerSchedule)
    }));
  }, [powerSchedule, reset]);

  return (
    <Box
      sx={{
        width: { md: "50%" }
      }}
    >
      <FormProvider {...methods}>
        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <NameField isLoading={isGetDataLoading} />
          <PowerOnField isLoading={isGetDataLoading} />
          <PowerOffField isLoading={isGetDataLoading} />
          <TimeZoneField isLoading={isGetDataLoading} />
          <InitiationDateField isLoading={isGetDataLoading} />
          <ExpirationDateField isLoading={isGetDataLoading} />
          <FormButtons submitButtonMessageId="edit" onCancel={onCancel} isLoading={isSubmitLoading || isGetDataLoading} />
        </form>
      </FormProvider>
    </Box>
  );
};

export default EditPowerScheduleForm;
