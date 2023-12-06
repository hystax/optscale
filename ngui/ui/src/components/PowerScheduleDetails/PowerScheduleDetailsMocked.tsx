import PowerScheduleDetails from "./PowerScheduleDetails";

const PowerScheduleDetailsMocked = () => (
  <PowerScheduleDetails
    powerSchedule={{
      id: "1",
      organization_id: "1",
      name: "dev-schedule",
      power_on: "8:00",
      power_off: "19:00",
      enabled: true,
      timezone: "Europe/Vienna",
      start_date: 1696912229,
      end_date: 1697274449,
      last_run: 0,
      last_run_error: null,
      created_at: 1696912229,
      deleted_at: 0,
      resources_count: 1,
      resources: [
        {
          name: "dev-1",
          resource_type: "Instance",
          cloud_resource_id: "environment_8778ced8a4d4d009fc1daf09a1b26a64",
          cloud_account_id: "31eebb02-f100-49ba-9de9-2c703fe14f5a",
          region: null,
          is_environment: true,
          active: true,
          shareable: true,
          ssh_only: false,
          created_at: 1680762726,
          deleted_at: 0,
          employee_id: "02398865-30b4-43e1-b421-68158e4b6638",
          pool_id: "24d45f81-6b73-4f66-a876-0bc15e1077a3",
          applied_rules: [
            {
              id: "f7743a69-878e-49e6-854a-c1ba2ad37be4",
              name: "Rule for Environment_1680762725",
              pool_id: "24d45f81-6b73-4f66-a876-0bc15e1077a3"
            }
          ],
          first_seen: 1680739200,
          last_seen: 1697068799,
          tags: {
            purpose: "dev"
          },
          last_expense: {
            date: 1696982400,
            cost: 0.052057672081999996
          },
          total_cost: 46.908893672082,
          constraint_violated: true,
          id: "665bc613-2421-4812-8fee-e204e363af9f",
          meta: {
            flavor: "xlarge"
          },
          sub_resources: [],
          recommendations: {},
          dismissed_recommendations: {},
          dismissed: [],
          cloud_account_name: "AWS",
          cloud_account_type: "aws_cnr",
          owner_name: "Sally wong",
          pool_name: "Environment",
          pool_purpose: "budget"
        }
      ]
    }}
    onActivate={() => {}}
    onDeactivate={() => {}}
  />
);

export default PowerScheduleDetailsMocked;
