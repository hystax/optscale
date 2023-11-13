import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import Table from "components/Table";
import anomalyStatusChart from "utils/columns/anomalyStatusChart";
import constraintHitActions from "utils/columns/constraintHitActions";
import constraintHitValue from "utils/columns/constraintHitValue";
import violatedAt from "utils/columns/violatedAt";
import { ANOMALY_TYPES } from "utils/constants";

const DetectedConstraintsHistoryTable = ({ limitHits, constraint }) => {
  const navigate = useNavigate();

  const tableData = useMemo(() => limitHits, [limitHits]);

  const columns = useMemo(() => {
    // column with chart is applied only for anomaly constraints
    const statusChartColumn = ANOMALY_TYPES[constraint.type] ? [anomalyStatusChart({ constraint })] : [];

    return [
      violatedAt(),
      ...statusChartColumn,
      constraintHitValue({ type: constraint.type }),
      constraintHitActions({ navigate, constraint })
    ];
  }, [navigate, constraint]);

  return (
    <Table
      data={tableData}
      columns={columns}
      localization={{
        emptyMessageId: "noDetectedAnomalies"
      }}
    />
  );
};

export default DetectedConstraintsHistoryTable;
