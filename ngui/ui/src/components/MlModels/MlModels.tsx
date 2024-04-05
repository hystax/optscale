import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import { Box } from "@mui/material";
import { FormattedMessage } from "react-intl";
import ExpandableList from "components/ExpandableList";
import LabelChip from "components/LabelChip";
import Markdown from "components/Markdown";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { ListModel } from "services/MlModelsService";
import { ML_MODEL_CREATE } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { mlModelVersion, model, tags, text, utcTime } from "utils/columns";
import { CELL_EMPTY_VALUE } from "utils/tables";

type MlModelsProps = {
  models: ListModel[];
  isLoading?: boolean;
};

type ModelsTableProps = {
  models: ListModel[];
};

const ALIASED_VERSIONS_SHOW_MORE_LIMIT = 3;

const getAliasedVersionString = (version: string, alias: string) => `${alias}: ${version}` as const;

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
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_used_aliases">
            <FormattedMessage id="usedAliases" />
          </TextWithDataTestId>
        ),
        id: "usedAliases",
        enableSorting: false,
        style: {
          maxWidth: "350px"
        },
        accessorFn: ({ aliased_versions: aliasedVersions = [] }) =>
          aliasedVersions.map(({ version, alias }) => getAliasedVersionString(version, alias)).join(" "),
        cell: ({ row: { original } }) => {
          const { aliased_versions: aliasedVersions } = original;

          if (isEmptyArray(aliasedVersions)) {
            return CELL_EMPTY_VALUE;
          }

          return (
            <Box display="flex" flexWrap="wrap" gap={1}>
              <ExpandableList
                items={aliasedVersions}
                render={(item) => {
                  const versionAliasString = getAliasedVersionString(item.version, item.alias);

                  return (
                    <LabelChip
                      key={versionAliasString}
                      label={versionAliasString}
                      colorizeBy={item.alias}
                      labelSymbolsLimit={40}
                    />
                  );
                }}
                maxRows={ALIASED_VERSIONS_SHOW_MORE_LIMIT}
              />
            </Box>
          );
        }
      },
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
