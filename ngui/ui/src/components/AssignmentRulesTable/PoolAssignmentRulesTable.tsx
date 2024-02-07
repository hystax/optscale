import { useMemo } from "react";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import { conditions, name, owner } from "./columns";
import { prepareData } from "./utils";

const PoolAssignmentRulesTable = ({ rules, isLoading = false }) => {
  const { rules: assignmentRules = [], entities = {} } = rules || {};

  const tableData = useMemo(
    () =>
      prepareData({
        assignmentRules,
        entities
      }),
    [assignmentRules, entities]
  );

  const columns = useMemo(() => [name(), owner(), conditions()], []);

  return isLoading ? (
    <TableLoader columnsCounter={4} showHeader />
  ) : (
    <>
      <Table
        data={tableData}
        columns={columns}
        localization={{ emptyMessageId: "noAutomaticResourceAssignmentRules" }}
        dataTestIds={{
          container: "table_rules"
        }}
      />
    </>
  );
};

export default PoolAssignmentRulesTable;
