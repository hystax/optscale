import ResourceRecommendations from "components/ResourceRecommendations";

export default {
  component: ResourceRecommendations
};

const recommendations = [
  {
    saving: 15.84,
    flavor: "t3.xlarge",
    current_region: "eu-west-1",
    recommended_region: "eu-south-1",
    cloud_resource_id: "i-320bc22927",
    resource_name: "int-dc",
    resource_id: "4cc1117f-0cbc-439b-88e4-fc28fb20a737",
    cloud_account_id: "c46cf66c-84ba-41a7-820c-c2408b923353",
    cloud_account_name: "aws",
    cloud_type: "aws_cnr",
    name: "instance_migration"
  },
  {
    saving: 1.0869047777142857,
    cloud_type: "azure_cnr",
    last_seen_active: 0,
    cloud_resource_id: "i-0562bc6556bf62835",
    resource_name: "centos_a7ef34f3-daa9-711e-18b5-206f5b981600",
    cost_in_stopped_state: 0.7608333444000001,
    resource_id: "4cc1117f-0cbc-439b-88e4-fc28fb20a737",
    cloud_account_id: "c46cf66c-84ba-41a7-820c-c2408b923353",
    cloud_account_name: "azure",
    name: "instances_in_stopped_state_for_a_long_time"
  },
  {
    cloud_resource_id: "snap-9323123124",
    resource_name: "my test snapshot",
    resource_id: "58bef498-9f06-4c0f-aac0-312b22fcb9ee",
    cloud_account_id: "01bcb8f5-85c7-4c3b-823f-800900477eda",
    cloud_account_name: "AWS c-Loud",
    cloud_type: "aws_cnr",
    first_seen: 1600077735,
    last_seen: 1600078565,
    saving: 228,
    region: "ap-northeast-2",
    name: "obsolete_snapshots"
  },
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
    cloud_type: "aws_cnr",
    name: "reserved_instances"
  },
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
    cpu_usage: 0.69,
    name: "rightsizing_instances"
  },
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
    cpu_usage: 0.69,
    name: "rightsizing_rds"
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
    saving: 150,
    name: "short_living_instances"
  },
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
    region: "eu-central-1",
    name: "volumes_not_attached_for_a_long_time"
  },
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
    region: "eu-central-1",
    name: "obsolete_ips"
  },
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
    region: "eu-central-1",
    name: "s3_abandoned_buckets_nebius"
  },
  {
    saving: 5.563254672357,
    cloud_type: "azure_cnr",
    last_seen_active: 0,
    cloud_resource_id:
      "/subscriptions/318bd278-e4ef-4230-9ab4-2ad6a29f578c/resourceGroups/aqa/providers/Microsoft.Network/publicIPAddresses/as_test_opt_ip",
    resource_name: "as_test_opt_ip",
    cost_not_active_ip: 2.546235467233,
    resource_id: "4cc1117f-0cbc-439b-88e4-fc28fb20a737",
    cloud_account_id: "c46cf66c-84ba-41a7-820c-c2408b923353",
    cloud_account_name: "azure cloud account",
    region: "eu-central-1",
    name: "cvos_opportunities"
  }
];

export const allWithBothRateAndUnit = () => (
  <ResourceRecommendations recommendations={recommendations} dismissedRecommendations={recommendations} />
);
