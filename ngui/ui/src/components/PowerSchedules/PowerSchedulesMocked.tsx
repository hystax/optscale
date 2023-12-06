import { millisecondsToSeconds, subHours } from "utils/datetime";
import PowerSchedules from "./PowerSchedules";

const PowerSchedulesMocked = () => (
  <PowerSchedules
    powerSchedules={[
      {
        id: "1",
        organization_id: "1",
        name: "dev-schedule",
        power_on: "8:00",
        power_off: "19:00",
        enabled: true,
        timezone: "Europe/Vienna",
        start_date: 1696912229,
        end_date: 1697274449,
        last_run: millisecondsToSeconds(subHours(new Date(), 4)),
        last_run_error: null,
        created_at: 1696912229,
        deleted_at: 0,
        resources_count: 23
      },
      {
        id: "2",
        organization_id: "1",
        name: "qa-schedule",
        power_on: "18:00",
        power_off: "8:00",
        enabled: true,
        timezone: "Europe/Vienna",
        start_date: 1696912229,
        end_date: null,
        last_run: millisecondsToSeconds(subHours(new Date(), 6)),
        last_run_error: null,
        created_at: 1696912229,
        deleted_at: 0,
        resources_count: 5
      },
      {
        id: "3",
        organization_id: "1",
        name: "ML Instances",
        power_on: "10:00",
        power_off: "20:00",
        enabled: true,
        timezone: "Europe/Vienna",
        start_date: null,
        end_date: 1697114449,
        last_run: 0,
        last_run_error: null,
        created_at: 1696912229,
        deleted_at: 0,
        resources_count: 12
      },
      {
        id: "4",
        organization_id: "1",
        name: "Server Maintenance",
        power_on: "01:00",
        power_off: "02:00",
        enabled: true,
        timezone: "Europe/Vienna",
        start_date: null,
        end_date: null,
        last_run: 0,
        last_run_error: null,
        created_at: 1696912229,
        deleted_at: 0,
        resources_count: 2
      }
    ]}
    onActivate={() => {}}
    onDeactivate={() => {}}
  />
);

export default PowerSchedulesMocked;
