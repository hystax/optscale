import { millisecondsToSeconds, subHours } from "utils/datetime";
import PowerSchedules from "./PowerSchedules";

const PowerSchedulesMocked = () => (
  <PowerSchedules
    powerSchedules={[
      {
        id: "1",
        organization_id: "1",
        name: "dev-schedule",
        enabled: true,
        triggers: [
          { action: "power_on", time: "00:00" },
          { action: "power_off", time: "02:00" },
          { action: "power_on", time: "04:00" },
          { action: "power_off", time: "06:00" },
          { action: "power_on", time: "08:00" },
          { action: "power_off", time: "10:00" },
          { action: "power_on", time: "12:00" },
          { action: "power_off", time: "14:00" },
        ],
        timezone: "Europe/Vienna",
        start_date: 1696912229,
        end_date: 1697274449,
        last_run: millisecondsToSeconds(subHours(new Date(), 4)),
        last_run_error: null,
        created_at: 1696912229,
        deleted_at: 0,
        resources_count: 23,
      },
      {
        id: "2",
        organization_id: "1",
        name: "qa-schedule",
        enabled: true,
        triggers: [
          { action: "power_on", time: "07:00" },
          { action: "power_off", time: "19:00" },
        ],
        timezone: "Europe/Vienna",
        start_date: 1696912229,
        end_date: null,
        last_run: millisecondsToSeconds(subHours(new Date(), 6)),
        last_run_error: null,
        created_at: 1696912229,
        deleted_at: 0,
        resources_count: 5,
      },
      {
        id: "3",
        organization_id: "1",
        name: "ML Instances",
        enabled: true,
        triggers: [
          { action: "power_on", time: "06:00" },
          { action: "power_off", time: "09:00" },
          { action: "power_on", time: "12:00" },
          { action: "power_off", time: "15:00" },
          { action: "power_on", time: "18:00" },
          { action: "power_off", time: "21:00" },
        ],
        timezone: "Europe/Vienna",
        start_date: null,
        end_date: 1697114449,
        last_run: 0,
        last_run_error: null,
        created_at: 1696912229,
        deleted_at: 0,
        resources_count: 12,
      },
      {
        id: "4",
        organization_id: "1",
        name: "Server Maintenance",
        enabled: true,
        triggers: [
          { action: "power_off", time: "03:00" },
          { action: "power_on", time: "04:00" },
        ],
        timezone: "Europe/Vienna",
        start_date: null,
        end_date: null,
        last_run: 0,
        last_run_error: null,
        created_at: 1696912229,
        deleted_at: 0,
        resources_count: 2,
      },
    ]}
    onActivate={() => {}}
    onDeactivate={() => {}}
  />
);

export default PowerSchedulesMocked;
