import { useMemo } from "react";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import { TABS } from "components/MlTaskRun";
import { MlDeleteArtifactModal } from "components/SideModalManager/SideModals";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TextWithDataTestId from "components/TextWithDataTestId";
import { Pagination, RangeFilter, Search } from "containers/MlArtifactsContainer/MlArtifactsContainer";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { Artifact } from "services/MlArtifactsService";
import { getEditMlArtifactUrl } from "urls";
import { markdown, run, slicedText, tags, utcTime } from "utils/columns";
import { TAB_QUERY_PARAM_NAME } from "utils/constants";

type ArtifactsTableProps = {
  artifacts: Artifact[];
  pagination: Pagination;
  search?: Search;
  rangeFilter?: RangeFilter;
};

const ArtifactsTable = ({ artifacts, pagination, search, rangeFilter }: ArtifactsTableProps) => {
  const openSideModal = useOpenSideModal();

  const tableData = useMemo(() => artifacts, [artifacts]);

  const isManageArtifactsAllowed = useIsAllowed({
    requiredActions: ["EDIT_PARTNER"]
  });

  const navigate = useNavigate();

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
          original: { id: artifactId, name, index }
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
              action: () => navigate(getEditMlArtifactUrl(artifactId))
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
      run({
        id: "run",
        getRunNumber: ({ run: { number } }) => number,
        getRunName: ({ run: { name } }) => name,
        getRunId: ({ run: { id } }) => id,
        getTaskId: ({ run: { task_id: taskId } }) => taskId,
        headerMessageId: "run",
        headerDataTestId: "lbl_run",
        enableSorting: false,
        runDetailsUrlOptions: {
          [TAB_QUERY_PARAM_NAME]: TABS.ARTIFACTS
        }
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
      localization={{ emptyMessageId: "noArtifacts" }}
      manualPagination={pagination}
      withSearch
      rangeFilter={rangeFilter?.filterComponentProps}
      manualGlobalFiltering={{
        search,
        rangeFilter: rangeFilter?.manualFilterDefinition
      }}
      counters={{
        showCounters: true
      }}
    />
  );
};

export default ArtifactsTable;
