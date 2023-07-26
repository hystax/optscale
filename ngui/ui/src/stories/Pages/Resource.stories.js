import React from "react";
import Resource from "components/Resource";
import { KINDS, MOCKED_RESOURCE_ID } from "stories";

export default {
  title: `${KINDS.PAGES}/Resource`,
  argTypes: {
    isGetResourceLoading: { name: "Get resource loading", control: "boolean", defaultValue: false },
    isLoadingPatch: { name: "Loading patch", control: "boolean", defaultValue: false }
  }
};

export const basic = (args) => (
  <Resource
    resource={{
      cloud_account_id: "57a11699-fe34-4cdd-8768-98dae4b39809",
      cloud_resource_id: "i-0436ee72bb653bf8a",
      cloud_account_name: "AWS HQ",
      flavor: "t2.micro",
      meta: {
        stopped_allocated: false,
        last_seen_not_stopped: 1617280562,
        spotted: false,
        security_groups: [{ GroupId: "sg-01e701998068ab9e3", GroupName: "launch-wizard-2" }]
      },
      name: "aqa_us_instance_for_migration",
      region: "us-west-1",
      resource_type: "Instance",
      tags: { purpose: "test", "aws:createdBy": "IAMUser:AIDAILS3JXIC55HPSQVYG:sf-full" },
      last_seen_not_stopped: 1617280562,
      spotted: false,
      stopped_allocated: false,
      pool_id: "145235a3-3add-45c8-bd0e-8e58fe88f15b",
      employee_id: "ba5e5c29-dd7d-4d31-ac28-86fa272614d1",
      pool_name: "Dev",
      pool_purpose: "team",
      recommendations: {
        modules: [
          {
            saving: 1.5839999999999996,
            flavor: "t2.micro",
            current_region: "us-west-1",
            recommended_region: "us-east-2",
            cloud_resource_id: "i-0436ee72bb653bf8a",
            resource_name: "aqa_us_instance_for_migration",
            resource_id: "e72d9e42-6ee8-4aba-9614-649e17c355d8",
            cloud_account_id: "8c63e980-6572-4b36-be82-a2bc59705888",
            cloud_account_name: "AWS HQ",
            cloud_type: "aws_cnr",
            name: "instance_migration"
          },
          {
            saving: 1512.288,
            average_saving: 1513.7913333333333,
            flavor: "t2.micro",
            region: "us-west-1",
            cloud_resource_id: "i-0436ee72bb653bf8a",
            resource_name: "aqa_us_instance_for_migration",
            resource_id: "e72d9e42-6ee8-4aba-9614-649e17c355d8",
            cloud_account_id: "8c63e980-6572-4b36-be82-a2bc59705888",
            cloud_account_name: "AWS HQ",
            cloud_type: "aws_cnr",
            name: "reserved_instances"
          }
        ],
        run_timestamp: 1617972973
      },
      image_id: "ami-021809d9177640a20",
      cloud_console_link:
        "https://console.aws.amazon.com/ec2/v2/home?region=us-west-1#InstanceDetails:instanceId=i-0436ee72bb653bf8a",
      active: true,
      first_seen: 1604620800,
      cloud_created_at: 1604579887,
      constraint_violated: true,
      created_at: 1605280056,
      last_seen: 1618579868,
      deleted_at: 0,
      id: MOCKED_RESOURCE_ID,
      dismissed_recommendations: {},
      dismissed: [],
      details: {
        cloud_type: "aws_cnr",
        cloud_name: "AWS HQ",
        total_cost: 2984.6603534076,
        cost: 449.7560903241,
        forecast: 1499.19,
        service_name: "AmazonEC2",
        region: "us-west-1",
        pool_name: "Dev",
        pool_purpose: "team",
        owner_name: "Cody Potter",
        last_seen: 1617975105,
        first_seen: 1612915200,
        active: true,
        policies: {},
        constraints: {
          ttl: {
            deleted_at: 0,
            id: "cfb0a5b1-7c8e-41a2-bfec-dfda433674bb",
            created_at: 1615370848,
            type: "ttl",
            limit: 1604638800,
            resource_id: MOCKED_RESOURCE_ID,
            organization_id: "a21e69f1-33e9-4aa8-bbcf-023f5cd5b15d"
          }
        }
      }
    }}
    isGetResourceLoading={args.isGetResourceLoading}
    isLoadingPatch={args.isLoadingPatch}
    patchResource={() => console.log("patchResource")}
  />
);

export const cluster = (args) => (
  <Resource
    resource={{
      cloud_account_id: null,
      cloud_resource_id: "some_tag_value",
      created_at: 1616067461,
      deleted_at: 0,
      first_seen: 1615939200,
      meta: {},
      name: null,
      region: null,
      resource_type: "my cluster name",
      tags: {
        some_tag_key: "some_tag_value"
      },
      active: true,
      cloud_console_link: null,
      last_seen: 1617109218,
      organization_id: "5be74ae0-fe96-40b0-b65d-d76d974f6913",
      recommendations: {
        run_timestamp: 1617105818,
        modules: [
          {
            cloud_resource_id:
              "/subscriptions/318bd278-e4ef-4230-9ab4-2ad6a29f578c/resourcegroups/aqa/providers/microsoft.compute/virtualmachines/aqa-stopped-not-deallocated",
            resource_name: "aqa-stopped-not-deallocated",
            resource_id: "a3cce70b-6de3-4c92-b99b-f3fd18b984e9",
            cloud_account_id: "e09d4a90-e30a-4feb-94f3-0d8ed7827fb1",
            cloud_account_name: "test2",
            cloud_type: "azure_cnr",
            cost_in_stopped_state: 6.815600448,
            saving: 17.03900112,
            last_seen_active: 0,
            name: "instances_in_stopped_state_for_a_long_time"
          }
        ]
      },
      id: MOCKED_RESOURCE_ID,
      employee_id: null,
      pool_id: null,
      details: {
        cloud_type: null,
        cloud_name: null,
        total_cost: 6.815600448,
        cost: 6.815600448,
        forecast: 7.04,
        service_name: null,
        region: null,
        pool_name: null,
        pool_purpose: null,
        owner_name: null,
        last_seen: 1617110815,
        first_seen: 1615939200,
        active: true,
        policies: {},
        constraints: {}
      },
      cluster_type_id: "7dfe1891-343b-4603-b086-9ca2fe654b36",
      sub_resources: [
        {
          cloud_account_id: "e09d4a90-e30a-4feb-94f3-0d8ed7827fb1",
          cloud_resource_id:
            "/subscriptions/318bd278-e4ef-4230-9ab4-2ad6a29f578c/resourcegroups/aqa/providers/microsoft.compute/virtualmachines/aqa-stopped-not-deallocated",
          created_at: 1616077461,
          deleted_at: 0,
          first_seen: 1615939200,
          last_seen_not_stopped: 0,
          meta: {
            stopped_allocated: true,
            last_seen_not_stopped: 0,
            spotted: false
          },
          name: "aqa-stopped-not-deallocated",
          region: "Germany West Central",
          resource_type: "Instance",
          stopped_allocated: true,
          tags: {
            purpose: "testing"
          },
          active: true,
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/318bd278-e4ef-4230-9ab4-2ad6a29f578c/resourceGroups/AQA/providers/Microsoft.Compute/virtualMachines/aqa-stopped-not-deallocated/overview",
          flavor: "Standard_B1ms",
          last_seen: 1617109218,
          organization_id: "5be74ae0-fe96-40b0-b65d-d76d974f6913",
          recommendations: {
            run_timestamp: 1617105818,
            modules: [
              {
                cloud_resource_id:
                  "/subscriptions/318bd278-e4ef-4230-9ab4-2ad6a29f578c/resourcegroups/aqa/providers/microsoft.compute/virtualmachines/aqa-stopped-not-deallocated",
                resource_name: "aqa-stopped-not-deallocated",
                resource_id: "a3cce70b-6de3-4c92-b99b-f3fd18b984e9",
                cloud_account_id: "e09d4a90-e30a-4feb-94f3-0d8ed7827fb1",
                cloud_account_name: "test2",
                cloud_type: "azure_cnr",
                cost_in_stopped_state: 6.815600448,
                saving: 17.03900112,
                last_seen_active: 0,
                name: "instances_in_stopped_state_for_a_long_time"
              }
            ]
          },
          id: "a3cce70b-6de3-4c92-b99b-f3fd18b984e9",
          employee_id: null,
          pool_id: null,
          dismissed_recommendations: {},
          dismissed: [],
          details: {
            cloud_type: "azure_cnr",
            cloud_name: "test2",
            total_cost: 6.815600448,
            cost: 6.815600448,
            forecast: 7.04,
            service_name: "Microsoft.Compute",
            region: "Germany West Central",
            pool_name: null,
            pool_purpose: null,
            owner_name: null,
            last_seen: 1617110815,
            first_seen: 1615939200,
            active: true,
            policies: {},
            constraints: {}
          },
          cluster_id: MOCKED_RESOURCE_ID
        }
      ]
    }}
    isGetResourceLoading={args.isGetResourceLoading}
    isLoadingPatch={args.isLoadingPatch}
    patchResource={() => console.log("patchResource")}
  />
);

export const clusterDependent = (args) => (
  <Resource
    resource={{
      cluster_id: "11111111-fe34-4cdd-8768-98dae4b39809",
      cloud_account_id: "57a11699-fe34-4cdd-8768-98dae4b39809",
      cloud_resource_id: "i-0436ee72bb653bf8a",
      cloud_account_name: "AWS HQ",
      flavor: "t2.micro",
      meta: {
        stopped_allocated: false,
        last_seen_not_stopped: 1617280562,
        spotted: false,
        security_groups: [{ GroupId: "sg-01e701998068ab9e3", GroupName: "launch-wizard-2" }]
      },
      name: "aqa_us_instance_for_migration",
      region: "us-west-1",
      resource_type: "Instance",
      tags: { purpose: "test", "aws:createdBy": "IAMUser:AIDAILS3JXIC55HPSQVYG:sf-full" },
      last_seen_not_stopped: 1617280562,
      spotted: false,
      stopped_allocated: false,
      pool_id: "145235a3-3add-45c8-bd0e-8e58fe88f15b",
      employee_id: "ba5e5c29-dd7d-4d31-ac28-86fa272614d1",
      pool_name: "Dev",
      pool_purpose: "team",
      recommendations: {
        modules: [
          {
            saving: 1.5839999999999996,
            flavor: "t2.micro",
            current_region: "us-west-1",
            recommended_region: "us-east-2",
            cloud_resource_id: "i-0436ee72bb653bf8a",
            resource_name: "aqa_us_instance_for_migration",
            resource_id: "e72d9e42-6ee8-4aba-9614-649e17c355d8",
            cloud_account_id: "8c63e980-6572-4b36-be82-a2bc59705888",
            cloud_account_name: "AWS HQ",
            cloud_type: "aws_cnr",
            name: "instance_migration"
          },
          {
            saving: 1512.288,
            average_saving: 1513.7913333333333,
            flavor: "t2.micro",
            region: "us-west-1",
            cloud_resource_id: "i-0436ee72bb653bf8a",
            resource_name: "aqa_us_instance_for_migration",
            resource_id: "e72d9e42-6ee8-4aba-9614-649e17c355d8",
            cloud_account_id: "8c63e980-6572-4b36-be82-a2bc59705888",
            cloud_account_name: "AWS HQ",
            cloud_type: "aws_cnr",
            name: "reserved_instances"
          }
        ],
        run_timestamp: 1617972973
      },
      image_id: "ami-021809d9177640a20",
      cloud_console_link:
        "https://console.aws.amazon.com/ec2/v2/home?region=us-west-1#InstanceDetails:instanceId=i-0436ee72bb653bf8a",
      active: true,
      first_seen: 1604620800,
      cloud_created_at: 1604579887,
      constraint_violated: true,
      created_at: 1605280056,
      last_seen: 1618579868,
      deleted_at: 0,
      id: MOCKED_RESOURCE_ID,
      dismissed_recommendations: {},
      dismissed: [],
      details: {
        cloud_type: "aws_cnr",
        cloud_name: "AWS HQ",
        total_cost: 2984.6603534076,
        cost: 449.7560903241,
        forecast: 1499.19,
        service_name: "AmazonEC2",
        region: "us-west-1",
        pool_name: "Dev",
        pool_purpose: "team",
        owner_name: "Cody Potter",
        last_seen: 1617975105,
        first_seen: 1612915200,
        active: true,
        policies: {},
        constraints: {
          ttl: {
            deleted_at: 0,
            id: "cfb0a5b1-7c8e-41a2-bfec-dfda433674bb",
            created_at: 1615370848,
            type: "ttl",
            limit: 1604638800,
            resource_id: MOCKED_RESOURCE_ID,
            organization_id: "a21e69f1-33e9-4aa8-bbcf-023f5cd5b15d"
          }
        }
      }
    }}
    isGetResourceLoading={args.isGetResourceLoading}
    isLoadingPatch={args.isLoadingPatch}
    patchResource={() => console.log("patchResource")}
  />
);
