import React, { useEffect } from "react";
import { Typography } from "@mui/material";
import { Box } from "@mui/system";
import PropTypes from "prop-types";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import WrapperCard from "components/WrapperCard";
import { useIsUpMediaQuery } from "hooks/useMediaQueries";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { CreatePoolPolicyPoolSelector, CreatePoolPolicyPolicyTypeSelector, CreatePoolPolicyLimitInput } from "./FormElements";

const POOL_ID = "poolId";
const POLICY_TYPE = "policyType";
const LIMIT = "limit";

const CreatePoolPolicyForm = ({
  pools,
  hasPermissionsToCreatePolicy,
  onSubmit,
  onCancel,
  isGetLoading = false,
  isDataReady = false,
  isSubmitLoading = false
}) => {
  const methods = useForm({
    defaultValues: {
      [POOL_ID]: "",
      [POLICY_TYPE]: "",
      [LIMIT]: ""
    }
  });

  const {
    handleSubmit,
    watch,
    setValue,
    formState: { isValidating },
    trigger
  } = methods;

  const isUpXl = useIsUpMediaQuery("xl");

  const policyType = watch(POLICY_TYPE);

  useEffect(() => {
    if (isValidating) {
      trigger(LIMIT);
    }
  }, [policyType, trigger, isValidating]);

  const isSubmitDisabled = () => isDataReady && (!hasPermissionsToCreatePolicy || isEmptyArray(pools));

  const selectedPoolId = watch(POOL_ID);

  const selectedPool = pools.find(({ id }) => id === selectedPoolId) ?? {};

  const renderContent = () => {
    if (isDataReady) {
      if (!hasPermissionsToCreatePolicy) {
        return (
          <>
            <Typography>
              <FormattedMessage id="youDoNotHaveEnoughPermissions" />
            </Typography>
            <Typography>
              <FormattedMessage id="onlyManagersCanCreateNewPoolPolicy" />
            </Typography>
            <Typography>
              <FormattedMessage id="poolPolicyContactManager" />
            </Typography>
          </>
        );
      }
      if (isEmptyArray(pools)) {
        return (
          <Typography>
            <FormattedMessage id="poolPolicyCannotBeCreated" />
          </Typography>
        );
      }
    }

    return (
      <>
        <CreatePoolPolicyPoolSelector
          name={POOL_ID}
          onChange={() => setValue(POLICY_TYPE, "")}
          pools={pools}
          isLoading={isGetLoading}
        />
        <CreatePoolPolicyPolicyTypeSelector name={POLICY_TYPE} selectedPool={selectedPool} />
        <CreatePoolPolicyLimitInput name={LIMIT} policyType={policyType} />
      </>
    );
  };

  return (
    <WrapperCard className={isUpXl ? "halfWidth" : ""}>
      <Typography paragraph data-test-id="p_form_description">
        <FormattedMessage id="createPoolPolicyFormDescription" />
      </Typography>
      <FormProvider {...methods}>
        <form
          onSubmit={handleSubmit(({ [POOL_ID]: poolIdValue, [LIMIT]: limitValue, [POLICY_TYPE]: policyTypeValue }) => {
            onSubmit({
              poolId: poolIdValue,
              limit: Number(limitValue),
              type: policyTypeValue
            });
          })}
          noValidate
        >
          {renderContent()}
          <FormButtonsWrapper justifyContent="space-between">
            <Box display="flex">
              <ButtonLoader
                variant="contained"
                messageId="save"
                color="primary"
                type="submit"
                isLoading={isGetLoading || isSubmitLoading}
                dataTestId="btn_save"
                disabled={isSubmitDisabled()}
              />
              <Button dataTestId="btn_cancel" messageId="cancel" onClick={onCancel} />
            </Box>
          </FormButtonsWrapper>
        </form>
      </FormProvider>
    </WrapperCard>
  );
};

CreatePoolPolicyForm.propTypes = {
  pools: PropTypes.array.isRequired,
  hasPermissionsToCreatePolicy: PropTypes.bool.isRequired,
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  isGetLoading: PropTypes.bool,
  isSubmitLoading: PropTypes.bool,
  isDataReady: PropTypes.bool
};

export default CreatePoolPolicyForm;
