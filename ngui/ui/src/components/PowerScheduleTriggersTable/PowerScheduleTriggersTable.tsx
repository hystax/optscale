import { useMemo } from "react";
import PowerSettingsNewOutlinedIcon from "@mui/icons-material/PowerSettingsNewOutlined";
import { FormattedMessage } from "react-intl";
import IconLabel from "components/IconLabel";
import PageContentDescription from "components/PageContentDescription";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { POWER_SCHEDULE_ACTIONS } from "utils/constants";
import { EN_TIME_FORMAT, EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM, formatTimeString } from "utils/datetime";
import { ObjectValues } from "utils/types";

type PowerAction = ObjectValues<typeof POWER_SCHEDULE_ACTIONS>;

type Trigger = {
  time: string;
  action: PowerAction;
};

type PowerScheduleTriggersTableProps = {
  triggers: Trigger[];
  isLoading?: boolean;
};

const PowerScheduleTriggersTable = ({ triggers = [], isLoading = false }: PowerScheduleTriggersTableProps) => {
  const tableData = useMemo(() => triggers, [triggers]);

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_time">
            <FormattedMessage id="time" />
          </TextWithDataTestId>
        ),
        accessorKey: "time",
        defaultSort: "asc",
        cell: ({ row: { original } }: { row: { original: Trigger } }) =>
          formatTimeString({
            timeString: original.time,
            timeStringFormat: EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM,
            parsedTimeStringFormat: EN_TIME_FORMAT,
          }),
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_state">
            <FormattedMessage id="state" />
          </TextWithDataTestId>
        ),
        accessorKey: "action",
        enableSorting: false,
        cell: ({ row: { original } }: { row: { original: Trigger } }) => {
          const isOn = original.action === POWER_SCHEDULE_ACTIONS.POWER_ON;

          return (
            <IconLabel
              icon={<PowerSettingsNewOutlinedIcon fontSize="small" color={isOn ? "success" : "error"} />}
              label={<FormattedMessage id={isOn ? "on" : "off"} />}
            />
          );
        },
      },
    ],
    []
  );

  return isLoading ? (
    <TableLoader columnsCounter={columns.length} showHeader />
  ) : (
    <>
      <Table
        data={tableData}
        columns={columns}
        localization={{
          emptyMessageId: "noTriggers",
        }}
        dataTestIds={{
          container: "table_triggers",
        }}
      />
      <PageContentDescription
        position="bottom"
        alertProps={{
          messageId: "triggersDescription",
          messageValues: {
            br: <br />,
          },
        }}
      />
    </>
  );
};

export default PowerScheduleTriggersTable;
