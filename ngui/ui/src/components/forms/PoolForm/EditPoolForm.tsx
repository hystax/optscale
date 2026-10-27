import { Box } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { useIntl } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import PoolsService from "services/PoolsService";
import { SCOPE_TYPES } from "utils/constants";
import { NameField, LimitField, TypeSelector, AutoExtendCheckbox, OwnerSelector } from "./FormElements";
import { EditPoolFormValues } from "./types";
import { getEditFormDefaultValues } from "./utils";

const EditPoolForm = ({ unallocatedLimit, poolInfo, onSuccess, onCancel }) => {
  const intl = useIntl();

  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  const { id, parent_id: parentPoolId } = poolInfo;
  const { useGetPoolOwners, useUpdatePool } = PoolsService();
  const { isLoading: isUpdatePoolLoading, updatePool } = useUpdatePool();
  const { poolOwners, isDataReady: isPoolOwnersDataReady } = useGetPoolOwners(id);

  const {
    name: poolName,
    id: poolId,
    limit: limitAmount,
    default_owner_id: defaultResourceOwnerId = "",
    purpose: type,
  } = poolInfo;

  const isReadOnly = !useIsAllowed({ entityType: SCOPE_TYPES.POOL, entityId: poolId, requiredActions: ["MANAGE_POOLS"] });

  const methods = useForm<EditPoolFormValues>({
    defaultValues: getEditFormDefaultValues({
      poolName,
      limitAmount,
      defaultResourceOwnerId,
      type,
    }),
  });

  const { handleSubmit } = methods;

  const onSubmit = handleSubmit((formValues) => updatePool({ ...formValues, poolId: id, parentPoolId }).then(onSuccess));

  const isOrganizationPool = !parentPoolId;
  const nameAndTypeReadOnly = !!(isOrganizationPool || isReadOnly);

  const getTooltipValue = () => {
    if (isRestricted) {
      return restrictionReasonMessage;
    }
    if (isReadOnly) {
      return intl.formatMessage({ id: "onlyOrganizationManagersCanSetThisUp" });
    }
    return undefined;
  };

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
              disabled={isRestricted || isReadOnly}
              color="primary"
              type="submit"
              isLoading={isUpdatePoolLoading}
              dataTestId="btn_save"
              tooltip={{
                show: isRestricted || isReadOnly,
                value: getTooltipValue(),
              }}
            />
            <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
          </Box>
        </FormButtonsWrapper>
      </form>
    </FormProvider>
  );
};

export default EditPoolForm;
