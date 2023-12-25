import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import { Link } from "@mui/material";
import { Stack } from "@mui/system";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import ActionBar from "components/ActionBar";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import PageContentWrapper from "components/PageContentWrapper";
import { DeleteMlGlobalParameterModal } from "components/SideModalManager/SideModals";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { ML_TASK_PARAMETER_CREATE, getEditModelParameterUrl, ML_TASKS } from "urls";
import { goalValue, name, tendency, text } from "utils/columns";
import aggregateFunction from "utils/columns/aggregateFunction";
import { SPACING_2 } from "utils/layouts";

const actionBarDefinition = {
  breadcrumbs: [
    <Link key={1} to={ML_TASKS} component={RouterLink}>
      <FormattedMessage id="tasks" />
    </Link>
  ],
  title: {
    messageId: "mlMetricsLibraryTitle",
    dataTestId: "lbl_ml_global_parameters"
  }
};

const tableActionBarDefinition = {
  items: [
    {
      key: "add",
      icon: <AddOutlinedIcon fontSize="small" />,
      messageId: "add",
      color: "success",
      variant: "contained",
      type: "button",
      link: ML_TASK_PARAMETER_CREATE,
      requiredActions: ["EDIT_PARTNER"],
      dataTestId: "btn_add"
    }
  ]
};

const MlModelGlobalParameters = ({ parameters, isLoading }) => {
  const memoizedParameters = useMemo(() => parameters, [parameters]);

  const navigate = useNavigate();

  const openSideModal = useOpenSideModal();

  const areActionsAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  const columns = useMemo(
    () => [
      name({ accessorKey: "name", headerDataTestId: "lbl_name" }),
      text({ headerMessageId: "key", headerDataTestId: "lbl_key", accessorKey: "key", copy: true }),
      tendency(),
      goalValue({
        accessorKey: "target_value",
        titleMessageId: "defaultGoalValue"
      }),
      aggregateFunction(),
      ...(areActionsAllowed
        ? [
            {
              header: <TextWithDataTestId dataTestId="lbl_actions" messageId="actions" />,
              id: "actions",
              disableSortBy: true,
              cell: ({
                row: {
                  id: index,
                  original: { id, name: parameterName }
                }
              }) => (
                <TableCellActions
                  items={[
                    {
                      key: "edit",
                      messageId: "edit",
                      icon: <EditOutlinedIcon />,
                      dataTestId: `btn_edit_${index}`,
                      action: () => navigate(getEditModelParameterUrl(id))
                    },
                    {
                      key: "delete",
                      messageId: "delete",
                      icon: <DeleteOutlinedIcon />,
                      action: () =>
                        openSideModal(DeleteMlGlobalParameterModal, {
                          id,
                          name: parameterName
                        }),
                      color: "error",
                      dataTestId: `btn_delete_${index}`
                    }
                  ]}
                />
              )
            }
          ]
        : [])
    ],
    [areActionsAllowed, navigate, openSideModal]
  );

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Stack spacing={SPACING_2}>
          <div>
            <Table
              isLoading={isLoading}
              data={memoizedParameters}
              columns={columns}
              actionBar={{
                show: true,
                definition: tableActionBarDefinition
              }}
              localization={{
                emptyMessageId: "noMetrics"
              }}
              pageSize={50}
            />
          </div>
          <div>
            <InlineSeverityAlert messageId="mlGlobalMetricsDescription" />
          </div>
        </Stack>
      </PageContentWrapper>
    </>
  );
};

export default MlModelGlobalParameters;
