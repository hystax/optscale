import { useMemo } from "react";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import ManageSearchOutlinedIcon from "@mui/icons-material/ManageSearchOutlined";
import { Typography } from "@mui/material";
import { Stack } from "@mui/system";
import { FormattedMessage } from "react-intl";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import CreateColumnSetFormContainer from "containers/CreateColumnSetFormContainer";
import { SPACING_1 } from "utils/layouts";

type ColumnSetsProps = {
  columnSets: object[];
  // TODO TS: Define proper type for table context
  tableContext: unknown;
  onApply: (columnSetId: string) => Promise<unknown>;
  onDelete: (columnSetId: string) => Promise<unknown>;
  isLoadingProps: {
    isGetAllColumnSetsLoading: boolean;
    getIsGetColumnSetLoading: (columnSetId: string) => boolean;
    getIsDeleteColumnSetLoading: (columnSetId: string) => boolean;
  };
};

const ColumnSets = ({ columnSets, tableContext, onApply, onDelete, isLoadingProps }: ColumnSetsProps) => {
  const { isGetAllColumnSetsLoading = false, getIsGetColumnSetLoading, getIsDeleteColumnSetLoading } = isLoadingProps;

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessorKey: "name"
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_actions">
            <FormattedMessage id="actions" />
          </TextWithDataTestId>
        ),
        id: "actions",
        cell: ({ row: { original } }) => {
          const { id } = original;

          return (
            <TableCellActions
              items={[
                {
                  key: "apply",
                  messageId: "apply",
                  icon: <ManageSearchOutlinedIcon />,
                  isLoading: getIsGetColumnSetLoading(id),
                  action: () => onApply(id)
                },
                {
                  key: "delete",
                  messageId: "delete",
                  color: "error",
                  icon: <DeleteOutlinedIcon />,
                  isLoading: getIsDeleteColumnSetLoading(id),
                  action: () => onDelete(id)
                }
              ]}
            />
          );
        }
      }
    ],
    [getIsDeleteColumnSetLoading, getIsGetColumnSetLoading, onApply, onDelete]
  );

  return (
    <Stack spacing={SPACING_1}>
      <div>
        <Typography gutterBottom>
          <FormattedMessage id="columnSetsDescription" />
        </Typography>
        <CreateColumnSetFormContainer tableContext={tableContext} />
      </div>
      <div>
        {isGetAllColumnSetsLoading ? (
          <TableLoader columnsCounter={1} />
        ) : (
          <Table
            data={columnSets}
            columns={columns}
            pageSize={5}
            withSearch
            enableSearchQueryParam={false}
            enablePaginationQueryParam={false}
            localization={{
              emptyMessageId: "noSets"
            }}
          />
        )}
      </div>
    </Stack>
  );
};

export default ColumnSets;
