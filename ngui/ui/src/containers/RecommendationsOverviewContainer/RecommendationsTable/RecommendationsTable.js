import React, { useMemo } from "react";
import { Box } from "@mui/material";
import PropTypes from "prop-types";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import { possibleMonthlySavings, text } from "utils/columns";
import Actions from "../Actions";
import actions from "./columns/actions";
import buttonLink from "./columns/buttonLink";
import services from "./columns/services";
import status from "./columns/status";

const RecommendationsTable = ({
  isLoading,
  recommendations = [],
  downloadLimit,
  onRecommendationClick,
  isDownloadAvailable,
  isGetIsDownloadAvailableLoading,
  selectedDataSources
}) => {
  const tableData = useMemo(
    () =>
      recommendations.map((r) => ({
        title: r.title,
        type: r.type,
        items: r.count,
        saving: r.saving,
        status: r.color || "ok",
        services: r.services,
        recommendation: r
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
            original: { recommendation }
          }
        }) => onRecommendationClick(recommendation)
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
            selectedDataSources={selectedDataSources}
          />
        )
      })
    ],
    [downloadLimit, isDownloadAvailable, onRecommendationClick, isGetIsDownloadAvailableLoading, selectedDataSources]
  );

  return (
    <Box sx={{ width: "100%" }}>
      {isLoading ? <TableLoader columnsCounter={columns.length} /> : <Table data={tableData} columns={columns} />}
    </Box>
  );
};

RecommendationsTable.propTypes = {
  isLoading: PropTypes.bool,
  downloadLimit: PropTypes.number,
  recommendations: PropTypes.array,
  onRecommendationClick: PropTypes.func,
  isDownloadAvailable: PropTypes.bool,
  isGetIsDownloadAvailableLoading: PropTypes.bool,
  selectedDataSources: PropTypes.array
};

export default RecommendationsTable;
