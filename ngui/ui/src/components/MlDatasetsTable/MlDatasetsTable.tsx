import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import { Stack } from "@mui/system";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import Markdown from "components/Markdown";
import { MlDeleteDatasetModal } from "components/SideModalManager/SideModals";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { ML_DATASET_CREATE, getEditMlDatasetUrl } from "urls";
import { datasetLabels, datasetTimespan, text } from "utils/columns";
import { SPACING_1 } from "utils/layouts";

const MlDatasetsTable = ({ datasets }) => {
  const openSideModal = useOpenSideModal();
  const navigate = useNavigate();

  const columns = useMemo(
    () => [
      text({
        headerDataTestId: "lbl_name",
        headerMessageId: "name",
        accessorKey: "name"
      }),
      text({
        headerDataTestId: "lbl_id",
        headerMessageId: "id",
        accessorKey: "path"
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
          maxWidth: 400,
          overflow: "auto"
        },
        cell: ({ cell }) => <Markdown>{cell.getValue()}</Markdown>
      },
      datasetLabels({
        id: "labels",
        accessorFn: (originalRow) => originalRow.labels,
        style: {
          maxWidth: "400px"
        }
      }),
      {
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
      }
    ],
    [openSideModal, navigate]
  );

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

  return (
    <>
      <Stack spacing={SPACING_1}>
        <div>
          <Table data={data} columns={columns} actionBar={tableActionBarDefinition} withSearch pageSize={50} />
        </div>
      </Stack>
    </>
  );
};

export default MlDatasetsTable;
