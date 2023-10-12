import React from "react";
import { Box } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import PoolTypesDescription from "components/PoolTypesDescription";
import QuestionMark from "components/QuestionMark";
import PoolsService from "services/PoolsService";
import {
  PoolFormNameInput,
  PoolFormLimitInput,
  PoolFormTypeSelector,
  PoolFormAutoExtendCheckbox,
  PoolFormOwnerSelector
} from "./FormElements";

const NAME = "name";
const TYPE = "type";

const getInputNameMessage = (inputName) =>
  ({
    [NAME]: "organizationPoolName",
    [TYPE]: "organizationPoolType"
  }[inputName]);

const getReadOnlyProps = (inputName) => ({
  readOnly: true,
  endAdornment: (
    <QuestionMark
      messageId="youCannotEditField"
      messageValues={{
        fieldName: getInputNameMessage(inputName)
      }}
    />
  )
});

const getInputProps = (inputName, isReadOnly) => (isReadOnly ? getReadOnlyProps(inputName) : {});

const EditPoolForm = ({ unallocatedLimit, poolInfo, onSuccess }) => {
  const { id, parent_id: parentPoolId } = poolInfo;
  const { useGetPoolOwners, useUpdatePool } = PoolsService();
  const { isLoading: isUpdatePoolLoading, updatePool } = useUpdatePool();
  const { poolOwners, isDataReady: isPoolOwnersDataReady } = useGetPoolOwners(id);

  const { name: poolName, limit: limitAmount, default_owner_id: defaultResourceOwnerId = "", purpose: type } = poolInfo;

  const methods = useForm({
    defaultValues: {
      name: poolName,
      limit: limitAmount,
      type,
      defaultOwnerId: defaultResourceOwnerId,
      autoExtension: false
    }
  });
  const { handleSubmit } = methods;

  const onSubmit = (formValues) => updatePool({ ...formValues, poolId: id, parentPoolId }).then(onSuccess);

  const isReadOnly = !parentPoolId;

  return (
    <FormProvider {...methods}>
      <form data-test-id={`form_edit_pool`} onSubmit={handleSubmit(onSubmit)} noValidate>
        <PoolFormOwnerSelector isLoading={!isPoolOwnersDataReady} owners={poolOwners} />
        <PoolFormNameInput inputProps={getInputProps(NAME, isReadOnly)} />
        <PoolFormLimitInput unallocatedLimit={unallocatedLimit} isRootPool={isReadOnly} />
        {parentPoolId && <PoolFormAutoExtendCheckbox />}
        <PoolFormTypeSelector inputProps={getInputProps(TYPE, isReadOnly)} />
        {!isReadOnly && <PoolTypesDescription />}
        <FormButtonsWrapper justifyContent="space-between">
          <Box display="flex">
            <ButtonLoader
              variant="contained"
              messageId="save"
              color="primary"
              type="submit"
              isLoading={isUpdatePoolLoading}
              dataTestId="btn_create"
            />
          </Box>
        </FormButtonsWrapper>
      </form>
    </FormProvider>
  );
};

export default EditPoolForm;
