import { Box } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import PoolsService from "services/PoolsService";
import { NameField, LimitField, TypeSelector, AutoExtendCheckbox } from "./FormElements";
import { CreatePoolFormValues } from "./types";
import { getCreateFormDefaultValues } from "./utils";

const CreatePoolForm = ({ parentId, onSuccess, unallocatedLimit }) => {
  const { isLoading: isCreatePoolLoading, createPool } = PoolsService().useCreatePool();

  const methods = useForm<CreatePoolFormValues>({
    defaultValues: getCreateFormDefaultValues()
  });

  const { handleSubmit } = methods;

  const onSubmit = handleSubmit((formValues) => createPool({ ...formValues, parentId }).then(onSuccess));

  return (
    <FormProvider {...methods}>
      <form data-test-id="form_add_pool" onSubmit={onSubmit} noValidate>
        <NameField />
        <LimitField unallocatedLimit={unallocatedLimit} />
        <AutoExtendCheckbox />
        <TypeSelector />
        <FormButtonsWrapper justifyContent="space-between">
          <Box display="flex">
            <ButtonLoader
              variant="contained"
              messageId="create"
              color="primary"
              type="submit"
              isLoading={isCreatePoolLoading}
              dataTestId="btn_create"
            />
          </Box>
        </FormButtonsWrapper>
      </form>
    </FormProvider>
  );
};

export default CreatePoolForm;
