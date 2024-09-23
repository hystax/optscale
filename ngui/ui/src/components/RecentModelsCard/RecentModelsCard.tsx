import { useMemo } from "react";
import ExitToAppOutlinedIcon from "@mui/icons-material/ExitToAppOutlined";
import { Box } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import IconButton from "components/IconButton";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import WrapperCard from "components/WrapperCard";
import { ListModel } from "services/MlModelsService";
import { ML_MODELS } from "urls";
import { mlModelUsedAliases, mlModelVersion, model } from "utils/columns";

type RecentModelsCardProps = {
  models: ListModel[];
  isLoading?: boolean;
};

type RecentModelsTableProps = {
  models: ListModel[];
};

const RecentModelsTable = ({ models }: RecentModelsTableProps) => {
  const tableData = useMemo(
    () => models.toSorted((modelA, modelB) => (modelB.last_version?.created_at ?? 0) - (modelA.last_version?.created_at ?? 0)),
    [models]
  );

  const columns = useMemo(
    () => [
      model({
        id: "model",
        getName: (rowOriginal) => rowOriginal.name,
        getId: (rowOriginal) => rowOriginal.id,
        headerMessageId: "name",
        headerDataTestId: "lbl_model",
        enableSorting: false
      }),
      mlModelVersion({
        headerMessageId: "version",
        headerDataTestId: "lbl_latest_versions",
        id: "latestVersion",
        accessorFn: (originalRow) => originalRow.last_version?.version,
        enableSorting: false
      }),
      mlModelUsedAliases()
    ],
    []
  );

  return (
    <Table
      data={tableData}
      columns={columns}
      pageSize={5}
      enablePaginationQueryParam={false}
      localization={{
        emptyMessageId: "noTasks"
      }}
    />
  );
};

const RecentModelsCard = ({ models, isLoading = false }: RecentModelsCardProps) => {
  const navigate = useNavigate();

  const goToTasks = () => navigate(ML_MODELS);

  return (
    <WrapperCard
      needAlign
      title={
        <Box display="flex" alignItems="center">
          <Box mr={0.5}>
            <FormattedMessage id="models" />
          </Box>
          <Box display="flex">
            <IconButton
              icon={<ExitToAppOutlinedIcon />}
              tooltip={{
                show: true,
                messageId: "goToModels"
              }}
              onClick={goToTasks}
              isLoading={isLoading}
              dataTestId="btn_go_to_models"
            />
          </Box>
        </Box>
      }
      dataTestIds={{
        wrapper: "block_recent_models",
        title: "lbl_recent_models",
        titleCaption: "p_recent_models"
      }}
      elevation={0}
    >
      {isLoading ? <TableLoader /> : <RecentModelsTable models={models} />}
    </WrapperCard>
  );
};

export default RecentModelsCard;
