import { useMemo } from "react";
import { Box } from "@mui/material";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import { possibleMonthlySavings, text } from "utils/columns";
import Actions from "../Actions";
import BaseRecommendation from "../recommendations/BaseRecommendation";
import actions from "./columns/actions";
import buttonLink from "./columns/buttonLink";
import services from "./columns/services";
import status from "./columns/status";

type RecommendationsTableProps = {
  isLoading: boolean;
  recommendations: BaseRecommendation[];
  downloadLimit?: number;
  onRecommendationClick: (id: string) => void;
  isDownloadAvailable: boolean;
  isGetIsDownloadAvailableLoading: boolean;
  selectedDataSourceIds: string[];
};

const RecommendationsTable = ({
  isLoading,
  recommendations = [],
  downloadLimit,
  onRecommendationClick,
  isDownloadAvailable,
  isGetIsDownloadAvailableLoading,
  selectedDataSourceIds,
}: RecommendationsTableProps) => {
  const tableData = useMemo(
    () =>
      recommendations.map((r) => ({
        title: r.title,
        type: r.type,
        items: r.count,
        saving: r.saving,
        status: r.color || "ok",
        services: r.services,
        recommendation: r,
      })),
    [recommendations]
  );

  const columns = useMemo(
    () => [
      buttonLink({
        headerDataTestId: "recommendation-name-header",
        accessorKey: "title",
        onClick: ({
          row: {
            original: { recommendation },
          },
        }) => onRecommendationClick(recommendation),
      }),
      status({ headerDataTestId: "status-header", accessorKey: "status" }),
      text({ headerDataTestId: "items-count-header", headerMessageId: "items", accessorKey: "items" }),
      possibleMonthlySavings({ headerDataTestId: "savings-header", accessorKey: "saving" }),
      services({ headerDataTestId: "services-header", accessorKey: "services" }),
      actions({
        headerDataTestId: "actions-header",
        cell: ({ row: { original } }) => (
          <Actions
            downloadLimit={downloadLimit}
            recommendation={original.recommendation}
            isDownloadAvailable={isDownloadAvailable}
            isGetIsDownloadAvailableLoading={isGetIsDownloadAvailableLoading}
            selectedDataSourceIds={selectedDataSourceIds}
          />
        ),
      }),
    ],
    [downloadLimit, isDownloadAvailable, onRecommendationClick, isGetIsDownloadAvailableLoading, selectedDataSourceIds]
  );

  return (
    <Box sx={{ width: "100%" }}>
      {isLoading ? (
        <TableLoader columnsCounter={columns.length} />
      ) : (
        <Table
          data={tableData}
          columns={columns}
          counters={{
            show: false,
          }}
        />
      )}
    </Box>
  );
};

export default RecommendationsTable;
