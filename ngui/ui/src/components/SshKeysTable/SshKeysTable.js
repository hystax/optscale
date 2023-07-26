import React, { useMemo } from "react";
import BookmarkIcon from "@mui/icons-material/Bookmark";
import BookmarkBorderOutlinedIcon from "@mui/icons-material/BookmarkBorderOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import { Box } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { DeleteSshKeyModal } from "components/SideModalManager/SideModals";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { SPACING_4 } from "utils/layouts";

const SshKeysTable = ({ isLoading, sshKeys = [], isMakeDefaultLoading, onMakeDefault }) => {
  const openSideModal = useOpenSideModal();

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessorKey: "name",
        defaultSort: "asc"
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_fingerprint">
            <FormattedMessage id="fingerprint" />
          </TextWithDataTestId>
        ),
        accessorKey: "fingerprint"
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_actions">
            <FormattedMessage id="actions" />
          </TextWithDataTestId>
        ),
        id: "actions",
        enableSorting: false,
        cell: ({ row: { original: { id: keyId, default: isDefault } = {}, index } }) => (
          <TableCellActions
            items={[
              {
                key: "default",
                messageId: isDefault ? "thisIsDefaultKey" : "makeDefault",
                icon: isDefault ? <BookmarkIcon /> : <BookmarkBorderOutlinedIcon />,
                dataTestId: `btn_default_${index}`,
                action: !isDefault && typeof onMakeDefault === "function" ? () => onMakeDefault(keyId) : undefined,
                disabled: isDefault,
                isLoading: isMakeDefaultLoading
              },
              {
                key: "delete",
                messageId: "delete",
                icon: <DeleteOutlinedIcon />,
                color: "error",
                dataTestId: `btn_delete_${index}`,
                action: () => openSideModal(DeleteSshKeyModal, { keyToDeleteId: keyId, sshKeys }),
                isLoading: isMakeDefaultLoading
              }
            ]}
          />
        )
      }
    ],
    [isMakeDefaultLoading, onMakeDefault, openSideModal, sshKeys]
  );

  const data = useMemo(() => sshKeys, [sshKeys]);

  return isLoading ? (
    <TableLoader columnsCounter={columns.length} showHeader />
  ) : (
    <Box mt={SPACING_4}>
      <Table
        data={data}
        localization={{
          emptyMessageId: "noKeys"
        }}
        counters={{
          showCounters: true,
          hideDisplayed: true
        }}
        columns={columns}
        dataTestIds={{
          container: "table_ssh_keys"
        }}
        withSearch
      />
    </Box>
  );
};

SshKeysTable.propTypes = {
  sshKeys: PropTypes.array.isRequired,
  isLoading: PropTypes.bool,
  isMakeDefaultLoading: PropTypes.bool,
  onMakeDefault: PropTypes.func
};

export default SshKeysTable;
