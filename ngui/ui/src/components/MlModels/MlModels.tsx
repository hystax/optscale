import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import { FormattedMessage } from "react-intl";
import Markdown from "components/Markdown";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { ListModel } from "services/MlModelsService";
import { ML_MODEL_CREATE } from "urls";
import { mlModelUsedAliases, mlModelVersion, model, tags, text, utcTime } from "utils/columns";
import { CELL_EMPTY_VALUE } from "utils/tables";

type MlModelsProps = {
  models: ListModel[];
  isLoading?: boolean;
};

type ModelsTableProps = {
  models: ListModel[];
};

const ModelsTable = ({ models }: ModelsTableProps) => {
  const tableData = useMemo(() => models, [models]);

  const columns = useMemo(
    () => [
      model({
        id: "model",
        getName: (rowOriginal) => rowOriginal.name,
        getId: (rowOriginal) => rowOriginal.id,
        headerMessageId: "name",
        headerDataTestId: "lbl_model",
        defaultSort: "asc"
      }),
      text({
        headerMessageId: "key",
        headerDataTestId: "lbl_key",
        accessorKey: "key"
      }),
      mlModelVersion({
        headerMessageId: "version",
        headerDataTestId: "lbl_latest_versions",
        id: "latestVersion",
        accessorFn: (originalRow) => originalRow.last_version?.version
      }),
      mlModelUsedAliases(),
      utcTime({
        id: "createdAt",
        accessorFn: (originalRow) => originalRow.created_at,
        headerMessageId: "createdAt",
        headerDataTestId: "lbl_created_at"
      }),
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_description">
            <FormattedMessage id="description" />
          </TextWithDataTestId>
        ),
        id: "description",
        accessorFn: (originalRow) => originalRow.description ?? "",
        cell: ({ cell }) => {
          const description = cell.getValue();

          return description ? <Markdown>{description}</Markdown> : CELL_EMPTY_VALUE;
        }
      },
      tags({
        id: "tags",
        accessorFn: (originalRow) =>
          Object.entries(originalRow.tags ?? {})
            .map(([key, val]) => `${key}: ${val}`)
            .join(" "),
        getTags: (rowOriginal) => rowOriginal.tags ?? {}
      })
    ],
    []
  );

  const tableActionBarDefinition = {
    show: true,
    definition: {
      items: [
        {
          key: "btn-create-model",
          icon: <AddOutlinedIcon />,
          messageId: "add",
          color: "success",
          variant: "contained",
          type: "button",
          dataTestId: "btn-create-model",
          link: ML_MODEL_CREATE,
          requiredActions: ["EDIT_PARTNER"]
        }
      ]
    }
  };

  return (
    <Table
      data={tableData}
      columns={columns}
      withSearch
      actionBar={tableActionBarDefinition}
      pageSize={50}
      localization={{
        emptyMessageId: "noModels"
      }}
    />
  );
};

const MlModels = ({ models, isLoading = false }: MlModelsProps) =>
  isLoading ? <TableLoader /> : <ModelsTable models={models} />;

export default MlModels;
