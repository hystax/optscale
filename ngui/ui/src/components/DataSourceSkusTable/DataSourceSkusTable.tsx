import { useMemo } from "react";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import StorageOutlinedIcon from "@mui/icons-material/StorageOutlined";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import IconLabel from "components/IconLabel";
import { UpdateDataSourceSkuModal } from "components/SideModalManager/SideModals";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import Tooltip from "components/Tooltip";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { FORMATTED_MONEY_TYPES, COST_MODEL_MONEY_MAXIMUM_FRACTION_DIGITS } from "utils/constants";

const DataSourceSkusTable = ({ dataSourceId, skus, usedSkus, costModel, isLoading = false }) => {
  const openSideModal = useOpenSideModal();

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_sku">
            <FormattedMessage id="sku" />
          </TextWithDataTestId>
        ),
        accessorKey: "sku",
        cell: ({ cell }) => {
          const sku = cell.getValue();
          const isInUse = usedSkus.includes(sku);

          return isInUse ? (
            <IconLabel
              endIcon={
                <Tooltip title={<FormattedMessage id="inUse" />} placement="top">
                  <StorageOutlinedIcon fontSize="small" />
                </Tooltip>
              }
              label={sku}
            />
          ) : (
            sku
          );
        },
        defaultSort: "asc"
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_cost">
            <FormattedMessage id="cost" />
          </TextWithDataTestId>
        ),
        accessorKey: "cost",
        cell: ({ cell }) => (
          <FormattedMoney
            type={FORMATTED_MONEY_TYPES.TINY}
            maximumFractionDigits={COST_MODEL_MONEY_MAXIMUM_FRACTION_DIGITS}
            value={cell.getValue()}
          />
        )
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_actions">
            <FormattedMessage id="actions" />
          </TextWithDataTestId>
        ),
        id: "actions",
        cell: ({ row: { original } }) => {
          const { sku, cost } = original;
          return (
            <TableCellActions
              items={[
                {
                  key: "edit",
                  messageId: "edit",
                  icon: <EditOutlinedIcon />,
                  requiredActions: ["MANAGE_CLOUD_CREDENTIALS"],
                  action: () => openSideModal(UpdateDataSourceSkuModal, { sku, cost, dataSourceId, costModel })
                }
              ]}
            />
          );
        }
      }
    ],
    [usedSkus, openSideModal, dataSourceId, costModel]
  );

  const tableData = useMemo(() => skus, [skus]);

  return isLoading ? <TableLoader /> : <Table data={tableData} columns={columns} />;
};

export default DataSourceSkusTable;
