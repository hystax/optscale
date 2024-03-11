import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import { Stack } from "@mui/system";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import CaptionedCell from "components/CaptionedCell";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import Markdown from "components/Markdown";
import { MlDeleteDatasetModal } from "components/SideModalManager/SideModals";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { ML_DATASET_CREATE, getEditMlDatasetUrl } from "urls";
import { datasetLabels, text } from "utils/columns";
import { EN_FULL_FORMAT, formatUTC } from "utils/datetime";
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
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_training_set">
            <FormattedMessage id="trainingSet" />
          </TextWithDataTestId>
        ),
        id: "trainingSet",
        accessorFn: (originalRow) => originalRow.training_set?.path,
        cell: ({
          cell,
          row: {
            original: {
              training_set: { timespan_from: timespanFrom, timespan_to: timespanTo }
            }
          }
        }) => (
          <CaptionedCell
            caption={[
              {
                key: "timespanFrom",
                node: (
                  <KeyValueLabel
                    keyMessageId="from"
                    variant="caption"
                    value={timespanFrom ? formatUTC(timespanFrom, EN_FULL_FORMAT) : undefined}
                  />
                )
              },
              {
                key: "timespanTo",
                node: (
                  <KeyValueLabel
                    keyMessageId="to"
                    variant="caption"
                    value={timespanTo ? formatUTC(timespanTo, EN_FULL_FORMAT) : undefined}
                  />
                )
              }
            ]}
          >
            {cell.getValue()}
          </CaptionedCell>
        )
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_validation_set">
            <FormattedMessage id="validationSet" />
          </TextWithDataTestId>
        ),
        id: "validationSet",
        accessorFn: (originalRow) => originalRow.validation_set?.path,
        cell: ({
          cell,
          row: {
            original: {
              validation_set: { timespan_from: timespanFrom, timespan_to: timespanTo }
            }
          }
        }) => (
          <CaptionedCell
            caption={[
              {
                key: "timespanFrom",
                node: (
                  <KeyValueLabel
                    keyMessageId="from"
                    variant="caption"
                    value={timespanFrom ? formatUTC(timespanFrom, EN_FULL_FORMAT) : undefined}
                  />
                )
              },
              {
                key: "timespanTo",
                node: (
                  <KeyValueLabel
                    keyMessageId="to"
                    variant="caption"
                    value={timespanTo ? formatUTC(timespanTo, EN_FULL_FORMAT) : undefined}
                  />
                )
              }
            ]}
          >
            {cell.getValue()}
          </CaptionedCell>
        )
      },
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
        accessorKey: "labels",
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
