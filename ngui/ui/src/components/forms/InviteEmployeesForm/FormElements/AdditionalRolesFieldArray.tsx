import { Fragment } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import { Box } from "@mui/material";
import FormControl from "@mui/material/FormControl";
import Grid from "@mui/material/Grid";
import { useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { makeStyles } from "tss-react/mui";
import Button from "components/Button";
import { Selector } from "components/forms/common/fields";
import IconButton from "components/IconButton";
import Input from "components/Input";
import { ItemContent, ItemContentWithPoolIcon } from "components/Selector";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { intl } from "translations/react-intl-config";
import { MANAGER, ENGINEER, ORGANIZATION_MANAGER, INVITABLE_ROLE_PURPOSES } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { FIELD_NAMES } from "../constants";
import { FormValues, InviteEmployeesFormProps, PoolTreeNode } from "../types";

const { FIELD_NAME, ROLE, POOL_ID } = FIELD_NAMES.ADDITIONAL_ROLES_FIELD_ARRAY;

const DEFAULT_ADDITIONAL_ROLE_CONDITION = { [ROLE]: "", [POOL_ID]: "" } as const;

const useStyles = makeStyles()(() => ({
  item: {
    width: "100%",
    minWidth: 0
  },
  deleteButton: {
    alignItems: "flex-end"
  }
}));

const flattenPoolTree = (poolsTree: PoolTreeNode[], level = 0): PoolTreeNode[] =>
  poolsTree.flatMap((pool) => [pool, ...flattenPoolTree(pool.children, level + 1)]);

const getPoolTree = (pools: InviteEmployeesFormProps["availablePools"], id: string | null = null, level = 0): PoolTreeNode[] =>
  [...pools]
    .sort((a, b) => a.name.localeCompare(b.name))
    .filter((pool) => pool.parent_id === id)
    .map((pool) => ({
      ...pool,
      level,
      children: getPoolTree(pools, pool.id, level + 1)
    }));

const AdditionalRolesFieldArray = ({ isGetAvailablePoolsLoading, availablePools, fields, onFieldAppend, onFieldRemove }) => {
  const { watch } = useFormContext<FormValues>();

  const { classes, cx } = useStyles();

  const { name: organizationName } = useOrganizationInfo();

  const watchAdditionalRoles = watch(FIELD_NAME);
  const busyPoolIds = watchAdditionalRoles?.map((item) => item[POOL_ID]) ?? [];
  const busyRoles = watchAdditionalRoles?.map((item) => item[ROLE]) ?? [];

  const flatPools = flattenPoolTree(getPoolTree(availablePools));

  const renderPoolField = (count: number) => (
    <Selector
      id="pool-selector"
      name={`${FIELD_NAME}.${count}.${POOL_ID}`}
      labelMessageId="pool"
      required
      fullWidth
      isLoading={isGetAvailablePoolsLoading}
      items={flatPools.map((obj) => ({
        value: obj.id,
        content: (
          <Box>
            <ItemContentWithPoolIcon poolType={obj.pool_purpose}>{obj.name}</ItemContentWithPoolIcon>
          </Box>
        ),
        depth: obj.level,
        disabled: (field) => busyPoolIds.includes(obj.id) && obj.id !== field.value
      }))}
    />
  );

  const renderOrganizationField = (count: number) => (
    <Input
      required
      InputProps={{
        readOnly: true
      }}
      defaultValue={organizationName}
      label={<FormattedMessage id="organization" />}
      type="text"
      dataTestId={`input_org_${count}`}
    />
  );

  const additionalRolesRow = (count: number) => {
    const additionalRole = watchAdditionalRoles?.[count]?.[ROLE];

    const getScopeFieldRenderer = () => {
      const poolFieldRenderer = () => renderPoolField(count);
      const organizationFieldRender = () => renderOrganizationField(count);
      return (
        {
          [ORGANIZATION_MANAGER]: organizationFieldRender,
          [MANAGER]: poolFieldRenderer,
          [ENGINEER]: poolFieldRenderer
        }[additionalRole] || poolFieldRenderer
      );
    };

    const renderScopeField = getScopeFieldRenderer();

    return (
      <Grid container spacing={SPACING_1}>
        <Grid item xs={4}>
          <Box>
            <Selector
              id="role-selector"
              name={`${FIELD_NAME}.${count}.${ROLE}`}
              labelMessageId="role"
              required
              fullWidth
              items={Object.entries(INVITABLE_ROLE_PURPOSES).map(([role, roleMessageId]) => ({
                value: role,
                content: (
                  <Box>
                    <ItemContent>{intl.formatMessage({ id: roleMessageId })}</ItemContent>
                  </Box>
                ),
                disabled: (field) =>
                  role === ORGANIZATION_MANAGER && busyRoles.includes(ORGANIZATION_MANAGER) && role !== field.value
              }))}
            />
          </Box>
        </Grid>
        <Grid item xs={8}>
          <Box display="flex">
            <Box flexGrow={1}>{renderScopeField()}</Box>
            <Box>
              <FormControl className={cx(classes.item, classes.deleteButton)}>
                <IconButton
                  color="error"
                  icon={<DeleteOutlinedIcon />}
                  onClick={() => onFieldRemove(count)}
                  tooltip={{
                    show: true,
                    value: <FormattedMessage id="delete" />
                  }}
                  dataTestId={`btn_delete_${count}`}
                />
              </FormControl>
            </Box>
          </Box>
        </Grid>
      </Grid>
    );
  };

  return (
    <>
      {fields.map((item, index) => (
        <Fragment key={item.id}>{additionalRolesRow(index)}</Fragment>
      ))}
      <FormControl fullWidth>
        <Button
          dashedBorder
          startIcon={<AddOutlinedIcon />}
          messageId="addRole"
          dataTestId="btn_add"
          size="large"
          color="primary"
          onClick={() => onFieldAppend(DEFAULT_ADDITIONAL_ROLE_CONDITION)}
        />
      </FormControl>
    </>
  );
};

export default AdditionalRolesFieldArray;
