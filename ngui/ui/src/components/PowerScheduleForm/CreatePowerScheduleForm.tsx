import { Box } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { MERIDIEM_NAMES } from "utils/datetime";
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
      [FIELD_NAMES.POWER_ON.FIELD]: {
        [FIELD_NAMES.POWER_ON.TIME]: "",
        [FIELD_NAMES.POWER_ON.TIME_OF_DAY]: MERIDIEM_NAMES.AM
      },
      [FIELD_NAMES.POWER_OFF.FIELD]: {
        [FIELD_NAMES.POWER_OFF.TIME]: "",
        [FIELD_NAMES.POWER_OFF.TIME_OF_DAY]: MERIDIEM_NAMES.AM
      },
      [FIELD_NAMES.TIME_ZONE]: Intl.DateTimeFormat().resolvedOptions().timeZone,
      [FIELD_NAMES.INITIATION_DATE]: undefined,
      [FIELD_NAMES.EXPIRATION_DATE]: undefined
    }
  });

  const { handleSubmit } = methods;

  return (
    <Box
      sx={{
        width: { md: "50%" }
      }}
    >
      <FormProvider {...methods}>
        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <NameField />
          <PowerOnField />
          <PowerOffField />
          <TimeZoneField />
          <InitiationDateField />
          <ExpirationDateField />
          <FormButtons submitButtonMessageId="create" onCancel={onCancel} isLoading={isSubmitLoading} />
        </form>
      </FormProvider>
    </Box>
  );
};

export default CreatePowerScheduleForm;
