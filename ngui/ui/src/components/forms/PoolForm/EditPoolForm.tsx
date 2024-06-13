import { Box } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useIsAllowed } from "hooks/useAllowedActions";
import PoolsService from "services/PoolsService";
import { SCOPE_TYPES } from "utils/constants";
import { NameField, LimitField, TypeSelector, AutoExtendCheckbox, OwnerSelector } from "./FormElements";
import { EditPoolFormValues } from "./types";
import { getEditFormDefaultValues } from "./utils";

const EditPoolForm = ({ unallocatedLimit, poolInfo, onSuccess, onCancel }) => {
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

  const methods = useForm<EditPoolFormValues>({
    defaultValues: getEditFormDefaultValues({
      poolName,
      limitAmount,
      defaultResourceOwnerId,
      type
    })
  });

  const { handleSubmit } = methods;

  const onSubmit = handleSubmit((formValues) => updatePool({ ...formValues, poolId: id, parentPoolId }).then(onSuccess));

  const isOrganizationPool = !parentPoolId;
  const nameAndTypeReadOnly = !!(isOrganizationPool || isReadOnly);

  return (
    <FormProvider {...methods}>
      <form data-test-id="form_edit_pool" onSubmit={onSubmit} noValidate>
        <NameField readOnly={nameAndTypeReadOnly} />
        <TypeSelector readOnly={nameAndTypeReadOnly} />
        <OwnerSelector isLoading={!isPoolOwnersDataReady} owners={poolOwners} isReadOnly={isReadOnly} />
        <LimitField unallocatedLimit={unallocatedLimit} isRootPool={!parentPoolId} isReadOnly={isReadOnly} />
        {parentPoolId && <AutoExtendCheckbox isReadOnly={isReadOnly} />}
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
            <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
          </Box>
        </FormButtonsWrapper>
      </form>
    </FormProvider>
  );
};

export default EditPoolForm;
