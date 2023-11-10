import { Box } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import PoolTypesDescription from "components/PoolTypesDescription";
import PoolsService from "services/PoolsService";
import { PoolFormNameInput, PoolFormLimitInput, PoolFormTypeSelector, PoolFormAutoExtendCheckbox } from "./FormElements";

const CreatePoolForm = ({ parentId, onSuccess, unallocatedLimit }) => {
  const { isLoading: isCreatePoolLoading, createPool } = PoolsService().useCreatePool();

  const methods = useForm();
  const { handleSubmit } = methods;

  const onSubmit = (formValues) => createPool({ ...formValues, parentId }).then(onSuccess);

  return (
    <FormProvider {...methods}>
      <form data-test-id={`form_add_pool`} onSubmit={handleSubmit(onSubmit)} noValidate>
        <PoolFormNameInput />
        <PoolFormLimitInput unallocatedLimit={unallocatedLimit} />
        <PoolFormAutoExtendCheckbox />
        <PoolFormTypeSelector />
        <PoolTypesDescription />
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
