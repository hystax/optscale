import { useState } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import ButtonGroup from "components/ButtonGroup";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import PoolLabel from "components/PoolLabel";
import { useIsAllowed } from "hooks/useAllowedActions";
import { EMPTY_UUID } from "utils/constants";
import { PoolSelector, WithSubPoolsCheckbox } from "./FormElements";

const POOL_ID = "poolId";
const INCLUDE_CHILDREN = "includeChildren";
const WHOLE_ORGANIZATION_ID = 0;
const SPECIFIC_POOL_ID = 1;

const getChildren = (array, parentId) => {
  const children = array.filter((x) => x.parent_id === parentId);
  return children.length !== 0 ? [...children, ...children.flatMap((child) => getChildren(array, child.id))] : children;
};

const ReapplyRulesetForm = ({ onSubmit, managedPools, closeSideModal, isSubmitLoading }) => {
  const methods = useForm({
    defaultValues: {
      [POOL_ID]: "",
      [INCLUDE_CHILDREN]: false
    }
  });

  const { handleSubmit, watch } = methods;

  const rootPoolId = managedPools.find((i) => i.parent_id === null)?.id;

  const isOrganizationManager = useIsAllowed({ requiredActions: ["MANAGE_POOLS"] });
  const isRootPoolManager = !!rootPoolId;

  const canReapplyForWholeOrganization = isOrganizationManager || isRootPoolManager;

  const [isSpecificPool, setIsSpecificPool] = useState(!canReapplyForWholeOrganization);

  const [poolId, includeChildren] = watch([POOL_ID, INCLUDE_CHILDREN]);

  const submit = (formData) => {
    if (isSpecificPool) {
      onSubmit(formData[POOL_ID] === EMPTY_UUID ? undefined : formData[POOL_ID], formData[INCLUDE_CHILDREN]);
    } else {
      onSubmit(rootPoolId, true);
    }
  };

  const buttonsGroup = [
    ...(canReapplyForWholeOrganization
      ? [
          {
            id: WHOLE_ORGANIZATION_ID,
            messageId: "wholeOrganization",
            dataTestId: "btn_apply_rule_type_whole_organization",
            action: () => {
              setIsSpecificPool(false);
            }
          }
        ]
      : []),
    {
      id: SPECIFIC_POOL_ID,
      messageId: "specificPool",
      dataTestId: "btn_apply_rule_type_specific_pool",
      action: () => {
        setIsSpecificPool(true);
      }
    }
  ];

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(submit)} noValidate>
        <Box display="flex" flexDirection="column" mb={2}>
          <Typography data-test-id="reapply_description">
            <FormattedMessage id="reapplyRulesetDescription" />
          </Typography>
          <FormButtonsWrapper mt={1} alignItems="center">
            <Typography component="span">
              <FormattedMessage id="reapplyRulesetTo" />{" "}
            </Typography>
            <ButtonGroup buttons={buttonsGroup} activeButtonId={isSpecificPool ? SPECIFIC_POOL_ID : WHOLE_ORGANIZATION_ID} />
          </FormButtonsWrapper>
          {isSpecificPool && <PoolSelector pools={managedPools} />}
          {poolId !== EMPTY_UUID && isSpecificPool && <WithSubPoolsCheckbox />}
          {includeChildren && isSpecificPool && (
            <Box display="flex" flexWrap="wrap">
              {getChildren(managedPools, poolId).map((pool, index) => (
                <Box mr={1} key={pool.id}>
                  <PoolLabel
                    iconProps={{ dataTestId: `pool_icon_${index}` }}
                    dataTestId={`pool_name_${index}`}
                    disableLink
                    id={pool.id}
                    name={pool.name}
                    type={pool.pool_purpose}
                  />
                </Box>
              ))}
            </Box>
          )}
          <FormButtonsWrapper>
            <ButtonLoader
              dataTestId="run_btn"
              messageId="run"
              color="primary"
              variant="contained"
              isLoading={isSubmitLoading}
              type="submit"
            />
            <Button dataTestId="cancel_btn" messageId="cancel" variant="outlined" onClick={closeSideModal} />
          </FormButtonsWrapper>
        </Box>
      </form>
    </FormProvider>
  );
};

export default ReapplyRulesetForm;
