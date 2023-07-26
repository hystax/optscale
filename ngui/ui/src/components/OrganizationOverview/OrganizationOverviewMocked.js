import React from "react";
import { MOCKED_ORGANIZATION_POOL_ID } from "stories";
import OrganizationOverview from "./OrganizationOverview";

const OrganizationOverviewMocked = () => (
  <OrganizationOverview
    isLoadingProps={{
      isGetPoolDataReady: true
    }}
    pool={{
      parent_id: null,
      unallocated_limit: 100000,
      forecast: 48948.14,
      savings: 5843.14,
      cost: 9473.83,
      id: MOCKED_ORGANIZATION_POOL_ID,
      organization_id: "2a03382a-a036-4881-b6b5-68c08192cc44",
      default_owner_name: "Sally Wong",
      purpose: "business_unit",
      default_owner_id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
      deleted_at: 0,
      created_at: 1593160378,
      tags: "{}",
      limit: 180000,
      name: "Sunflower corporation",
      email: null,
      children: [
        {
          name: "Marketing",
          deleted_at: 0,
          created_at: 1593162650,
          unallocated_limit: 15000,
          default_owner_name: "Ava Davies",
          tags: "{}",
          cost: 248.85,
          id: "70db3052-0583-4852-bd2a-8067f88df245",
          email: null,
          default_owner_id: "8886a4df-37f1-4598-aa92-c39eae9567d4",
          parent_id: MOCKED_ORGANIZATION_POOL_ID,
          forecast: 1102.04,
          limit: 15000,
          purpose: "business_unit"
        },
        {
          name: "Engineering",
          deleted_at: 0,
          created_at: 1593162658,
          unallocated_limit: 17700,
          default_owner_name: "Poppy Davies",
          tags: "{}",
          cost: 8885.93,
          id: "7112961c-1225-4022-b529-029bfaee8e07",
          email: null,
          default_owner_id: "015c36f9-5c05-4da8-b445-932560a00191",
          parent_id: MOCKED_ORGANIZATION_POOL_ID,
          forecast: 39351.96,
          limit: 50000,
          purpose: "business_unit"
        },
        {
          name: "Operations",
          deleted_at: 0,
          created_at: 1593178353,
          unallocated_limit: 15000,
          default_owner_name: "Poppy Davies",
          tags: "{}",
          cost: 2040.77,
          id: "ed09b5e9-930e-4c2a-9db9-010dd95e386b",
          email: null,
          default_owner_id: "015c36f9-5c05-4da8-b445-932560a00191",
          parent_id: MOCKED_ORGANIZATION_POOL_ID,
          forecast: 9037.68,
          limit: 15000,
          purpose: "asset_pool"
        },
        {
          name: "QA",
          deleted_at: 0,
          created_at: 1593178267,
          unallocated_limit: 300,
          default_owner_name: "Oscar Walsh",
          tags: "{}",
          cost: 872.01,
          id: "ad70fb29-3ef7-4bc2-8ed1-6110df0bcca6",
          email: null,
          default_owner_id: "c4c3a518-ab9c-4aba-912c-708cc51d9b5e",
          parent_id: "7112961c-1225-4022-b529-029bfaee8e07",
          forecast: 3861.77,
          limit: 1800,
          purpose: "team"
        },
        {
          name: "Ops",
          deleted_at: 0,
          created_at: 1593178283,
          unallocated_limit: 30000,
          default_owner_name: "Taylor Everett",
          tags: "{}",
          cost: 7820.35,
          id: "bc1b73fb-216d-40f9-87cd-b1c1b1255e99",
          email: null,
          default_owner_id: "ab9f39d4-d486-429a-814e-9717a1e12ac7",
          parent_id: "7112961c-1225-4022-b529-029bfaee8e07",
          forecast: 34632.99,
          limit: 30000,
          purpose: "cicd"
        },
        {
          name: "Dev",
          deleted_at: 0,
          created_at: 1593178242,
          unallocated_limit: 500,
          default_owner_name: "Poppy Davies",
          tags: "{}",
          cost: 193.56,
          id: "f6787d54-06bd-4c89-ade0-c1db1ce0e733",
          email: null,
          default_owner_id: "015c36f9-5c05-4da8-b445-932560a00191",
          parent_id: "7112961c-1225-4022-b529-029bfaee8e07",
          forecast: 857.2,
          limit: 500,
          purpose: "team"
        },
        {
          name: "Release 3.4",
          deleted_at: 0,
          created_at: 1596029766,
          unallocated_limit: 1000,
          default_owner_name: "Amy Smith",
          tags: "{}",
          cost: 0,
          id: "1d1a28c6-0ac0-4461-a768-9c80c7e51d85",
          email: null,
          default_owner_id: "5153cb97-94e4-403b-ac9a-8f1343f1fbc5",
          parent_id: "ad70fb29-3ef7-4bc2-8ed1-6110df0bcca6",
          forecast: 0,
          limit: 1000,
          purpose: "project"
        },
        {
          name: "Release 3.5",
          deleted_at: 0,
          created_at: 1599461516,
          unallocated_limit: 500,
          default_owner_name: "Amy Smith",
          tags: "{}",
          cost: 0,
          id: "81bf3c3c-fcf9-4985-a61f-83f8a9be2852",
          email: null,
          default_owner_id: "5153cb97-94e4-403b-ac9a-8f1343f1fbc5",
          parent_id: "ad70fb29-3ef7-4bc2-8ed1-6110df0bcca6",
          forecast: 0,
          limit: 500,
          purpose: "project"
        }
      ]
    }}
  />
);

export default OrganizationOverviewMocked;
