import { Box } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { POWER_SCHEDULE_ACTIONS } from "utils/constants";
import { MERIDIEM_NAMES } from "utils/datetime";
import { FIELD_NAMES } from "./constants";
import {
  ExpirationDateField,
  FormButtons,
  InitiationDateField,
  NameField,
  TimeZoneField,
  TriggersFieldArray,
} from "./FormElements";
import { type FormValues } from "./types";

type CreatePowerScheduleFormProps = {
  onSubmit: (formData: FormValues) => void;
  onCancel: () => void;
  isLoadingProps?: {
    isSubmitLoading?: boolean;
  };
};

const CreatePowerScheduleForm = ({ onSubmit, onCancel, isLoadingProps = {} }: CreatePowerScheduleFormProps) => {
  const { isSubmitLoading = false } = isLoadingProps;

  const methods = useForm<FormValues>({
    defaultValues: {
      [FIELD_NAMES.NAME]: "",
      [FIELD_NAMES.TIME_ZONE]: Intl.DateTimeFormat().resolvedOptions().timeZone,
      [FIELD_NAMES.INITIATION_DATE]: undefined,
      [FIELD_NAMES.EXPIRATION_DATE]: undefined,
      [FIELD_NAMES.TRIGGERS_FIELD_ARRAY.FIELD_NAME]: [
        {
          [FIELD_NAMES.TRIGGERS_FIELD_ARRAY.TIME]: "",
          [FIELD_NAMES.TRIGGERS_FIELD_ARRAY.MERIDIEM]: MERIDIEM_NAMES.AM,
          [FIELD_NAMES.TRIGGERS_FIELD_ARRAY.ACTION]: POWER_SCHEDULE_ACTIONS.POWER_ON,
        },
      ],
    },
  });

  const { handleSubmit } = methods;

  return (
    <Box
      sx={{
        width: { md: "50%" },
      }}
    >
      <FormProvider {...methods}>
        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <NameField />
          <TimeZoneField />
          <InitiationDateField />
          <ExpirationDateField />
          <TriggersFieldArray />
          <FormButtons submitButtonMessageId="create" onCancel={onCancel} isLoading={isSubmitLoading} />
        </form>
      </FormProvider>
    </Box>
  );
};

export default CreatePowerScheduleForm;
