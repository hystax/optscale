import { useMemo } from "react";
import Skeleton from "@mui/material/Skeleton";
import { useTheme } from "@mui/material/styles";
import { FormattedMessage } from "react-intl";
import { ConstraintLimitMessage, ConstraintHitMessage } from "components/ConstraintMessage";
import ResourceLimitHitEvent from "components/ResourceLimitHitEvent";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { isEmpty } from "utils/arrays";
import { CONSTRAINTS_TYPES, isExpensesLimit, isTtlLimit } from "utils/constraints";
import { format, EN_FULL_FORMAT, secondsToMilliseconds } from "utils/datetime";

const ResourceLimitHits = ({ limitHits, isLoading }) => {
  const theme = useTheme();

  const data = useMemo(() => limitHits, [limitHits]);

  const columns = useMemo(() => {
    const getResourceLimitHitValue = (limitHit) => {
      const { type: limitHitType } = limitHit;
      if (isExpensesLimit(limitHitType)) {
        return limitHit.expense_value;
      }
      if (isTtlLimit(limitHitType)) {
        return limitHit.ttl_value;
      }
      return undefined;
    };

    return [
      {
        header: <TextWithDataTestId messageId="type" dataTestId="lbl_type" />,
        accessorKey: "type",
        cell: ({ cell }) => <FormattedMessage id={CONSTRAINTS_TYPES[cell.getValue()]} />
      },
      {
        header: <TextWithDataTestId messageId="scope" dataTestId="lbl_scope" />,
        id: "scope",
        cell: ({ row: { original } }) =>
          original.pool_id ? <FormattedMessage id="poolPolicy" /> : <FormattedMessage id="resourceSpecific" />
      },
      {
        header: <TextWithDataTestId messageId="event" dataTestId="lbl_event" />,
        id: "event",
        cell: ({ row: { original } }) => <ResourceLimitHitEvent state={original.state} />
      },
      {
        header: <TextWithDataTestId messageId="limit" dataTestId="lbl_limit" />,
        accessorKey: "constraint_limit",
        cell: ({ row: { original } }) => <ConstraintLimitMessage limit={original.constraint_limit} type={original.type} />
      },
      {
        header: <TextWithDataTestId messageId="value" dataTestId="lbl_value" />,
        id: "hit_value",
        cell: ({ row: { original } }) => (
          <ConstraintHitMessage limit={getResourceLimitHitValue(original)} type={original.type} />
        )
      },
      {
        header: <TextWithDataTestId messageId="time" dataTestId="lbl_time" />,
        accessorKey: "time",
        defaultSort: "desc",
        cell: ({ cell }) => format(secondsToMilliseconds(cell.getValue()), EN_FULL_FORMAT)
      }
    ];
  }, []);

  return isLoading ? (
    <>
      <Skeleton height={theme.spacing(5)} width={theme.spacing(30)} />
      <TableLoader columnsCounter={columns.length} showHeader />
    </>
  ) : (
    !isEmpty(data) && (
      <>
        <span data-test-id="p_constraints_table">
          <FormattedMessage id="resourceConstraintsStateHistory" />:
        </span>
        <Table
          dataTestIds={{
            container: "table_constraints"
          }}
          data={data}
          columns={columns}
          localization={{
            emptyMessageId: "noConstraintViolations"
          }}
          pageSize={50}
          queryParamPrefix="constraints"
        />
      </>
    )
  );
};

export default ResourceLimitHits;
