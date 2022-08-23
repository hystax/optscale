import React, { useMemo } from "react";
import Skeleton from "@mui/material/Skeleton";
import { useTheme } from "@mui/material/styles";
import PropTypes from "prop-types";
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
        Header: <TextWithDataTestId messageId="type" dataTestId="lbl_type" />,
        accessor: "type",
        Cell: ({ cell: { value } }) => <FormattedMessage id={CONSTRAINTS_TYPES[value]} />
      },
      {
        Header: <TextWithDataTestId messageId="scope" dataTestId="lbl_scope" />,
        id: "scope",
        Cell: ({ row: { original } }) =>
          original.pool_id ? <FormattedMessage id="poolPolicy" /> : <FormattedMessage id="resourceSpecific" />
      },
      {
        Header: <TextWithDataTestId messageId="event" dataTestId="lbl_event" />,
        id: "event",
        Cell: ({ row: { original } }) => <ResourceLimitHitEvent state={original.state} />
      },
      {
        Header: <TextWithDataTestId messageId="limit" dataTestId="lbl_limit" />,
        accessor: "constraint_limit",
        Cell: ({ row: { original } }) => <ConstraintLimitMessage limit={original.constraint_limit} type={original.type} />
      },
      {
        Header: <TextWithDataTestId messageId="value" dataTestId="lbl_value" />,
        id: "hit_value",
        Cell: ({ row: { original } }) => (
          <ConstraintHitMessage limit={getResourceLimitHitValue(original)} type={original.type} />
        )
      },
      {
        Header: <TextWithDataTestId messageId="time" dataTestId="lbl_time" />,
        accessor: "time",
        defaultSort: "desc",
        Cell: ({ cell: { value } }) => format(secondsToMilliseconds(value), EN_FULL_FORMAT)
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
        />
      </>
    )
  );
};

ResourceLimitHits.propTypes = {
  limitHits: PropTypes.array,
  isLoading: PropTypes.bool
};

export default ResourceLimitHits;
