import React from "react";
import ResourceLifecycleGlobalPoolPolicies from "components/ResourceLifecycleGlobalPoolPolicies/ResourceLifecycleGlobalPoolPolicies";

const mockedData = [
  {
    deleted_at: 0,
    id: "71f9de03-d9d9-42ff-89a1-5b8bfb22395d",
    created_at: 1608967732,
    type: "ttl",
    limit: 10,
    active: true,
    pool_id: "749aaa76-29ad-4ca9-a67a-3b079873197d",
    organization_id: "dc31d34a-8684-42a3-88c7-fb0877b94eae",
    details: {
      deleted_at: 0,
      id: "749aaa76-29ad-4ca9-a67a-3b079873197d",
      created_at: 1593249058,
      limit: 39750,
      name: "Engineering",
      organization_id: "dc31d34a-8684-42a3-88c7-fb0877b94eae",
      parent_id: "80d53906-6fbd-424a-bbc8-2faea012110f",
      purpose: "business_unit",
      default_owner_id: "48c2bf0f-e6c0-4060-93ff-c04c3599ac20",
      default_owner_name: "Charlie Skywalker",
      unallocated_limit: 26765
    }
  },
  {
    deleted_at: 0,
    id: "df1da970-a265-431b-8dc6-f92ad6d438cc",
    created_at: 1601034524,
    type: "ttl",
    limit: 1,
    active: true,
    pool_id: "80d53906-6fbd-424a-bbc8-2faea012110f",
    organization_id: "dc31d34a-8684-42a3-88c7-fb0877b94eae",
    details: {
      deleted_at: 0,
      id: "80d53906-6fbd-424a-bbc8-2faea012110f",
      created_at: 1651150666,
      limit: 63600,
      name: "Sunflower Inc",
      organization_id: "dc31d34a-8684-42a3-88c7-fb0877b94eae",
      parent_id: null,
      purpose: "business_unit",
      default_owner_id: "b09bcb1a-ad62-4eee-8283-bcc7b7e5b61d",
      default_owner_name: "Demo User",
      unallocated_limit: 18179
    }
  },
  {
    deleted_at: 0,
    id: "0223f9a6-787d-430f-9273-4a284e55644a",
    created_at: 1607769019,
    type: "ttl",
    limit: 5,
    active: true,
    pool_id: "9dc1d4a1-f8fc-4934-8352-f8d1c89478e1",
    organization_id: "dc31d34a-8684-42a3-88c7-fb0877b94eae",
    details: {
      deleted_at: 0,
      id: "9dc1d4a1-f8fc-4934-8352-f8d1c89478e1",
      created_at: 1593264683,
      limit: 2915,
      name: "Daily checks",
      organization_id: "dc31d34a-8684-42a3-88c7-fb0877b94eae",
      parent_id: "749aaa76-29ad-4ca9-a67a-3b079873197d",
      purpose: "cicd",
      default_owner_id: "60b5c2ec-dd76-4e5b-8a2e-1c932396829d",
      default_owner_name: "Luke Roberts",
      unallocated_limit: 2915
    }
  },
  {
    deleted_at: 0,
    id: "16973156-9897-41ba-9b24-b590a48d3ac9",
    created_at: 1599547950,
    type: "ttl",
    limit: 5,
    active: false,
    pool_id: "bd716212-9314-4990-8912-dc807962a576",
    organization_id: "dc31d34a-8684-42a3-88c7-fb0877b94eae",
    details: {
      deleted_at: 0,
      id: "bd716212-9314-4990-8912-dc807962a576",
      created_at: 1593264667,
      limit: 3710,
      name: "QA",
      organization_id: "dc31d34a-8684-42a3-88c7-fb0877b94eae",
      parent_id: "749aaa76-29ad-4ca9-a67a-3b079873197d",
      purpose: "team",
      default_owner_id: "a2459c67-d6f0-4131-83d5-1393f59cb8a1",
      default_owner_name: "Ellie Black",
      unallocated_limit: 1325
    }
  }
];

const ResourceLifecycleGlobalPoolPoliciesContainerMocked = () => (
  <ResourceLifecycleGlobalPoolPolicies isLoading={false} poolPolicies={mockedData} />
);

export default ResourceLifecycleGlobalPoolPoliciesContainerMocked;
