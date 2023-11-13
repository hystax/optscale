import { Box } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import PoolTypesDescription from "components/PoolTypesDescription";
import QuestionMark from "components/QuestionMark";
import { useIsAllowed } from "hooks/useAllowedActions";
import PoolsService from "services/PoolsService";
import { SCOPE_TYPES } from "utils/constants";
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
  })[inputName];

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

const getInputProps = (inputName, isOrganizationPool, isReadOnly) => {
  if (isOrganizationPool) {
    return getReadOnlyProps(inputName);
  }
  if (isReadOnly) {
    return { readOnly: true };
  }
  return {};
};

const EditPoolForm = ({ unallocatedLimit, poolInfo, onSuccess }) => {
  const { id, parent_id: parentPoolId } = poolInfo;
  const { useGetPoolOwners, useUpdatePool } = PoolsService();
  const { isLoading: isUpdatePoolLoading, updatePool } = useUpdatePool();
  const { poolOwners, isDataReady: isPoolOwnersDataReady } = useGetPoolOwners(id);

  const {
    name: poolName,
    id: poolId,
    limit: limitAmount,
    default_owner_id: defaultResourceOwnerId = "",
    purpose: type
  } = poolInfo;

  const isReadOnly = !useIsAllowed({ entityType: SCOPE_TYPES.POOL, entityId: poolId, requiredActions: ["MANAGE_POOLS"] });

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

  const isOrganizationPool = !parentPoolId;

  return (
    <FormProvider {...methods}>
      <form data-test-id={`form_edit_pool`} onSubmit={handleSubmit(onSubmit)} noValidate>
        <PoolFormOwnerSelector isLoading={!isPoolOwnersDataReady} owners={poolOwners} isReadOnly={isReadOnly} />
        <PoolFormNameInput InputProps={getInputProps(NAME, isOrganizationPool, isReadOnly)} />
        <PoolFormLimitInput unallocatedLimit={unallocatedLimit} isRootPool={!parentPoolId} isReadOnly={isReadOnly} />
        {parentPoolId && <PoolFormAutoExtendCheckbox isReadOnly={isReadOnly} />}
        <PoolFormTypeSelector InputProps={getInputProps(TYPE, isOrganizationPool, isReadOnly)} />
        {!isOrganizationPool && <PoolTypesDescription />}
        <FormButtonsWrapper justifyContent="space-between">
          <Box display="flex">
            <ButtonLoader
              variant="contained"
              messageId="save"
              disabled={isReadOnly}
              color="primary"
              type="submit"
              isLoading={isUpdatePoolLoading}
              dataTestId="btn_create"
              tooltip={{ show: isReadOnly, messageId: "onlyOrganizationManagersCanSetThisUp" }}
            />
          </Box>
        </FormButtonsWrapper>
      </form>
    </FormProvider>
  );
};

export default EditPoolForm;
