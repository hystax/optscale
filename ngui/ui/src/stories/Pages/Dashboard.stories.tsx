import { useContext } from "react";
import { Provider } from "react-redux";
import { GET_DATA_SOURCES, GET_ENVIRONMENTS } from "api/restapi/actionTypes";
import Dashboard from "components/Dashboard";
import { MockPermissionsStateContext } from "stories";

export default {
  component: Dashboard,
  argTypes: {
    withEnvironments: { name: "With environments", control: "boolean", defaultValue: false }
  }
};

const environments = [
  {
    name: "dev-1",
    resource_type: "QA stand",
    cloud_resource_id: "environment_8778ced8a4d4d009fc1daf09a1b26a64",
    cloud_account_id: "8c6cc9dc-0983-4d73-b81f-3c57d84ec60e",
    region: null,
    is_environment: true,
    active: true,
    employee_id: "9eeb7c0e-6a58-42be-8fc7-f82fa8679ed7",
    pool_id: "8d67b712-d897-4129-8bf5-cf5cf5d1cf65",
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
    created_at: 1630191997,
    last_seen: 1632598175,
    deleted_at: 0,
    shareable_bookings: [
      {
        deleted_at: 0,
        id: "fc9aa9b9-da61-47ab-9e23-226ede6912c9",
        created_at: 1630964660,
        resource_id: "4aca8b0b-8f3f-4b5d-8591-72d3f7291ba7",
        organization_id: "02a7a9e0-9b09-412f-a739-7209fbc067ec",
        acquired_since: 1631991855,
        released_at: 0,
        acquired_by: {
          id: "9271f4db-7ce5-46d0-bd5c-9224b94e0d06",
          name: "Evelyn Jackson"
        }
      }
    ],
    id: "4aca8b0b-8f3f-4b5d-8591-72d3f7291ba7",
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
    cloud_account_id: "8c6cc9dc-0983-4d73-b81f-3c57d84ec60e",
    region: null,
    is_environment: true,
    active: true,
    employee_id: "9eeb7c0e-6a58-42be-8fc7-f82fa8679ed7",
    pool_id: "8d67b712-d897-4129-8bf5-cf5cf5d1cf65",
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
    created_at: 1630192052,
    last_seen: 1632598175,
    deleted_at: 0,
    shareable_bookings: [
      {
        deleted_at: 0,
        id: "77a4f81b-356f-4a93-9766-bfca6c889352",
        created_at: 1630967219,
        resource_id: "3c473d0f-609e-4521-9660-64a38f28a4b4",
        organization_id: "02a7a9e0-9b09-412f-a739-7209fbc067ec",
        acquired_since: 1633153896,
        released_at: 0,
        acquired_by: {
          id: "9271f4db-7ce5-46d0-bd5c-9224b94e0d06",
          name: "Evelyn Jackson"
        }
      }
    ],
    id: "3c473d0f-609e-4521-9660-64a38f28a4b4",
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
    cloud_account_id: "8c6cc9dc-0983-4d73-b81f-3c57d84ec60e",
    region: null,
    is_environment: true,
    active: true,
    employee_id: "9eeb7c0e-6a58-42be-8fc7-f82fa8679ed7",
    pool_id: "8d67b712-d897-4129-8bf5-cf5cf5d1cf65",
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
    created_at: 1630192014,
    last_seen: 1632598175,
    deleted_at: 0,
    shareable_bookings: [
      {
        deleted_at: 0,
        id: "2f69ffe1-3dec-4557-b62c-8d428a7e2d82",
        created_at: 1630967250,
        resource_id: "ff3cceb5-0149-4e44-8df4-921189a94b8a",
        organization_id: "02a7a9e0-9b09-412f-a739-7209fbc067ec",
        acquired_since: 1633585865,
        released_at: 1633672265,
        acquired_by: {
          id: "9271f4db-7ce5-46d0-bd5c-9224b94e0d06",
          name: "Evelyn Jackson"
        }
      },
      {
        deleted_at: 0,
        id: "6bc036b6-3f55-4cf8-8d91-04919dcd7de9",
        created_at: 1630964683,
        resource_id: "ff3cceb5-0149-4e44-8df4-921189a94b8a",
        organization_id: "02a7a9e0-9b09-412f-a739-7209fbc067ec",
        acquired_since: 1631991832,
        released_at: 1632724432,
        acquired_by: {
          id: "9271f4db-7ce5-46d0-bd5c-9224b94e0d06",
          name: "Evelyn Jackson"
        }
      }
    ],
    id: "ff3cceb5-0149-4e44-8df4-921189a94b8a",
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
    cloud_account_id: "8c6cc9dc-0983-4d73-b81f-3c57d84ec60e",
    region: null,
    is_environment: true,
    active: true,
    employee_id: "9eeb7c0e-6a58-42be-8fc7-f82fa8679ed7",
    pool_id: "8d67b712-d897-4129-8bf5-cf5cf5d1cf65",
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
    created_at: 1630192031,
    last_seen: 1632598175,
    deleted_at: 0,
    shareable_bookings: [],
    id: "301b86c0-cf44-4103-acd4-03851286b339",
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
    cloud_account_id: "8c6cc9dc-0983-4d73-b81f-3c57d84ec60e",
    region: null,
    is_environment: true,
    active: true,
    employee_id: "9eeb7c0e-6a58-42be-8fc7-f82fa8679ed7",
    pool_id: "8d67b712-d897-4129-8bf5-cf5cf5d1cf65",
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
    created_at: 1630192066,
    last_seen: 1632598175,
    deleted_at: 0,
    shareable_bookings: [],
    id: "2e661302-3f6c-44d7-9476-54512af1fa4d",
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

const onlyEnvironmentDataSources = [
  {
    deleted_at: 0,
    id: "e2bc1b1f-deeb-4eb7-892a-d3714fde97c6",
    created_at: 1630193075,
    name: "Environment",
    type: "environment",
    config: {},
    organization_id: "a42c727b-52dd-4b48-8785-dfaed6b75404",
    auto_import: false,
    import_period: 1,
    last_import_at: 1631992150,
    last_import_modified_at: 0,
    account_id: "4e84a988-a4ab-418a-a576-9f0e9611e5fb",
    process_recommendations: false,
    last_import_attempt_at: 1631516521,
    last_import_attempt_error: null,
    details: {}
  }
];

const allDataSources = [
  {
    deleted_at: 0,
    id: "e2bc1b1f-deeb-4eb7-892a-d3714fde97c6",
    created_at: 1630193075,
    name: "Environment",
    type: "environment",
    config: {},
    organization_id: "a42c727b-52dd-4b48-8785-dfaed6b75404",
    auto_import: false,
    import_period: 1,
    last_import_at: 1631992150,
    last_import_modified_at: 0,
    account_id: "4e84a988-a4ab-418a-a576-9f0e9611e5fb",
    process_recommendations: false,
    last_import_attempt_at: 1631516521,
    last_import_attempt_error: null,
    details: {}
  },
  {
    deleted_at: 0,
    id: "12bc1b1f-deeb-4eb7-892a-d3714fde97c6",
    created_at: 1630193075,
    name: "AWS",
    type: "aws_cnr",
    config: {},
    organization_id: "a42c727b-52dd-4b48-8785-dfaed6b75404",
    auto_import: false,
    import_period: 1,
    last_import_at: 1631992150,
    last_import_modified_at: 0,
    account_id: "4e84a988-a4ab-418a-a576-9f0e9611e5fb",
    process_recommendations: false,
    last_import_attempt_at: 1631516521,
    last_import_attempt_error: null,
    details: {}
  }
];

const MockPermissionsContextWrapper = ({ children }) => children(useContext(MockPermissionsStateContext));

export const NoDataSources = () => (
  <MockPermissionsContextWrapper>
    {({ mockStore, mockState }) => {
      mockState.mockRestapi({
        [GET_DATA_SOURCES]: {
          cloudAccounts: []
        }
      });

      const store = mockStore(mockState);

      return (
        <Provider store={store}>
          <Dashboard />
        </Provider>
      );
    }}
  </MockPermissionsContextWrapper>
);

export const OnlyEnvironmentDataSources = (args) => (
  <MockPermissionsContextWrapper>
    {({ mockStore, mockState }) => {
      mockState.mockRestapi({
        [GET_DATA_SOURCES]: {
          cloudAccounts: onlyEnvironmentDataSources
        },
        [GET_ENVIRONMENTS]: args.withEnvironments ? [] : environments
      });

      const store = mockStore(mockState);

      return (
        <Provider store={store}>
          <Dashboard />
        </Provider>
      );
    }}
  </MockPermissionsContextWrapper>
);

export const AllDataSources = (args) => (
  <MockPermissionsContextWrapper>
    {({ mockStore, mockState }) => {
      mockState.mockRestapi({
        [GET_DATA_SOURCES]: {
          cloudAccounts: allDataSources
        },
        [GET_ENVIRONMENTS]: args.withEnvironments ? [] : environments
      });

      const store = mockStore(mockState);

      return (
        <Provider store={store}>
          <Dashboard />
        </Provider>
      );
    }}
  </MockPermissionsContextWrapper>
);
