import ResourceLimitHits from "components/ResourceLimitHits";
import React from "react";

export default {
  title: "Components/ResourceLimitHits"
};

const limitHits = [
  {
    deleted_at: 0,
    state: "red",
    id: "5c0e0a94-8159-4bac-8d01-de3bc8a288b6",
    created_at: 1617345628,
    resource_id: "14d75330-c111-482a-97d0-0fe4b3b7125c",
    pool_id: "6731a6ef-7b52-44ed-bc69-a137c36f8840",
    type: "ttl",
    constraint_limit: 1585735200,
    hit_value: 1617604830,
    time: 1617345628,
    organization_id: "2a03382a-a036-4881-b6b5-68c08192cc44"
  },
  {
    deleted_at: 0,
    state: "red",
    id: "bece3430-5316-4e1a-9ad6-f8a3aeedf72b",
    created_at: 1606312457,
    resource_id: "14d75330-c111-482a-97d0-0fe4b3b7125c",
    pool_id: null,
    type: "daily_expense_limit",
    constraint_limit: 1000,
    hit_value: 203128,
    time: 1606312456,
    organization_id: "2a03382a-a036-4881-b6b5-68c08192cc44"
  },
  {
    deleted_at: 0,
    state: "green",
    id: "bece3430-5316-4e1a-9ad6-f8a3aeedf72b",
    created_at: 1606312457,
    resource_id: "14d75330-c111-482a-97d0-0fe4b3b7125c",
    pool_id: null,
    type: "total_expense_limit",
    constraint_limit: 1000,
    hit_value: 203128,
    time: 1606312456,
    organization_id: "2a03382a-a036-4881-b6b5-68c08192cc44"
  },
  {
    deleted_at: 0,
    state: "red",
    id: "d70706b6-3bc8-4880-b227-efcb2def4ab3",
    created_at: 1617605121,
    resource_id: "14d75330-c111-482a-97d0-0fe4b3b7125c",
    pool_id: null,
    type: "ttl",
    constraint_limit: 1617605040,
    hit_value: 1617636927,
    time: 1617605121,
    organization_id: "2a03382a-a036-4881-b6b5-68c08192cc44"
  }
];

export const basic = () => <ResourceLimitHits limitHits={limitHits} />;
