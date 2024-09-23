import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import { Box } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import Markdown from "components/Markdown";
import { MlDeleteDatasetModal } from "components/SideModalManager/SideModals";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { ML_DATASET_CREATE, getEditMlDatasetUrl } from "urls";
import { datasetLabels, datasetTimespan, localTime, slicedText } from "utils/columns";
import { DATASET_NAME_LENGTH_LIMIT, DATASET_PATH_LENGTH_LIMIT } from "utils/constants";
import { secondsToMilliseconds } from "utils/datetime";

const MlDatasetsTable = ({ datasets }) => {
  const openSideModal = useOpenSideModal();
  const navigate = useNavigate();

  const isManageDatasetsAllowed = useIsAllowed({
    requiredActions: ["EDIT_PARTNER"]
  });

  const columns = useMemo(() => {
    const getActionsColumn = () => ({
      header: (
        <TextWithDataTestId dataTestId="lbl_actions">
          <FormattedMessage id="actions" />
        </TextWithDataTestId>
      ),
      enableSorting: false,
      id: "actions",
      cell: ({ row: { original: { id, path } = {}, index } }) => (
        <TableCellActions
          items={[
            {
              key: "adit",
              messageId: "edit",
              icon: <EditOutlinedIcon />,
              requiredActions: ["EDIT_PARTNER"],
              dataTestId: `btn_edit_${index}`,
              action: () => navigate(getEditMlDatasetUrl(id))
            },
            {
              key: "delete",
              messageId: "delete",
              icon: <DeleteOutlinedIcon />,
              color: "error",
              requiredActions: ["EDIT_PARTNER"],
              dataTestId: `btn_delete_${index}`,
              action: () => openSideModal(MlDeleteDatasetModal, { id, path })
            }
          ]}
        />
      )
    });

    return [
      slicedText({
        headerMessageId: "name",
        headerDataTestId: "lbl_name",
        accessorKey: "name",
        maxTextLength: DATASET_NAME_LENGTH_LIMIT
      }),
      slicedText({
        headerMessageId: "path",
        headerDataTestId: "lbl_path",
        accessorKey: "path",
        maxTextLength: DATASET_PATH_LENGTH_LIMIT,
        copy: true
      }),
      localTime({
        id: "created_at",
        accessorFn: (originalRow) => secondsToMilliseconds(originalRow.created_at),
        headerDataTestId: "lbl_updated_at",
        headerMessageId: "createdAt",
        defaultSort: "desc"
      }),
      datasetTimespan(),
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_description">
            <FormattedMessage id="description" />
          </TextWithDataTestId>
        ),
        accessorKey: "description",
        style: {
          minWidth: 200,
          maxWidth: 400
        },
        cell: ({ cell }) => (
          <Box overflow="auto">
            <Markdown>{cell.getValue()}</Markdown>
          </Box>
        )
      },
      datasetLabels({
        id: "labels",
        accessorFn: (originalRow) => originalRow.labels,
        style: {
          maxWidth: "400px"
        }
      }),
      ...(isManageDatasetsAllowed ? [getActionsColumn()] : [])
    ];
  }, [isManageDatasetsAllowed, navigate, openSideModal]);

  const data = useMemo(() => datasets, [datasets]);

  const tableActionBarDefinition = {
    show: true,
    definition: {
      items: [
        {
          key: "btn-create-dataset",
          icon: <AddOutlinedIcon />,
          messageId: "add",
          color: "success",
          variant: "contained",
          type: "button",
          dataTestId: "btn-create-dataset",
          link: ML_DATASET_CREATE,
          requiredActions: ["EDIT_PARTNER"]
        }
      ]
    }
  };

  return <Table data={data} columns={columns} actionBar={tableActionBarDefinition} withSearch pageSize={50} />;
};

export default MlDatasetsTable;
