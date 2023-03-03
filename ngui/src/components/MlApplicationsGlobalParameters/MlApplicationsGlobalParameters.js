import React, { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import { Breadcrumbs, Link } from "@mui/material";
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
import { ML_MODELS_PARAMETER_CREATE, getEditModelParameterUrl, ML_APPLICATIONS } from "urls";
import { goalValue, name, tendency, text } from "utils/columns";
import aggregateFunction from "utils/columns/aggregateFunction";

const actionBarDefinition = {
  title: {
    text: (
      <>
        <FormattedMessage id="mlApplicationsParametersLibraryTitle" />
        <Breadcrumbs>
          <Link to={ML_APPLICATIONS} component={RouterLink}>
            <FormattedMessage id="applications" />
          </Link>
          <FormattedMessage id="mlApplicationsParametersLibrary" />
        </Breadcrumbs>
      </>
    ),
    dataTestId: "lbl_ml_applications_global_parameters"
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
      link: ML_MODELS_PARAMETER_CREATE,
      requiredActions: ["EDIT_PARTNER"],
      dataTestId: "btn_add"
    }
  ]
};

const MlApplicationsGlobalParameters = ({ parameters, isLoading }) => {
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
        <Table
          isLoading={isLoading}
          data={memoizedParameters}
          columns={columns}
          actionBar={{
            show: true,
            definition: tableActionBarDefinition
          }}
          localization={{
            emptyMessageId: "noParameters"
          }}
        />
        <InlineSeverityAlert messageId="mlGlobalParametersDescription" />
      </PageContentWrapper>
    </>
  );
};

export default MlApplicationsGlobalParameters;
