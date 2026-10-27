import { useEffect } from "react";
import { Box } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { type PowerScheduleResponse } from "services/PowerScheduleService";
import {
  EN_TIME_FORMAT,
  EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM,
  formatTimeString,
  moveDateToUTC,
  parse,
  secondsToMilliseconds,
} from "utils/datetime";
import { FIELD_NAMES } from "./constants";
import {
  ExpirationDateField,
  FormButtons,
  InitiationDateField,
  NameField,
  TimeZoneField,
  TriggersFieldArray,
} from "./FormElements";
import { Meridiem, type FormValues } from "./types";

type EditPowerScheduleFormProps = {
  powerSchedule: Partial<PowerScheduleResponse>;
  onSubmit: (formData: FormValues) => void;
  onCancel: () => void;
  isLoadingProps?: {
    isSubmitLoading?: boolean;
    isGetDataLoading?: boolean;
  };
};

const getDefaultFormValues = (powerSchedule: EditPowerScheduleFormProps["powerSchedule"]): FormValues => ({
  [FIELD_NAMES.NAME]: powerSchedule.name ?? "",
  [FIELD_NAMES.TIME_ZONE]: powerSchedule.timezone ?? "",
  [FIELD_NAMES.INITIATION_DATE]: powerSchedule.start_date
    ? new Date(moveDateToUTC(secondsToMilliseconds(powerSchedule.start_date)))
    : undefined,
  [FIELD_NAMES.EXPIRATION_DATE]: powerSchedule.end_date
    ? new Date(moveDateToUTC(secondsToMilliseconds(powerSchedule.end_date)))
    : undefined,
  [FIELD_NAMES.TRIGGERS_FIELD_ARRAY.FIELD_NAME]:
    powerSchedule.triggers
      ?.toSorted((triggerA, triggerB) => {
        const timeA = parse(triggerA.time, EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM, new Date());
        const timeB = parse(triggerB.time, EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM, new Date());

        return timeA.getTime() - timeB.getTime();
      })
      .map((trigger) => {
        const [time, meridiem] = formatTimeString({
          timeString: trigger.time,
          timeStringFormat: EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM,
          parsedTimeStringFormat: EN_TIME_FORMAT,
        }).split(" ");

        return {
          [FIELD_NAMES.TRIGGERS_FIELD_ARRAY.TIME]: time,
          [FIELD_NAMES.TRIGGERS_FIELD_ARRAY.MERIDIEM]: meridiem as Meridiem,
          [FIELD_NAMES.TRIGGERS_FIELD_ARRAY.ACTION]: trigger.action,
        };
      }) ?? [],
});

const EditPowerScheduleForm = ({ powerSchedule, onSubmit, onCancel, isLoadingProps = {} }: EditPowerScheduleFormProps) => {
  const { isSubmitLoading = false, isGetDataLoading = false } = isLoadingProps;

  const methods = useForm<FormValues>({
    defaultValues: getDefaultFormValues(powerSchedule),
  });

  const { handleSubmit, reset } = methods;

  useEffect(() => {
    reset((formValues) => ({
      ...formValues,
      ...getDefaultFormValues(powerSchedule),
    }));
  }, [powerSchedule, reset]);

  return (
    <Box
      sx={{
        width: { md: "50%" },
      }}
    >
      <FormProvider {...methods}>
        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <NameField isLoading={isGetDataLoading} />
          <TimeZoneField isLoading={isGetDataLoading} />
          <InitiationDateField isLoading={isGetDataLoading} />
          <ExpirationDateField isLoading={isGetDataLoading} />
          <TriggersFieldArray isLoading={isGetDataLoading} />
          <FormButtons submitButtonMessageId="edit" onCancel={onCancel} isLoading={isSubmitLoading || isGetDataLoading} />
        </form>
      </FormProvider>
    </Box>
  );
};

export default EditPowerScheduleForm;
