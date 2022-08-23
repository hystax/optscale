import React, { useState } from "react";
import { boolean } from "@storybook/addon-knobs";
import { Provider } from "react-redux";
import RelevantRecommendations from "components/RelevantRecommendations";
import { ALL_CATEGORY } from "components/RelevantRecommendations/constants";
import { MOCKED_ORGANIZATION_ID } from "mocks/idsMock";
import { KINDS } from "stories";
import {
  RECOMMENDATION_SHORT_LIVING_INSTANCES,
  RECOMMENDATION_VOLUMES_NOT_ATTACHED_FOR_LONG_TIME,
  RECOMMENDATION_INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME,
  RECOMMENDATION_INSTANCE_MIGRATION,
  RECOMMENDATION_OBSOLETE_SNAPSHOTS,
  RECOMMENDATION_OBSOLETE_SNAPSHOT_CHAINS,
  RECOMMENDATIONS_TABS,
  RECOMMENDATION_OBSOLETE_IMAGES,
  RECOMMENDATION_RESERVED_INSTANCES,
  RECOMMENDATION_INSTANCE_SUBSCRIPTION,
  RECOMMENDATION_RIGHTSIZING_INSTANCES,
  RECOMMENDATION_RIGHTSIZING_RDS_INSTANCES,
  RECOMMENDATION_ABANDONED_INSTANCES,
  RECOMMENDATION_INACTIVE_USERS,
  RECOMMENDATION_INACTIVE_CONSOLE_USERS,
  RECOMMENDATION_INSECURE_SECURITY_GROUPS,
  RECOMMENDATION_OBSOLETE_IPS,
  RECOMMENDATION_ABANDONED_KINESIS_STREAMS,
  RECOMMENDATION_PUBLIC_S3_BUCKETS,
  RECOMMENDATION_ABANDONED_S3_BUCKETS
} from "utils/constants";
import { getCurrentUTCTimeInSec } from "utils/datetime";
import { MockState, mockStore } from "utils/mockStore";
import { mockCategorizedRecommendations } from "utils/recommendationCategories";

const { ACTIVE: ACTIVE_RECOMMENDATIONS_TAB } = RECOMMENDATIONS_TABS;

export default {
  title: `${KINDS.COMPONENTS}/Recommendations`
};

const options = {
  days_threshold: 90,
  cpu_percent_threshold: 5,
  network_bps_threshold: 1000
};

const basicDataWithDismissed = mockCategorizedRecommendations({
  id: "aabe9d07-2eca-42de-9d2d-ad3984c4fb0f",
  last_run: 1599827314,
  next_run: 1599838114,
  last_completed: 1599827314,
  organization_id: "e9ce024e-588c-4ce9-9147-b894111738e9",
  total_saving: 0.7841682144000001,
  optimizations: {
    [RECOMMENDATION_SHORT_LIVING_INSTANCES]: {
      count: 1,
      saving: 150,
      items: [
        {
          cloud_resource_id: "i-9323123124",
          resource_name: "my test instance",
          resource_id: "58bef498-9f06-4c0f-aac0-312b22fcb9ee",
          cloud_account_id: "01bcb8f5-85c7-4c3b-823f-800900477eda",
          cloud_account_name: "AWS c-Loud",
          cloud_type: "aws_cnr",
          total_cost: 20,
          first_seen: 1600077735,
          last_seen: 1600078565,
          saving: 150
        }
      ]
    },
    [RECOMMENDATION_INSECURE_SECURITY_GROUPS]: {
      count: 1,
      items: [
        {
          cloud_resource_id: "i-9323123124",
          resource_id: "e8e8f77d-79e8-4e8b-85d4-dc3676e75b44",
          cloud_type: "aws_cnr",
          resource_name: "my test instance",
          cloud_account_id: "01bcb8f5-85c7-4c3b-823f-800900477eda",
          cloud_account_name: "aws_cnr",
          security_group_name: "my unsecure sg",
          security_group_id: "sg-0b5f201c2dfed49b1"
        }
      ]
    },
    [RECOMMENDATION_VOLUMES_NOT_ATTACHED_FOR_LONG_TIME]: {
      count: 1,
      saving: 1.0869047777142857,
      items: [
        {
          saving: 1.0869047777142857,
          cloud_type: "aws_cnr",
          last_seen_in_attached_state: 0,
          cloud_resource_id: "vol-096cb82fa789e439d",
          resource_name: "centos_a7ef34f3-daa9-711e-18b5-206f5b981600",
          cost_in_detached_state: 0.7608333444000001,
          resource_id: "4cc1117f-0cbc-439b-88e4-fc28fb20a737",
          cloud_account_id: "c46cf66c-84ba-41a7-820c-c2408b923353",
          cloud_account_name: "aws",
          region: "eu-central-1"
        }
      ]
    },
    [RECOMMENDATION_INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME]: {
      count: 1,
      saving: 1.0869047777142857,
      items: [
        {
          saving: 1.0869047777142857,
          cloud_type: "azure_cnr",
          last_seen_active: 0,
          cloud_resource_id: "i-0562bc6556bf62835",
          resource_name: "centos_a7ef34f3-daa9-711e-18b5-206f5b981600",
          cost_in_stopped_state: 0.7608333444000001,
          resource_id: "4cc1117f-0cbc-439b-88e4-fc28fb20a737",
          cloud_account_id: "c46cf66c-84ba-41a7-820c-c2408b923353",
          cloud_account_name: "azure"
        }
      ]
    },
    [RECOMMENDATION_INSTANCE_MIGRATION]: {
      count: 1,
      saving: 15.84,
      items: [
        {
          saving: 15.84,
          flavor: "t3.xlarge",
          current_region: "eu-west-1",
          recommended_region: "eu-south-1",
          cloud_resource_id: "i-320bc22927",
          resource_name: "int-dc",
          resource_id: "4cc1117f-0cbc-439b-88e4-fc28fb20a737",
          cloud_account_id: "c46cf66c-84ba-41a7-820c-c2408b923353",
          cloud_account_name: "aws"
        }
      ]
    },
    [RECOMMENDATION_OBSOLETE_IMAGES]: {
      count: 1,
      saving: 15,
      items: [
        {
          cloud_resource_id: "ami-f856be97",
          resource_name: "my test snapshot",
          cloud_account_id: "01bcb8f5-85c7-4c3b-823f-800900477eda",
          cloud_account_name: "aws-elasticbeanstalk-amzn-2016.03.2.x86_64-java8-pv-201606252039",
          cloud_type: "aws_cnr",
          first_seen: 0,
          last_used: 0,
          saving: 15,
          region: "eu-west-1",
          snapshots: [
            {
              resource_id: "56c6bcad-15c1-46cf-bcb4-6562e6d9fe27",
              cloud_resource_id: "snap-0b27b8fea604efe02",
              cost: 2.5
            },
            {
              resource_id: "0422cd69-508d-4307-8e0f-a38b2feb61ce",
              cloud_resource_id: "snap-0cb661037f1ccac00",
              cost: 12.5
            }
          ]
        }
      ]
    },
    [RECOMMENDATION_RESERVED_INSTANCES]: {
      count: 1,
      saving: 15.84,
      items: [
        {
          saving: 15.84,
          average_saving: 20.33,
          flavor: "t3.xlarge",
          region: "eu-west-1",
          cloud_resource_id: "i-320bc22927",
          resource_name: "int-dc",
          resource_id: "4cc1117f-0cbc-439b-88e4-fc28fb20a737",
          cloud_account_id: "c46cf66c-84ba-41a7-820c-c2408b923353",
          cloud_account_name: "aws",
          cloud_type: "aws_cnr"
        }
      ]
    },
    [RECOMMENDATION_INSTANCE_SUBSCRIPTION]: {
      count: 2,
      saving: 1562.76,
      items: [
        {
          monthly_saving: 13.170000000000002,
          yearly_saving: 215.97999999999996,
          invoice_discount: 0.0,
          flavor: "ecs.t5-c1m1.xlarge",
          region: "Germany (Frankfurt)",
          cloud_resource_id: "i-gw8bwy1fbwc2spcyqhdy",
          resource_name: "instance",
          resource_id: "d6652f90-e9d2-4681-9199-ddfd24d3f9cf",
          cloud_account_id: "ebcf6ecd-adc9-4db6-9001-956387497d89",
          cloud_account_name: "ali",
          cloud_type: "alibaba_cnr"
        }
      ]
    },
    [RECOMMENDATION_RIGHTSIZING_INSTANCES]: {
      count: 1,
      saving: 34.29,
      items: [
        {
          cloud_resource_id: "i-asdasfhakdfd",
          resource_name: "some name",
          resource_id: "6a756189-bcca-4675-b175-7a1e5ed1a951",
          cloud_account_id: "c0b8a7eb-19b2-4f75-bd1e-59c471974021",
          cloud_account_name: "my cloud",
          cloud_type: "aws_cnr",
          region: "westus2",
          flavor: "t6.medium",
          recommended_flavor: "t6.mini",
          saving: 34.29,
          saving_percent: 28,
          current_cost: 231,
          cpu: 8,
          recommended_flavor_cpu: 2,
          recommended_flavor_ram: 4,
          cpu_usage: 0.69
        }
      ]
    },
    [RECOMMENDATION_RIGHTSIZING_RDS_INSTANCES]: {
      count: 1,
      saving: 34.29,
      items: [
        {
          cloud_resource_id: "i-zxzxsfhakdfd",
          resource_name: "some RDS name",
          resource_id: "7a756189-bcca-4675-b175-7a1e5ed1a951",
          cloud_account_id: "c1b8a7eb-19b2-4f75-bd1e-59c471974021",
          cloud_account_name: "my cloud",
          cloud_type: "aws_cnr",
          region: "westus2",
          flavor: "t6.medium",
          recommended_flavor: "t6.mini",
          saving: 34.29,
          saving_percent: 28,
          current_cost: 231,
          cpu: 8,
          recommended_flavor_cpu: 2,
          recommended_flavor_ram: 4,
          cpu_usage: 0.69
        }
      ]
    },
    [RECOMMENDATION_ABANDONED_INSTANCES]: {
      count: 1,
      saving: 9.246616381499999,
      items: [
        {
          cloud_resource_id: "i-0436ee72bb653bf8a",
          resource_name: "aqa_us_instance_for_migration",
          resource_id: "6bd18da1-65bd-474c-8a6b-f67c7f408834",
          cloud_account_id: "7a84793a-4316-441b-bf86-2281540f4336",
          cloud_account_name: "ds-aws",
          cloud_type: "aws_cnr",
          region: "us-west-1",
          owner: {
            id: "d572bd3f-5660-47e8-8357-148cabbdcc3d",
            name: "Test User"
          },
          pool: {
            id: "4bbe9978-5717-4ee7-aca1-f13b73e4acdc",
            name: "ds-aws",
            purpose: "budget"
          },
          saving: 9.246616381499999
        }
      ]
    },
    [RECOMMENDATION_INACTIVE_USERS]: {
      count: 1,
      items: [
        {
          cloud_account_id: "01bcb8f5-85c7-4c3b-823f-800900477eda",
          cloud_account_name: "AWS c-Loud",
          cloud_type: "aws_cnr",
          user_name: "va-iam-full",
          user_id: "AIDAIRJLK4AMQQJFQ22T2",
          last_used: 1600078565
        }
      ]
    },
    [RECOMMENDATION_INACTIVE_CONSOLE_USERS]: {
      count: 1,
      items: [
        {
          cloud_account_id: "01bcb8f5-85c7-4c3b-823f-800900477eda",
          cloud_account_name: "AWS cloud",
          cloud_type: "aws_cnr",
          user_name: "as-full",
          user_id: "AIDAIRJLK4AMQQJFQ22T2",
          last_used: 1600078565
        }
      ]
    },
    [RECOMMENDATION_OBSOLETE_IPS]: {
      count: 1,
      saving: 4.563254672357,
      items: [
        {
          saving: 4.563254672357,
          cloud_type: "azure_cnr",
          last_seen_active: 0,
          cloud_resource_id:
            "/subscriptions/318bd278-e4ef-4230-9ab4-2ad6a29f578c/resourceGroups/aqa/providers/Microsoft.Network/publicIPAddresses/as_test_opt_ip",
          resource_name: "as_test_opt_ip",
          cost_not_active_ip: 2.546235467233,
          resource_id: "4cc1117f-0cbc-439b-88e4-fc28fb20a737",
          cloud_account_id: "c46cf66c-84ba-41a7-820c-c2408b923353",
          cloud_account_name: "azure cloud account",
          region: "eu-central-1"
        }
      ]
    },
    [RECOMMENDATION_ABANDONED_KINESIS_STREAMS]: {
      count: 1,
      saving: 216,
      items: [
        {
          cloud_resource_id: "i-0436ee72bb653bf8a",
          resource_name: "aqa_us_instance_for_migration",
          resource_id: "6bd18da1-65bd-474c-8a6b-f67c7f408834",
          cloud_account_id: "7a84793a-4316-441b-bf86-2281540f4336",
          cloud_account_name: "ds-aws",
          cloud_type: "aws_cnr",
          region: "us-west-1",
          shardhours_capacity: 20,
          shardhours_price: 0.015,
          saving: 216
        }
      ]
    },
    [RECOMMENDATION_ABANDONED_S3_BUCKETS]: {
      count: 1,
      items: [
        {
          cloud_resource_id: "hystax-ap-south-1",
          resource_name: "hystax-ap-south-1",
          resource_id: "7fe79f82-dbde-4c94-9ceb-8feea604bdb6",
          cloud_account_id: "7a84793a-4316-441b-bf86-2281540f4336",
          cloud_account_name: "as-aws",
          cloud_type: "aws_cnr",
          region: "ap-south-1",
          owner: {
            id: "d572bd3f-5660-47e8-8357-148cabbdcc3d",
            name: "AS Test User"
          },
          pool: {
            id: "4bbe9978-5717-4ee7-aca1-f13b73e4acdc",
            name: "as-aws",
            purpose: "budget"
          },
          avg_data_size: 512,
          tier_2_request_quantity: 1000,
          tier_1_request_quantity: 50,
          saving: 9.246616381499999
        }
      ],
      saving: 9.246616381499999
    }
  },
  dismissed_optimizations: {
    [RECOMMENDATION_OBSOLETE_SNAPSHOTS]: {
      count: 1,
      saving: 3.5231851912,
      items: [
        {
          cloud_resource_id: "snap-09f6eb8f60d61385e",
          resource_name: null,
          resource_id: "f916043c-23fb-438d-9ca5-b0b4e908a4e1",
          cloud_account_id: "78e040e0-5715-4974-9c66-380865112652",
          cloud_account_name: "AWS root",
          cloud_type: "aws_cnr",
          first_seen: 1614211200,
          last_seen: 1615852800,
          saving: 3.5231851912,
          region: "eu-central-1",
          is_dismissed: true
        }
      ],
      limit: 1000
    },
    [RECOMMENDATION_OBSOLETE_SNAPSHOT_CHAINS]: {
      count: 1,
      saving: 0.053740981001114234,
      items: [
        {
          cloud_resource_id: "sl-gw89m2bx11esxxu38zgn",
          resource_name: null,
          resource_id: "54789ed0-bb2a-416d-8c85-9338b9549e17",
          cloud_account_id: "5b41bd31-9b73-498f-a3a1-36e0900a1271",
          cloud_account_name: "ds-alibaba",
          cloud_type: "alibaba_cnr",
          first_seen: 1622505600,
          last_seen: 1627257600,
          saving: 0.053740981001114234,
          region: "Germany (Frankfurt)",
          last_used: 0,
          child_snapshots: [
            {
              cloud_resource_id: "s-gw8ifbha3p0ixonr77xy",
              name: "data-disk-snap1",
              cloud_console_link:
                "https://ecs.console.aliyun.com/#/snapshot/region/eu-central-1?snapshotIds=s-gw8ifbha3p0ixonr77xy"
            }
          ]
        }
      ],
      limit: 1000
    },
    [RECOMMENDATION_PUBLIC_S3_BUCKETS]: {
      count: 1,
      items: [
        {
          cloud_resource_id: "test-bucket",
          resource_name: null,
          resource_id: "58bef498-9f06-4c0f-aac0-312b22fcb9ee",
          cloud_account_id: "01bcb8f5-85c7-4c3b-823f-800900477eda",
          cloud_account_name: "AWS",
          cloud_type: "aws_cnr",
          region: "us-west-2",
          owner: {
            id: "d572bd3f-5660-47e8-8357-148cabbdcc3d",
            name: "Test User"
          },
          pool: {
            id: "4bbe9978-5717-4ee7-aca1-f13b73e4acdc",
            name: "ds-aws",
            purpose: "budget"
          },
          is_excluded: false,
          is_public_policy: true,
          is_public_acls: false
        }
      ]
    }
  }
});

const dataSampleWithError = mockCategorizedRecommendations({
  id: "aabe9d07-2eca-42de-9d2d-ad3984c4fb0f",
  last_run: 1599827314,
  next_run: 1599838114,
  last_completed: 1599827314,
  organization_id: "e9ce024e-588c-4ce9-9147-b894111738e9",
  total_saving: 0.7841682144000001,
  optimizations: {
    [RECOMMENDATION_SHORT_LIVING_INSTANCES]: {
      count: 0,
      saving: 0,
      error: "test error text",
      items: []
    },
    [RECOMMENDATION_OBSOLETE_IMAGES]: {
      count: 0,
      saving: 0,
      error: "test error text",
      items: []
    },
    [RECOMMENDATION_RESERVED_INSTANCES]: {
      count: 1,
      saving: 12,
      error: "test error text",
      items: [
        {
          saving: 15.84,
          average_saving: 20.33,
          flavor: "t3.xlarge",
          region: "eu-west-1",
          cloud_resource_id: "i-320bc22927",
          resource_name: "int-dc",
          resource_id: "4cc1117f-0cbc-439b-88e4-fc28fb20a737",
          cloud_account_id: "c46cf66c-84ba-41a7-820c-c2408b923353",
          cloud_account_name: "aws",
          cloud_type: "aws_cnr"
        }
      ]
    }
  }
});

const lastRunLastCompletedAreZeroData = mockCategorizedRecommendations({
  id: "aabe9d07-2eca-42de-9d2d-ad3984c4fb0f",
  last_run: 0,
  next_run: 0,
  last_completed: 0,
  organization_id: "e9ce024e-588c-4ce9-9147-b894111738e9",
  total_saving: 0.7841682144000001,
  optimizations: {},
  dismissed_recommendations: {}
});

const lastRunIsNotZeroLastCompletedIsZeroData = mockCategorizedRecommendations({
  id: "aabe9d07-2eca-42de-9d2d-ad3984c4fb0f",
  last_run: 1599827314,
  next_run: 1599838114,
  last_completed: 0,
  organization_id: "e9ce024e-588c-4ce9-9147-b894111738e9",
  total_saving: 0.7841682144000001,
  optimizations: {}
});

const limitedData = mockCategorizedRecommendations({
  id: "aabe9d07-2eca-42de-9d2d-ad3984c4fb0f",
  last_run: 1599827314,
  next_run: 1599838114,
  last_completed: 1599827314,
  organization_id: "e9ce024e-588c-4ce9-9147-b894111738e9",
  total_saving: 0.7841682144000001,
  optimizations: {
    [RECOMMENDATION_SHORT_LIVING_INSTANCES]: {
      count: 5,
      limit: 2,
      saving: 150,
      items: [
        {
          cloud_resource_id: "i-9323123124",
          resource_name: "my test instance",
          resource_id: "58bef498-9f06-4c0f-aac0-312b22fcb9ee",
          cloud_account_id: "01bcb8f5-85c7-4c3b-823f-800900477eda",
          cloud_account_name: "AWS c-Loud",
          cloud_type: "aws_cnr",
          total_cost: 20,
          first_seen: 1600077735,
          last_seen: 1600078565,
          saving: 150
        },
        {
          cloud_resource_id: "i-9323123124",
          resource_name: "my test instance",
          resource_id: "58bef498-9f06-4c0f-aac0-312b22fcb9ee",
          cloud_account_id: "01bcb8f5-85c7-4c3b-823f-800900477eda",
          cloud_account_name: "AWS c-Loud",
          cloud_type: "aws_cnr",
          total_cost: 20,
          first_seen: 1600077735,
          last_seen: 1600078565,
          saving: 150
        }
      ]
    }
  }
});

const allGoodData = mockCategorizedRecommendations({
  id: "aabe9d07-2eca-42de-9d2d-ad3984c4fb0f",
  last_run: getCurrentUTCTimeInSec() - 500,
  next_run: getCurrentUTCTimeInSec() + 10000,
  last_completed: getCurrentUTCTimeInSec() - 500,
  organization_id: "e9ce024e-588c-4ce9-9147-b894111738e9",
  total_saving: 0.7841682144000001,
  optimizations: {}
});

const initExpandedState = {
  [RECOMMENDATION_SHORT_LIVING_INSTANCES]: false,
  [RECOMMENDATION_VOLUMES_NOT_ATTACHED_FOR_LONG_TIME]: false,
  [RECOMMENDATION_INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME]: false,
  [RECOMMENDATION_INSTANCE_MIGRATION]: false,
  [RECOMMENDATION_OBSOLETE_IMAGES]: false,
  [RECOMMENDATION_RESERVED_INSTANCES]: false,
  [RECOMMENDATION_RIGHTSIZING_INSTANCES]: false,
  [RECOMMENDATION_RIGHTSIZING_RDS_INSTANCES]: false,
  [RECOMMENDATION_INACTIVE_USERS]: false,
  [RECOMMENDATION_INACTIVE_CONSOLE_USERS]: false,
  [RECOMMENDATION_INSECURE_SECURITY_GROUPS]: false,
  [RECOMMENDATION_INSTANCE_SUBSCRIPTION]: false,
  [RECOMMENDATION_ABANDONED_KINESIS_STREAMS]: false,
  [RECOMMENDATION_PUBLIC_S3_BUCKETS]: false
};

const RecommendationsStory = ({ data }) => {
  const [expanded, setExpanded] = useState(initExpandedState);
  const [selectedTab, setSelectedTab] = useState(ACTIVE_RECOMMENDATIONS_TAB);

  const updateExpanded = (taskName) => {
    setExpanded((prevState) => ({
      ...{
        ...prevState,
        ...initExpandedState,
        [taskName]: !prevState[taskName]
      }
    }));
  };

  const handleAccordionsChange = (optimizationName) => {
    updateExpanded(optimizationName);
  };

  const handleTabChange = (event, value) => {
    setSelectedTab(value);
    handleAccordionsChange();
  };

  const withManageResourcePermissions = boolean(
    "with [MANAGE_RESOURCES, MANAGE_OWN_RESOURCES] permissions (enables activate and dismissed actions)",
    false
  );
  const withManageChecklistsPermission = boolean("with [MANAGE_CHECKLISTS] permission (enables force check button)", false);
  const withManageCloudCredentialsPermission = boolean(
    "with [MANAGE_CLOUD_CREDENTIALS] permission (renders data source name as a link)",
    false
  );
  const getPermissions = () => {
    const permissions = [];
    if (withManageResourcePermissions) {
      permissions.push("MANAGE_RESOURCES", "MANAGE_OWN_RESOURCES");
    }
    if (withManageChecklistsPermission) {
      permissions.push("MANAGE_CHECKLISTS");
    }
    if (withManageCloudCredentialsPermission) {
      permissions.push("MANAGE_CLOUD_CREDENTIALS");
    }
    return permissions;
  };

  const mockState = new MockState();
  mockState.mockOrganizationPermissions(MOCKED_ORGANIZATION_ID, getPermissions());

  const store = mockStore(mockState);

  const [recommendationCategory, setRecommendationCategory] = useState(ALL_CATEGORY);

  const updateCategoryAndSelectedTab = (newCategory) => {
    setRecommendationCategory(newCategory);
    setSelectedTab(selectedTab);
  };

  return (
    <Provider store={store}>
      <RelevantRecommendations
        isLoadingProps={{
          isGetRecommendationsLoading: boolean("isGetRecommendationsLoading", false),
          isTabWrapperReady: boolean("isTabWrapperReady", true),
          isUpdateRecommendationsLoading: boolean("isUpdateRecommendationsLoading", false),
          isGetResourceAllowedActionsLoading: boolean("isGetResourceAllowedActionsLoading", false)
        }}
        selectedTab={selectedTab}
        handleTabChange={handleTabChange}
        patchResource={() => console.log("patchResource")}
        data={data}
        expanded={expanded}
        handleAccordionsChange={handleAccordionsChange}
        downloadRecommendation={() => console.log("downloadRecommendation")}
        downloadCleanupScript={() => console.log("downloadCleanupScript")}
        categorizedRecommendations={data.categorizedRecommendations}
        categoriesSizes={data.categoriesSizes}
        recommendationCategory={recommendationCategory}
        updateCategoryAndSelectedTab={updateCategoryAndSelectedTab}
        options={options}
      />
    </Provider>
  );
};

export const basic = () => <RecommendationsStory data={basicDataWithDismissed} />;

export const pluralTitles = () => {
  const pluralData = {
    ...basicDataWithDismissed,
    optimizations: {
      ...Object.entries(basicDataWithDismissed.optimizations).reduce(
        (res, [optimization, data]) => ({
          ...res,
          [optimization]: {
            ...data,
            count: 2
          }
        }),
        {}
      )
    }
  };
  return <RecommendationsStory data={pluralData} />;
};

export const withError = () => <RecommendationsStory data={dataSampleWithError} />;

export const lastRunLastCompletedAreZero = () => <RecommendationsStory data={lastRunLastCompletedAreZeroData} />;

export const lastRunIsNotZeroLastCompletedIsZero = () => (
  <RecommendationsStory data={lastRunIsNotZeroLastCompletedIsZeroData} />
);

export const limited = () => <RecommendationsStory data={limitedData} />;

export const allGood = () => <RecommendationsStory data={allGoodData} />;

export const onlyDismissed = () => {
  const { optimizations: _, ...rest } = basicDataWithDismissed;
  const updatedData = { ...rest, optimizations: {} };
  return <RecommendationsStory data={updatedData} />;
};
