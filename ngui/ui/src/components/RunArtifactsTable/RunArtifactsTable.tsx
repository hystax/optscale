import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import { FormattedMessage } from "react-intl";
import { useNavigate, useParams } from "react-router-dom";
import { MlDeleteArtifactModal } from "components/SideModalManager/SideModals";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TextWithDataTestId from "components/TextWithDataTestId";
import { Pagination, Search } from "containers/MlArtifactsContainer/MlArtifactsContainer";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { Artifact } from "services/MlArtifactsService";
import { getCreateMlRunArtifactUrl, getEditMlRunArtifactUrl } from "urls";
import { markdown, slicedText, tags, utcTime } from "utils/columns";

type RunArtifactsTableProps = {
  artifacts: Artifact[];
  pagination: Pagination;
  search: Search;
};

const RunArtifactsTable = ({ artifacts, pagination, search }: RunArtifactsTableProps) => {
  const { taskId, runId } = useParams() as { taskId: string; runId: string };

  const navigate = useNavigate();

  const openSideModal = useOpenSideModal();

  const isManageArtifactsAllowed = useIsAllowed({
    requiredActions: ["EDIT_PARTNER"]
  });

  const tableData = useMemo(() => artifacts, [artifacts]);

  const columns = useMemo(() => {
    const getActionsColumn = () => ({
      header: (
        <TextWithDataTestId dataTestId="lbl_actions">
          <FormattedMessage id="actions" />
        </TextWithDataTestId>
      ),
      enableSorting: false,
      id: "actions",
      cell: ({
        row: {
          original: { id: artifactId, name, run: { task_id: artifactRunTaskId, id: artifactRunId } = {}, index }
        }
      }) => (
        <TableCellActions
          items={[
            {
              key: "adit",
              messageId: "edit",
              icon: <EditOutlinedIcon />,
              requiredActions: ["EDIT_PARTNER"],
              dataTestId: `btn_edit_${index}`,
              action: () => navigate(getEditMlRunArtifactUrl(artifactRunTaskId, artifactRunId, artifactId))
            },
            {
              key: "delete",
              messageId: "delete",
              icon: <DeleteOutlinedIcon />,
              color: "error",
              requiredActions: ["EDIT_PARTNER"],
              dataTestId: `btn_delete_${index}`,
              action: () =>
                openSideModal(MlDeleteArtifactModal, {
                  id: artifactId,
                  name,
                  onSuccess: () => {
                    const isLastArtifactOnPage = artifacts.length === 1;

                    if (isLastArtifactOnPage) {
                      pagination.onPageIndexChange(Math.max(pagination.pageIndex - 1, 0));
                    }
                  }
                })
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
        maxTextLength: 70,
        enableSorting: false
      }),
      slicedText({
        headerMessageId: "path",
        headerDataTestId: "lbl_path",
        accessorKey: "path",
        maxTextLength: 70,
        copy: true,
        enableSorting: false
      }),
      markdown({
        id: "description",
        accessorFn: (originalRow) => originalRow.description,
        headerMessageId: "description",
        headerDataTestId: "lbl_description",
        enableSorting: false
      }),
      utcTime({
        id: "createdAt",
        accessorFn: (originalRow) => originalRow.created_at,
        headerMessageId: "createdAt",
        headerDataTestId: "lbl_created_at",
        enableSorting: false
      }),
      tags({
        id: "tags",
        accessorFn: (originalRow) =>
          Object.entries(originalRow.tags ?? {})
            .map(([key, val]) => `${key}: ${val}`)
            .join(" "),
        getTags: (originalRow) => originalRow.tags,
        enableSorting: false
      }),
      ...(isManageArtifactsAllowed ? [getActionsColumn()] : [])
    ];
  }, [artifacts.length, isManageArtifactsAllowed, navigate, openSideModal, pagination]);

  return (
    <Table
      data={tableData}
      columns={columns}
      actionBar={{
        show: true,
        definition: {
          items: [
            {
              key: "add",
              icon: <AddOutlinedIcon fontSize="small" />,
              messageId: "add",
              color: "success",
              variant: "contained",
              type: "button",
              link: getCreateMlRunArtifactUrl(taskId, runId),
              dataTestId: "btn_add",
              requiredActions: ["EDIT_PARTNER"]
            }
          ]
        }
      }}
      localization={{ emptyMessageId: "noArtifacts" }}
      manualPagination={pagination}
      withSearch
      manualGlobalFiltering={{
        search
      }}
      counters={{
        showCounters: true
      }}
    />
  );
};

export default RunArtifactsTable;
