import LinkOutlinedIcon from "@mui/icons-material/LinkOutlined";
import PriorityHighOutlinedIcon from "@mui/icons-material/PriorityHighOutlined";
import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import Icon from "components/Icon";
import PoolLabel from "components/PoolLabel";
import Expander from "components/Table/components/Expander";
import TextWithDataTestId from "components/TextWithDataTestId";
import Tooltip from "components/Tooltip";
import { isEmpty as isEmptyArray } from "utils/arrays";

const poolName = ({ onExpensesExportClick, onConstraintsClick }) => ({
  header: <TextWithDataTestId dataTestId="lbl_name" messageId="name" />,
  accessorKey: "name",
  cell: ({ row }) => {
    const { original, id: rowId } = row;
    const { purpose: type, id, name, expenses_export_link: expensesExportLink, policies } = original;
    const constraintsApplied = !isEmptyArray(policies) && policies.some(({ active }) => active);

    return (
      <div style={{ display: "flex", alignItems: "center" }}>
        <Expander row={row} />
        <PoolLabel disableLink type={type} name={name} dataTestId={`link_pool_${rowId}`} />
        {!!expensesExportLink && (
          <span
            onClick={(e) => {
              e.stopPropagation();
              onExpensesExportClick(id);
            }}
            style={{ cursor: "pointer" }}
          >
            <Icon icon={LinkOutlinedIcon} hasLeftMargin tooltip={{ show: true, messageId: "thisPoolIsShared" }} />
          </span>
        )}
        {constraintsApplied && (
          <>
            &nbsp;
            <Link
              sx={{ cursor: "pointer", display: "flex" }}
              onClick={(e) => {
                e.stopPropagation();
                onConstraintsClick(id);
              }}
            >
              <Tooltip title={<FormattedMessage id="constraintsApplied" />}>
                <PriorityHighOutlinedIcon fontSize="inherit" />
              </Tooltip>
            </Link>
          </>
        )}
      </div>
    );
  },
  style: {
    whiteSpace: "nowrap"
  },
  enableHiding: false
});

export default poolName;
