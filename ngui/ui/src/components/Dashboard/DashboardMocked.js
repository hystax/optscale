import React from "react";

import DashboardGridLayout from "components/DashboardGridLayout";
import EnvironmentsCard from "components/EnvironmentsCard";
import OrganizationExpenses from "components/OrganizationExpenses";
import PageContentWrapper from "components/PageContentWrapper";
import RecommendationsCard from "components/RecommendationsCard";
import TopResourcesExpensesCard from "components/TopResourcesExpensesCard";
import { MOCKED_ORGANIZATION_POOL_ID } from "stories";
import { getLastMonthRange, millisecondsToSeconds } from "utils/datetime";

const cleanExpenses = [
  {
    resource_id: "672211a0-d08e-452d-880f-7d815b3c4d48",
    _id: {
      resource_id: "672211a0-d08e-452d-880f-7d815b3c4d48"
    },
    resource_type: "Instance",
    active: false,
    pool: {
      purpose: "business_unit",
      id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
      name: "Engineering"
    },
    region: "eu-central-1",
    owner: {
      id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
      name: "Amy Smith"
    },
    cloud_account_type: "aws_cnr",
    service_name: "AmazonEC2",
    cloud_resource_id: "i-0307c865e6f4f379f",
    cloud_account_id: "8c63e980-6572-4b36-be82-a2bc59705888",
    cloud_account_name: "AWS HQ",
    resource_name: "sunflower-us-east-2",
    cost: 22.5719317827
  },
  {
    resource_id: "3dd84f76-b16b-48e1-a22b-a6078a1c4ba4",
    _id: {
      resource_id: "3dd84f76-b16b-48e1-a22b-a6078a1c4ba4"
    },
    resource_type: "Instance",
    active: true,
    pool: {
      purpose: "business_unit",
      id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
      name: "Engineering"
    },
    region: "DE Zone 1",
    owner: {
      id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
      name: "Marie Briggs"
    },
    cloud_account_type: "azure_cnr",
    service_name: "Microsoft.Compute",
    cloud_resource_id:
      "/subscriptions/318bd278-e4ef-4230-9ab4-2ad6a29f578c/resourcegroups/ishtestgroup/providers/microsoft.compute/virtualmachines/spottest",
    cloud_account_id: "11fddd0e-3ece-410c-8e68-003abcc44576",
    cloud_account_name: "Azure trial",
    resource_name: "spottest",
    cost: 14.5
  },
  {
    resource_id: "258804b8-e684-42b9-a148-21795e749168",
    _id: {
      resource_id: "258804b8-e684-42b9-a148-21795e749168"
    },
    resource_type: "Instance",
    active: true,
    pool: {
      purpose: "team",
      id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
      name: "QA"
    },
    region: "eu-central-1",
    owner: {
      id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
      name: "Katy Ali"
    },
    cloud_account_type: "aws_cnr",
    service_name: "AmazonEC2",
    cloud_resource_id: "i-0701429a26d0d574c",
    cloud_account_id: "8c63e980-6572-4b36-be82-a2bc59705888",
    cloud_account_name: "AWS HQ",
    resource_name: "sunflower-us-east-1",
    cost: 28.7082291744
  },
  {
    resource_id: "c955ea30-349e-4fd1-8764-c766e676fd7a",
    _id: {
      resource_id: "c955ea30-349e-4fd1-8764-c766e676fd7a"
    },
    resource_type: "Instance",
    active: true,
    pool: {
      purpose: "business_unit",
      id: "8ce779dc-cc2a-4210-9770-00a2ce7ccf39",
      name: "Marketing"
    },
    region: "eu-central-1",
    owner: {
      id: "015c36f9-5c05-4da8-b445-932560a00191",
      name: "Sally Wong"
    },
    cloud_account_type: "aws_cnr",
    service_name: "AmazonEC2",
    cloud_resource_id: "i-095a8e515029f5153",
    cloud_account_id: "8c63e980-6572-4b36-be82-a2bc59705888",
    cloud_account_name: "AWS HQ",
    resource_name: "mail-server",
    cost: 24.639862891499998
  },
  {
    resource_id: "eb9c3b77-d5e6-48f8-b1f5-0a9c7a92e44a",
    _id: {
      resource_id: "eb9c3b77-d5e6-48f8-b1f5-0a9c7a92e44a"
    },
    resource_type: "Instance",
    active: false,
    pool: {
      purpose: "team",
      id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
      name: "Dev"
    },
    region: "eu-central-1",
    owner: {
      id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
      name: "Ella Price"
    },
    cloud_account_type: "aws_cnr",
    service_name: "AmazonEC2",
    cloud_resource_id: "i-041a8aaca5347338a",
    cloud_account_id: "8c63e980-6572-4b36-be82-a2bc59705888",
    cloud_account_name: "AWS HQ",
    resource_name: "jenkins-worker-1",
    cost: 24.6400322778
  }
];

const environments = [
  {
    name: "dev-1",
    resource_type: "QA stand",
    cloud_resource_id: "environment_8778ced8a4d4d009fc1daf09a1b26a64",
    cloud_account_id: "f64ef403-b787-4df6-b25a-262dce770599",
    region: null,
    is_environment: true,
    active: true,
    employee_id: "6067dd40-6cba-40d1-be75-aeb10face30b",
    pool_id: "9a12b6e1-8541-400b-8bf8-d1d4c0b11f25",
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
      software: "SunWare 1.3.423-integration",
      jira_tickets: [
        {
          url: "https://jira.com.example/NGUI-1242",
          number: "NGUI-1242"
        },
        {
          url: "jira.com.example/NGUI-3214",
          number: "NGUI-3214"
        }
      ]
    },
    shareable: true,
    created_at: 1629798263,
    last_seen: 1631179560,
    deleted_at: 0,
    shareable_bookings: [
      {
        deleted_at: 0,
        id: "17975b2b-0893-4800-86a3-abdce55e5972",
        created_at: 1630570926,
        resource_id: "59edde97-b799-4cf8-8e4d-16c30dbe51c1",
        organization_id: "b4b671c4-f020-464c-b029-05bedb62c598",
        acquired_since: 1630569406,
        released_at: 0,
        acquired_by: {
          id: "c0f9232c-9687-4323-b18a-83fe298b3783",
          name: "Luke Davies"
        }
      }
    ],
    id: "59edde97-b799-4cf8-8e4d-16c30dbe51c1",
    meta: {},
    cloud_console_link: null,
    sub_resources: [],
    recommendations: {},
    dismissed_recommendations: {},
    dismissed: [],
    cloud_account_name: "Environment",
    cloud_account_type: "environment"
  },
  {
    name: "feature-1",
    resource_type: "Dev stand",
    cloud_resource_id: "environment_b79a445f910e942147757b1cabb5b84f",
    cloud_account_id: "f64ef403-b787-4df6-b25a-262dce770599",
    region: null,
    is_environment: true,
    active: true,
    employee_id: "6067dd40-6cba-40d1-be75-aeb10face30b",
    pool_id: "9a12b6e1-8541-400b-8bf8-d1d4c0b11f25",
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
      software: "SunWare 1.3.232-hotfix/support-fix",
      jira_tickets: [
        {
          url: "https://jira.com.example/TCS-2214",
          number: "TCS-2214"
        }
      ]
    },
    created_at: 1629798318,
    last_seen: 1631179560,
    deleted_at: 0,
    shareable_bookings: [
      {
        deleted_at: 0,
        id: "f7824652-9db5-466c-96d7-3cac9321407c",
        created_at: 1630573485,
        resource_id: "7b947ce5-6883-4094-89e5-1784f779d0fb",
        organization_id: "b4b671c4-f020-464c-b029-05bedb62c598",
        acquired_since: 1631734006,
        released_at: 0,
        acquired_by: {
          id: "c0f9232c-9687-4323-b18a-83fe298b3783",
          name: "Luke Davies"
        }
      }
    ],
    id: "7b947ce5-6883-4094-89e5-1784f779d0fb",
    meta: {},
    cloud_console_link: null,
    sub_resources: [],
    recommendations: {},
    dismissed_recommendations: {},
    dismissed: [],
    cloud_account_name: "Environment",
    cloud_account_type: "environment"
  },
  {
    name: "dev-2",
    resource_type: "QA stand",
    cloud_resource_id: "environment_ebff946b5681ea9aa4785f2d719b768e",
    cloud_account_id: "f64ef403-b787-4df6-b25a-262dce770599",
    region: null,
    is_environment: true,
    active: true,
    employee_id: "6067dd40-6cba-40d1-be75-aeb10face30b",
    pool_id: "9a12b6e1-8541-400b-8bf8-d1d4c0b11f25",
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
      software: "SunWare 1.3.424-feature/sunrise_control",
      jira_tickets: [
        {
          url: "https://jira.com.example/TCS-1674",
          number: "TCS-1674"
        },
        {
          url: "https://jira.com.example/TCS-2161",
          number: "TCS-2161"
        }
      ]
    },
    created_at: 1629798280,
    last_seen: 1631179560,
    deleted_at: 0,
    shareable_bookings: [
      {
        deleted_at: 0,
        id: "0e099469-acb4-4da7-905a-3ba50cfad8d1",
        created_at: 1630573516,
        resource_id: "9fabaa52-a719-4aea-b9ce-10af570bf91f",
        organization_id: "b4b671c4-f020-464c-b029-05bedb62c598",
        acquired_since: 1632166006,
        released_at: 1632252406,
        acquired_by: {
          id: "c0f9232c-9687-4323-b18a-83fe298b3783",
          name: "Luke Davies"
        }
      },
      {
        deleted_at: 0,
        id: "3cf8b0db-299b-4efc-b34f-65f8496e2a2b",
        created_at: 1630570949,
        resource_id: "9fabaa52-a719-4aea-b9ce-10af570bf91f",
        organization_id: "b4b671c4-f020-464c-b029-05bedb62c598",
        acquired_since: 1630569406,
        released_at: 1631302006,
        acquired_by: {
          id: "c0f9232c-9687-4323-b18a-83fe298b3783",
          name: "Luke Davies"
        }
      }
    ],
    id: "9fabaa52-a719-4aea-b9ce-10af570bf91f",
    meta: {},
    cloud_console_link: null,
    sub_resources: [],
    recommendations: {},
    dismissed_recommendations: {},
    dismissed: [],
    cloud_account_name: "Environment",
    cloud_account_type: "environment"
  },
  {
    name: "pre-release",
    resource_type: "QA stand",
    cloud_resource_id: "environment_6d273a1175ba5916eae2b4f6708b21d6",
    cloud_account_id: "f64ef403-b787-4df6-b25a-262dce770599",
    region: null,
    is_environment: true,
    active: true,
    employee_id: "6067dd40-6cba-40d1-be75-aeb10face30b",
    pool_id: "9a12b6e1-8541-400b-8bf8-d1d4c0b11f25",
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
      software: "SunWare 1.2.161-master",
      jira_tickets: [
        {
          url: "https://jira.com.example/QA-617",
          number: "QA-617"
        }
      ]
    },
    created_at: 1629798297,
    last_seen: 1631179560,
    deleted_at: 0,
    shareable_bookings: [],
    id: "1e067935-1888-403b-a6ed-ade9522a15cc",
    meta: {},
    cloud_console_link: null,
    sub_resources: [],
    recommendations: {},
    dismissed_recommendations: {},
    dismissed: [],
    cloud_account_name: "Environment",
    cloud_account_type: "environment"
  },
  {
    name: "feature-2",
    resource_type: "Dev stand",
    cloud_resource_id: "environment_1d140fbc9f902a8608a51307e4d0612b",
    cloud_account_id: "f64ef403-b787-4df6-b25a-262dce770599",
    region: null,
    is_environment: true,
    active: true,
    employee_id: "6067dd40-6cba-40d1-be75-aeb10face30b",
    pool_id: "9a12b6e1-8541-400b-8bf8-d1d4c0b11f25",
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
      software: "SunWare 1.2.162-master",
      jira_tickets: [
        {
          url: "https://jira.com.example/NGUI-2617",
          number: "NGUI-2617"
        },
        {
          url: "https://jira.com.example/NGUI-2600",
          number: "NGUI-2600"
        },
        {
          url: "https://jira.com.example/NGUI-2620",
          number: "NGUI-2620"
        },
        {
          url: "https://jira.com.example/TCS-1355",
          number: "TCS-1355"
        },
        {
          url: "https://jira.com.example/TCS-1558",
          number: "TCS-1558"
        }
      ]
    },
    created_at: 1629798332,
    last_seen: 1631179560,
    deleted_at: 0,
    shareable_bookings: [],
    id: "b9893a72-09a1-47d4-9950-a2100feaf3c7",
    meta: {},
    cloud_console_link: null,
    sub_resources: [],
    recommendations: {},
    dismissed_recommendations: {},
    dismissed: [],
    cloud_account_name: "Environment",
    cloud_account_type: "environment"
  }
];

const getOrganizationExpenses = () => {
  const todayUnix = millisecondsToSeconds(+new Date());
  const lastMonthRangeEndUnix = getLastMonthRange(true).end;

  return {
    expenses: {
      this_month: {
        total: 118080.90259006835,
        date: todayUnix
      },
      this_month_forecast: {
        total: 141080.9,
        date: todayUnix
      },
      last_month: {
        total: 169000.02920730546,
        date: lastMonthRangeEndUnix
      }
    },
    total: 160000,
    pools: [
      {
        this_month_forecast: 118546.9,
        name: "Sunflower corporation",
        purpose: "business_unit",
        pool: 160000,
        this_month_expenses: 95546.0502165,
        id: MOCKED_ORGANIZATION_POOL_ID
      }
    ]
  };
};

const DashboardMocked = () => (
  <PageContentWrapper>
    <DashboardGridLayout
      topResourcesExpensesCard={<TopResourcesExpensesCard cleanExpenses={cleanExpenses} />}
      environmentsCard={<EnvironmentsCard environments={environments} />}
      organizationExpenses={<OrganizationExpenses data={getOrganizationExpenses()} />}
      recommendationsCard={
        <RecommendationsCard
          possibleMonthlySavings={55108.924360775185}
          costRecommendationsCount={116}
          securityRecommendationsCount={21}
        />
      }
    />
  </PageContentWrapper>
);

export default DashboardMocked;
