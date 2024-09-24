import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import Table from "components/Table";
import { CREATE_BI_EXPORT } from "urls";
import {
  biExportExportedDays,
  biExportLastSuccessfulExport,
  biExportName,
  biExportNextExport,
  biExportTargetStorage
} from "utils/columns";

const BIExportsTable = ({ exports }) => {
  const columns = useMemo(
    () => [
      biExportName(),
      biExportTargetStorage(),
      biExportExportedDays(),
      biExportLastSuccessfulExport(),
      biExportNextExport()
    ],
    []
  );

  const data = useMemo(() => exports, [exports]);

  return (
    <Table
      data={data}
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
              link: CREATE_BI_EXPORT,
              dataTestId: "btn_add",
              requiredActions: ["EDIT_PARTNER"]
            }
          ]
        }
      }}
      pageSize={50}
      columns={columns}
      localization={{
        emptyMessageId: "noBIExports"
      }}
    />
  );
};

export default BIExportsTable;
