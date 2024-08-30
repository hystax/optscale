import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import FormattedMoney from "components/FormattedMoney";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useIsOptScaleModeEnabled } from "hooks/useIsOptScaleModeEnabled";
import { getMlRunsetTemplateUrl, ML_RUNSET_TEMPLATE_CREATE } from "urls";
import { mlRunsCount } from "utils/columns";
import { OPTSCALE_MODE } from "utils/constants";

const MlRunsetTemplatesTable = ({ data, isLoading }) => {
  const isFinOpsEnabled = useIsOptScaleModeEnabled(OPTSCALE_MODE.FINOPS);

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessorKey: "name",
        cell: ({
          cell,
          row: {
            original: { id }
          }
        }) => {
          const name = cell.getValue();

          return (
            <Link to={getMlRunsetTemplateUrl(id)} component={RouterLink}>
              {name}
            </Link>
          );
        }
      },
      mlRunsCount({
        accessorKey: "total_runs"
      }),
      ...(isFinOpsEnabled
        ? [
            {
              header: (
                <TextWithDataTestId dataTestId="lbl_last_runset_expenses">
                  <FormattedMessage id="lastRunsetExpenses" />
                </TextWithDataTestId>
              ),
              accessorKey: "last_runset_cost",
              cell: ({
                row: {
                  original: { last_runset_cost: lastRunsetExpenses }
                }
              }) => <FormattedMoney value={lastRunsetExpenses} />
            },
            {
              header: (
                <TextWithDataTestId dataTestId="lbl_expenses">
                  <FormattedMessage id="totalExpenses" />
                </TextWithDataTestId>
              ),
              accessorKey: "total_cost",
              cell: ({
                row: {
                  original: { total_cost: total }
                }
              }) => <FormattedMoney value={total} />
            }
          ]
        : [])
    ],
    [isFinOpsEnabled]
  );

  const tableActionBarDefinition = {
    show: true,
    definition: {
      items: [
        {
          key: "btn-create-runset-template",
          icon: <AddOutlinedIcon />,
          messageId: "add",
          color: "success",
          variant: "contained",
          type: "button",
          dataTestId: "btn-create-runset-template",
          link: ML_RUNSET_TEMPLATE_CREATE,
          requiredActions: ["EDIT_PARTNER"]
        }
      ]
    }
  };

  return (
    <>
      {isLoading ? (
        <TableLoader columnsCounter={columns.length} showHeader />
      ) : (
        <Table
          data={data}
          columns={columns}
          actionBar={tableActionBarDefinition}
          withSearch
          pageSize={50}
          localization={{ emptyMessageId: "noRunsetTemplates" }}
          counters={{
            showCounters: true
          }}
        />
      )}
    </>
  );
};

export default MlRunsetTemplatesTable;
