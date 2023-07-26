import React from "react";
import Employees from "components/Employees";
import { KINDS } from "stories";

export default {
  title: `${KINDS.PAGES}/Employees`,
  argTypes: {
    isLoading: { name: "Loading", control: "boolean", defaultValue: false }
  }
};

const employees = [
  {
    name: "Kate Skywalker",
    user_email: "kskywalker@sunflower.demo",
    slack_connected: true,
    assignments: [
      {
        assignment_resource_id: "3cdb43e6-33b3-433e-b32e-fb2052225253",
        role_name: "Manager",
        assignment_resource_name: "Engineering",
        assignment_resource_type: "pool",
        assignment_resource_purpose: "business_unit",
        assignment_id: "852fc65c-235d-4b78-87cb-05b55a0e24ec",
        purpose: "optscale_manager"
      }
    ]
  },
  {
    name: "Joe Smith",
    user_email: "jsmith@sunflower.demo",
    assignments: [
      {
        assignment_resource_id: "47d7f743-de27-421b-b1e0-db8172078b34",
        role_name: "Engineer",
        assignment_resource_name: "QA",
        assignment_resource_type: "pool",
        assignment_resource_purpose: "team",
        assignment_id: "979ceeee-df04-44f7-902d-38107fc308b3",
        purpose: "optscale_engineer"
      }
    ]
  },
  {
    name: "Cooper Foster",
    user_email: "cfoster@sunflower.demo",
    slack_connected: true,
    assignments: [
      {
        assignment_resource_id: "46aae007-0443-4509-9f58-ccb03ea5e35c",
        role_name: "Manager",
        assignment_resource_name: "Sunflower Inc",
        assignment_resource_type: "organization",
        assignment_resource_purpose: "business_unit",
        assignment_id: "0a8c9f17-2b31-445b-bead-f5d37db9279b",
        purpose: "optscale_manager"
      }
    ]
  },
  {
    name: "Jack Jackson",
    slack_connected: true,
    user_email: "jjackson@sunflower.demo",
    assignments: [
      {
        assignment_resource_id: "46aae007-0443-4509-9f58-ccb03ea5e35c",
        role_name: "Manager",
        assignment_resource_name: "Sunflower Inc",
        assignment_resource_type: "organization",
        assignment_resource_purpose: "business_unit",
        assignment_id: "ec269aa8-66b3-4bf2-b7ae-ee1fd28206ae",
        purpose: "optscale_manager"
      }
    ]
  },
  {
    name: "Edwin Hamilton",
    user_email: "ehamilton@sunflower.demo",
    assignments: [
      {
        assignment_resource_id: "0f632e0f-41f6-408d-ba17-85de7e5a2177",
        role_name: "Engineer",
        assignment_resource_name: "Daily checks",
        assignment_resource_type: "pool",
        assignment_resource_purpose: "cicd",
        assignment_id: "d8e3b4cb-b265-4c81-a402-5d9228faba8f",
        purpose: "optscale_engineer"
      }
    ]
  },
  {
    name: "Homer Bond",
    user_email: "hbond@sunflower.demo",
    slack_connected: true,
    assignments: [
      {
        assignment_resource_id: "fda11011-f431-44db-bf88-a12438fb4cfb",
        role_name: "Manager",
        assignment_resource_name: "Sunflower Inc",
        assignment_resource_type: "pool",
        assignment_resource_purpose: "business_unit",
        assignment_id: "5c9e2934-7498-4237-9387-8204eac67031",
        purpose: "optscale_manager"
      }
    ]
  },
  {
    name: "Demo User",
    user_email: "duser@sunflower.demo",
    slack_connected: true,
    assignments: [
      {
        assignment_resource_id: "46aae007-0443-4509-9f58-ccb03ea5e35c",
        role_name: "Manager",
        assignment_resource_name: "Sunflower Inc",
        assignment_resource_type: "organization",
        assignment_resource_purpose: "business_unit",
        assignment_id: "b2274025-687b-464a-970e-63d3f9c91288",
        purpose: "optscale_manager"
      }
    ]
  },
  {
    name: "Evelyn Roy",
    user_email: "eroy@sunflower.demo",
    assignments: [
      {
        assignment_resource_id: "46aae007-0443-4509-9f58-ccb03ea5e35c",
        role_name: "Manager",
        assignment_resource_name: "Sunflower Inc",
        assignment_resource_type: "organization",
        assignment_resource_purpose: "business_unit",
        assignment_id: "e4153812-4ea4-4552-a16d-755f6ede31e8",
        purpose: "optscale_manager"
      }
    ]
  },
  {
    name: "Cody Potter",
    user_email: "cpotter@sunflower.demo",
    assignments: [
      {
        assignment_resource_id: "a4e6cb74-4c82-4403-a192-c62eb5466295",
        role_name: "Engineer",
        assignment_resource_name: "Dev",
        assignment_resource_type: "pool",
        assignment_resource_purpose: "team",
        assignment_id: "9a0228df-3583-417e-8031-e766266d08b3",
        purpose: "optscale_engineer"
      }
    ]
  },
  {
    name: "Julian Thomas",
    user_email: "jthomas@sunflower.demo",
    assignments: [
      {
        assignment_resource_id: "fda11011-f431-44db-bf88-a12438fb4cfb",
        role_name: "Manager",
        assignment_resource_name: "Sunflower Inc",
        assignment_resource_type: "pool",
        assignment_resource_purpose: "business_unit",
        assignment_id: "052bb832-e20d-413c-8e20-d3d58e04a45b",
        purpose: "optscale_manager"
      }
    ]
  },
  {
    name: "Amelia Swan",
    user_email: "aswan@sunflower.demo",
    assignments: [
      {
        assignment_resource_id: "46aae007-0443-4509-9f58-ccb03ea5e35c",
        role_name: "Manager",
        assignment_resource_name: "Sunflower Inc",
        assignment_resource_type: "organization",
        assignment_resource_purpose: "business_unit",
        assignment_id: "28d03f6b-32e4-4ca9-88e4-7f828a2174ae",
        purpose: "optscale_manager"
      }
    ]
  },
  {
    name: "Addison Davis",
    user_email: "adavis@sunflower.demo",
    assignments: [
      {
        assignment_resource_id: "46aae007-0443-4509-9f58-ccb03ea5e35c",
        role_name: "Manager",
        assignment_resource_name: "Sunflower Inc",
        assignment_resource_type: "organization",
        assignment_resource_purpose: "business_unit",
        assignment_id: "c4816d67-f752-47ec-8e88-f1447b39e9b7",
        purpose: "optscale_manager"
      }
    ]
  },
  {
    name: "William Murphy",
    user_email: "wmurphy@sunflower.demo",
    assignments: [
      {
        assignment_resource_id: "46aae007-0443-4509-9f58-ccb03ea5e35c",
        role_name: "Manager",
        assignment_resource_name: "Sunflower Inc",
        assignment_resource_type: "organization",
        assignment_resource_purpose: "business_unit",
        assignment_id: "c78ccaf7-8f05-40bd-94ce-5cf4debe9ddd",
        purpose: "optscale_manager"
      }
    ]
  },
  {
    name: "Emmett Wilson",
    user_email: "ewilson@sunflower.demo",
    assignments: [
      {
        assignment_resource_id: "46aae007-0443-4509-9f58-ccb03ea5e35c",
        role_name: "Manager",
        assignment_resource_name: "Sunflower Inc",
        assignment_resource_type: "organization",
        assignment_resource_purpose: "business_unit",
        assignment_id: "28e5d374-3cca-4a36-a7d3-dff98e83f465",
        purpose: "optscale_manager"
      }
    ]
  }
];

export const basic = (args) => <Employees employees={employees} isLoading={args.isLoading} />;
