import React, { useEffect } from "react";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";
import { useForm, FormProvider } from "react-hook-form";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import DeletePool from "components/DeletePool";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import PoolTypesDescription from "components/PoolTypesDescription";
import QuestionMark from "components/QuestionMark";
import {
  PoolFormOwnerSelector,
  PoolFormNameInput,
  PoolFormLimitInput,
  PoolFormTypeSelector,
  PoolFormAutoExtendCheckbox
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

const PoolForm = ({
  defaultValues,
  onSubmit,
  onCancel,
  isLoadingProps = {},
  owners,
  parentPoolId,
  poolId,
  hasSubPools = false
}) => {
  const {
    isCreateLoading = false,
    isPoolOwnersLoading = false,
    isGetPoolLoading = false,
    isEditLoading = false
  } = isLoadingProps;

  const methods = useForm({ defaultValues });
  const { handleSubmit, reset } = methods;

  const isEdit = !!poolId;
  const isReadOnly = isEdit && !parentPoolId;

  useEffect(() => {
    if (isEdit) {
      reset(defaultValues);
    }
  }, [defaultValues, isEdit, reset]);

  return (
    <FormProvider {...methods}>
      <form data-test-id={`form_${isEdit ? "edit" : "add"}_pool`} onSubmit={handleSubmit(onSubmit)} noValidate>
        {isEdit && <PoolFormOwnerSelector isLoading={isPoolOwnersLoading} owners={owners} />}
        <PoolFormNameInput inputProps={getInputProps(NAME, isReadOnly)} isLoading={isGetPoolLoading} />
        <PoolFormLimitInput isLoading={isGetPoolLoading} />
        {parentPoolId && <PoolFormAutoExtendCheckbox isLoading={isGetPoolLoading} />}
        <PoolFormTypeSelector isLoading={isGetPoolLoading} inputProps={getInputProps(TYPE, isReadOnly)} />
        <PoolTypesDescription />
        <FormButtonsWrapper justifyContent="space-between">
          <Box display="flex">
            <ButtonLoader
              variant="contained"
              messageId={isEdit ? "save" : "create"}
              color="primary"
              type="submit"
              isLoading={isCreateLoading || isEditLoading}
              dataTestId="btn_create"
            />
            <Button dataTestId="btn_cancel" messageId="cancel" onClick={onCancel} />
          </Box>
          {isEdit && parentPoolId && !hasSubPools ? <DeletePool poolId={poolId} /> : null}
        </FormButtonsWrapper>
      </form>
    </FormProvider>
  );
};

export const FormPropTypes = {
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  owners: PropTypes.array,
  poolId: PropTypes.string,
  parentPoolId: PropTypes.string,
  hasSubPools: PropTypes.bool,
  defaultValues: PropTypes.shape({
    name: PropTypes.string,
    limit: PropTypes.number,
    type: PropTypes.string,
    defaultOwnerId: PropTypes.string
  }),
  isLoadingProps: PropTypes.shape({
    isEditLoading: PropTypes.bool,
    isGetParentPoolLoading: PropTypes.bool,
    isGetPoolLoading: PropTypes.bool,
    isCreateLoading: PropTypes.bool,
    isPoolOwnersLoading: PropTypes.bool
  })
};

PoolForm.propTypes = FormPropTypes;

export default PoolForm;
