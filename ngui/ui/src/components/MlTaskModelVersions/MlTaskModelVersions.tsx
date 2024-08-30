import { useMemo } from "react";
import { Box } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { useParams } from "react-router-dom";
import LabelChip from "components/LabelChip";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { ModelVersionWithModel } from "services/MlModelsService";
import { isEmpty } from "utils/arrays";
import { mlModelPath, mlModelVersion, model, run } from "utils/columns";
import { SPACING_1 } from "utils/layouts";
import { CELL_EMPTY_VALUE } from "utils/tables";

type MlTaskModelVersionsProps = {
  modelVersions: ModelVersionWithModel[];
  isLoading: boolean;
};

const MlTaskModelVersions = ({ modelVersions, isLoading }: MlTaskModelVersionsProps) => {
  const tableData = useMemo(() => modelVersions, [modelVersions]);

  const { taskId } = useParams();

  const columns = useMemo(
    () => [
      model({
        id: "model",
        getName: (rowOriginal) => rowOriginal.model.name,
        getId: (rowOriginal) => rowOriginal.model.id,
        headerMessageId: "model",
        headerDataTestId: "lbl_model"
      }),
      run({
        id: "run",
        getRunNumber: ({ run: { number } }) => number,
        getRunName: ({ run: { name } }) => name,
        getRunId: ({ run: { id } }) => id,
        getTaskId: () => taskId,
        headerMessageId: "run",
        headerDataTestId: "lbl_run"
      }),
      mlModelVersion({
        headerMessageId: "version",
        headerDataTestId: "lbl_version",
        accessorKey: "version"
      }),
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_aliases">
            <FormattedMessage id="aliases" />
          </TextWithDataTestId>
        ),
        id: "aliases",
        accessorFn: ({ aliases }) => aliases.join(", "),
        enableSorting: false,
        cell: ({ row: { original } }) => {
          const { aliases } = original;

          if (isEmpty(aliases)) {
            return CELL_EMPTY_VALUE;
          }

          return (
            <Box display="flex" gap={SPACING_1} alignItems="center" flexWrap="wrap">
              {aliases.map((alias) => (
                <LabelChip key={alias} label={alias} />
              ))}
            </Box>
          );
        }
      },
      mlModelPath({
        accessorKey: "path",
        headerMessageId: "path",
        headerDataTestId: "lbl_path"
      })
    ],
    [taskId]
  );

  return isLoading ? (
    <TableLoader />
  ) : (
    <Table
      data={tableData}
      columns={columns}
      withSearch
      queryParamPrefix="modelVersion"
      pageSize={50}
      localization={{
        emptyMessageId: "noModelVersions"
      }}
      counters={{ showCounters: true }}
    />
  );
};

export default MlTaskModelVersions;
