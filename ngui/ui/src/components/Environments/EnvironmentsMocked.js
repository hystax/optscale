import React from "react";
import { ENVIRONMENT_SOFTWARE_FIELD, ENVIRONMENT_JIRA_TICKETS_FIELD } from "utils/constants";
import Environments from "./Environments";

const liveDemoData = [
  {
    name: "dev-1",
    resource_type: "QA stand",
    cloud_resource_id: "environment_8778ced8a4d4d009fc1daf09a1b26a64",
    cloud_account_id: "9be18397-16d0-4a53-af9f-e363ee5fdd9f",
    region: null,
    is_environment: true,
    active: true,
    employee_id: "e584b198-1689-49f3-a014-18c56978d12e",
    pool_id: "3ca27b87-a5a9-4994-8965-a92955716e5a",
    applied_rules: [
      {
        id: "5dcc90a7-8923-4530-9fdd-891ea66ae1d1",
        name: "Rule for Environment_1629717445",
        pool_id: "3f6aa54c-bc90-4145-b351-34284bd5c4cd"
      }
    ],
    first_seen: 1629676800,
    tags: {},
    env_properties: {
      [ENVIRONMENT_SOFTWARE_FIELD]: "SunWare 1.3.423-integration",
      [ENVIRONMENT_JIRA_TICKETS_FIELD]:
        "[NGUI-1242](https://jira.com.example/NGUI-1242)  \n[NGUI-3214](jira.com.example/NGUI-3214)"
    },
    shareable: true,
    created_at: 1629787458,
    last_seen: 1632896806,
    deleted_at: 0,
    shareable_bookings: [
      {
        deleted_at: 0,
        id: "5b6154d4-7725-4b28-8852-1941607bdf60",
        created_at: 1630560121,
        resource_id: "efd9cb03-5e14-4222-bc59-2e55dfaff985",
        organization_id: "a54d9db6-9da0-481a-b0c9-0d7e31ba2085",
        acquired_since: 1632290486,
        released_at: 0,
        acquired_by: {
          id: "58f99e3b-a480-4e12-944d-d0d91b260407",
          name: "William Williams"
        }
      }
    ],
    id: "efd9cb03-5e14-4222-bc59-2e55dfaff985",
    meta: {},
    cloud_console_link: null,
    sub_resources: [],
    recommendations: {},
    dismissed_recommendations: {},
    dismissed: [],
    cloud_account_name: "Environment",
    cloud_account_type: "environment",
    pool_name: "Environment",
    pool_purpose: "budget"
  },
  {
    name: "feature-1",
    resource_type: "Dev stand",
    cloud_resource_id: "environment_b79a445f910e942147757b1cabb5b84f",
    cloud_account_id: "9be18397-16d0-4a53-af9f-e363ee5fdd9f",
    region: null,
    is_environment: true,
    active: true,
    employee_id: "e584b198-1689-49f3-a014-18c56978d12e",
    pool_id: "3ca27b87-a5a9-4994-8965-a92955716e5a",
    applied_rules: [
      {
        id: "5dcc90a7-8923-4530-9fdd-891ea66ae1d1",
        name: "Rule for Environment_1629717445",
        pool_id: "3f6aa54c-bc90-4145-b351-34284bd5c4cd"
      }
    ],
    first_seen: 1629676800,
    tags: {},
    shareable: true,
    env_properties: {
      [ENVIRONMENT_SOFTWARE_FIELD]: "SunWare 1.3.232-hotfix/support-fix",
      [ENVIRONMENT_JIRA_TICKETS_FIELD]: "[TCS-2214](https://jira.com.example/TCS-2214)"
    },
    created_at: 1629787513,
    last_seen: 1632896806,
    deleted_at: 0,
    shareable_bookings: [
      {
        deleted_at: 0,
        id: "19df3e91-d76f-416b-b1a1-20269f609bdd",
        created_at: 1630562680,
        resource_id: "6b9a6d53-5131-4431-a0b8-8077ca713914",
        organization_id: "a54d9db6-9da0-481a-b0c9-0d7e31ba2085",
        acquired_since: 1633452527,
        released_at: 0,
        acquired_by: {
          id: "58f99e3b-a480-4e12-944d-d0d91b260407",
          name: "William Williams"
        }
      }
    ],
    id: "6b9a6d53-5131-4431-a0b8-8077ca713914",
    meta: {},
    cloud_console_link: null,
    sub_resources: [],
    recommendations: {},
    dismissed_recommendations: {},
    dismissed: [],
    cloud_account_name: "Environment",
    cloud_account_type: "environment",
    pool_name: "Environment",
    pool_purpose: "budget"
  },
  {
    name: "dev-2",
    resource_type: "QA stand",
    cloud_resource_id: "environment_ebff946b5681ea9aa4785f2d719b768e",
    cloud_account_id: "9be18397-16d0-4a53-af9f-e363ee5fdd9f",
    region: null,
    is_environment: true,
    active: true,
    employee_id: "e584b198-1689-49f3-a014-18c56978d12e",
    pool_id: "3ca27b87-a5a9-4994-8965-a92955716e5a",
    applied_rules: [
      {
        id: "5dcc90a7-8923-4530-9fdd-891ea66ae1d1",
        name: "Rule for Environment_1629717445",
        pool_id: "3f6aa54c-bc90-4145-b351-34284bd5c4cd"
      }
    ],
    first_seen: 1629676800,
    tags: {},
    shareable: true,
    env_properties: {
      [ENVIRONMENT_SOFTWARE_FIELD]: "SunWare 1.3.424-feature/sunrise_control",
      [ENVIRONMENT_JIRA_TICKETS_FIELD]:
        "[TCS-1674](https://jira.com.example/TCS-1674)  \n[TCS-2161](https://jira.com.example/TCS-2161)"
    },
    created_at: 1629787475,
    last_seen: 1632896806,
    deleted_at: 0,
    shareable_bookings: [
      {
        deleted_at: 0,
        id: "83ce057e-7c61-4330-ad5d-7b61ab516ba1",
        created_at: 1630560144,
        resource_id: "b4053a50-13ab-4d7d-8279-537a2e5a5614",
        organization_id: "a54d9db6-9da0-481a-b0c9-0d7e31ba2085",
        acquired_since: 1632290463,
        released_at: 1633023063,
        acquired_by: {
          id: "58f99e3b-a480-4e12-944d-d0d91b260407",
          name: "William Williams"
        }
      },
      {
        deleted_at: 0,
        id: "c792afd7-abfe-4d63-802e-e41b2571c3da",
        created_at: 1630562711,
        resource_id: "b4053a50-13ab-4d7d-8279-537a2e5a5614",
        organization_id: "a54d9db6-9da0-481a-b0c9-0d7e31ba2085",
        acquired_since: 1633884496,
        released_at: 1633970896,
        acquired_by: {
          id: "58f99e3b-a480-4e12-944d-d0d91b260407",
          name: "William Williams"
        }
      }
    ],
    id: "b4053a50-13ab-4d7d-8279-537a2e5a5614",
    meta: {},
    cloud_console_link: null,
    sub_resources: [],
    recommendations: {},
    dismissed_recommendations: {},
    dismissed: [],
    cloud_account_name: "Environment",
    cloud_account_type: "environment",
    pool_name: "Environment",
    pool_purpose: "budget"
  },
  {
    name: "pre-release",
    resource_type: "QA stand",
    cloud_resource_id: "environment_6d273a1175ba5916eae2b4f6708b21d6",
    cloud_account_id: "9be18397-16d0-4a53-af9f-e363ee5fdd9f",
    region: null,
    is_environment: true,
    active: true,
    employee_id: "e584b198-1689-49f3-a014-18c56978d12e",
    pool_id: "3ca27b87-a5a9-4994-8965-a92955716e5a",
    applied_rules: [
      {
        id: "5dcc90a7-8923-4530-9fdd-891ea66ae1d1",
        name: "Rule for Environment_1629717445",
        pool_id: "3f6aa54c-bc90-4145-b351-34284bd5c4cd"
      }
    ],
    first_seen: 1629676800,
    tags: {},
    shareable: true,
    env_properties: {
      [ENVIRONMENT_SOFTWARE_FIELD]: "SunWare 1.2.161-master",
      [ENVIRONMENT_JIRA_TICKETS_FIELD]: "[QA-617](https://jira.com.example/QA-617)"
    },
    created_at: 1629787492,
    last_seen: 1632896806,
    deleted_at: 0,
    shareable_bookings: [],
    id: "d33c940d-dba0-472b-a4ef-4c0fdc84492d",
    meta: {},
    cloud_console_link: null,
    sub_resources: [],
    recommendations: {},
    dismissed_recommendations: {},
    dismissed: [],
    cloud_account_name: "Environment",
    cloud_account_type: "environment",
    pool_name: "Environment",
    pool_purpose: "budget"
  },
  {
    name: "feature-2",
    resource_type: "Dev stand",
    cloud_resource_id: "environment_1d140fbc9f902a8608a51307e4d0612b",
    cloud_account_id: "9be18397-16d0-4a53-af9f-e363ee5fdd9f",
    region: null,
    is_environment: true,
    active: true,
    employee_id: "e584b198-1689-49f3-a014-18c56978d12e",
    pool_id: "3ca27b87-a5a9-4994-8965-a92955716e5a",
    applied_rules: [
      {
        id: "5dcc90a7-8923-4530-9fdd-891ea66ae1d1",
        name: "Rule for Environment_1629717445",
        pool_id: "3f6aa54c-bc90-4145-b351-34284bd5c4cd"
      }
    ],
    first_seen: 1629676800,
    tags: {},
    shareable: true,
    env_properties: {
      [ENVIRONMENT_SOFTWARE_FIELD]: "SunWare 1.2.162-master",
      [ENVIRONMENT_JIRA_TICKETS_FIELD]:
        "[NGUI-2617](https://jira.com.example/NGUI-2617)  \n[NGUI-2600](https://jira.com.example/NGUI-2600)  \n[NGUI-2620](https://jira.com.example/NGUI-2620)  \n[TCS-1355](https://jira.com.example/TCS-1355)  \n[TCS-1558](https://jira.com.example/TCS-1558)"
    },
    created_at: 1629787527,
    last_seen: 1632896806,
    deleted_at: 0,
    shareable_bookings: [],
    id: "f432f6da-8a61-45ed-9f77-423135cdaf5a",
    meta: {},
    cloud_console_link: null,
    sub_resources: [],
    recommendations: {},
    dismissed_recommendations: {},
    dismissed: [],
    cloud_account_name: "Environment",
    cloud_account_type: "environment",
    pool_name: "Environment",
    pool_purpose: "budget"
  }
];

const EnvironmentsMocked = () => <Environments disableFilters environments={liveDemoData} />;

export default EnvironmentsMocked;
