import React from "react";
import AssignmentRules from "./AssignmentRules";

const rules = {
  rules: [
    {
      priority: 1,
      pool_name: "QA",
      creator_name: "Amelia Black",
      owner_name: null,
      name: "dev-dc for flow",
      organization_id: "941508fc-2338-4716-b945-c227f87261b3",
      owner_id: null,
      id: "d45a5b34-c9ce-405c-a470-bc2e6d136032",
      creator_id: "724fed9e-aa09-4339-a666-63f24133e9c1",
      created_at: 1595703532,
      pool_purpose: "team",
      pool_id: "72976397-9606-48dc-9f85-188849d9cbcc",
      active: true,
      conditions: [{ id: "4e8524ec-ee00-4a41-8537-eb3ff14dd78b", type: "name_ends_with", meta_info: "-integration_dev_dc" }]
    },
    {
      priority: 2,
      pool_name: "QA",
      creator_name: "Amelia Black",
      owner_name: null,
      name: "Test volumes",
      organization_id: "941508fc-2338-4716-b945-c227f87261b3",
      owner_id: null,
      id: "561332e6-f48a-4b8b-b207-37c84981dfa4",
      creator_id: "724fed9e-aa09-4339-a666-63f24133e9c1",
      created_at: 1595704125,
      pool_purpose: "team",
      pool_id: "72976397-9606-48dc-9f85-188849d9cbcc",
      active: true,
      conditions: [
        { id: "4def7fff-9e61-4f58-8041-491bb3b79c76", type: "name_is", meta_info: "sunflower_availability_test_volume" }
      ]
    },
    {
      priority: 3,
      pool_name: "QA",
      creator_name: "Amelia Black",
      owner_name: null,
      name: "Availability agents",
      organization_id: "941508fc-2338-4716-b945-c227f87261b3",
      owner_id: null,
      id: "051997d4-02ac-4c27-a47b-0ec4a54ca61d",
      creator_id: "724fed9e-aa09-4339-a666-63f24133e9c1",
      created_at: 1595703213,
      pool_purpose: "team",
      pool_id: "72976397-9606-48dc-9f85-188849d9cbcc",
      active: true,
      conditions: [
        { id: "73bf0503-6dd5-422d-9a7d-6a9a9e08231a", type: "name_is", meta_info: "sunflower_availability_test_agent" }
      ]
    },
    {
      priority: 4,
      pool_name: "Release 3.4",
      creator_name: "Amelia Black",
      owner_name: null,
      name: "Resources for smoke testing 3.4",
      organization_id: "941508fc-2338-4716-b945-c227f87261b3",
      owner_id: null,
      id: "5cc55c15-f7e8-4d67-ab56-6c74acca7407",
      creator_id: "724fed9e-aa09-4339-a666-63f24133e9c1",
      created_at: 1596757397,
      pool_purpose: "project",
      pool_id: "5bd7803a-408d-4281-9598-4c6095f444b4",
      active: true,
      conditions: [
        { id: "36ec6b00-29c4-4ac2-811c-1a5d1b6a58c5", type: "name_starts_with", meta_info: "sunflower_lily_VA_MGR_AWS_3_4" }
      ]
    },
    {
      priority: 5,
      pool_name: "QA",
      creator_name: "Amelia Black",
      owner_name: null,
      name: "Baget Smokes",
      organization_id: "941508fc-2338-4716-b945-c227f87261b3",
      owner_id: null,
      id: "d94f246b-acb9-4ab9-85f6-d38a738342d7",
      creator_id: "724fed9e-aa09-4339-a666-63f24133e9c1",
      created_at: 1597350671,
      pool_purpose: "team",
      pool_id: "72976397-9606-48dc-9f85-188849d9cbcc",
      active: true,
      conditions: [
        { id: "fcd01848-063b-48e5-956c-ed7c07a58bbd", type: "name_starts_with", meta_info: "baget_smoke_managed__cloud_agent" }
      ]
    },
    {
      priority: 6,
      pool_name: "QA",
      creator_name: "Amelia Black",
      owner_name: null,
      name: "failback_smoke_manag_cloud_agent",
      organization_id: "941508fc-2338-4716-b945-c227f87261b3",
      owner_id: null,
      id: "82b79b60-c761-4747-9fb1-5c4a5355f9da",
      creator_id: "724fed9e-aa09-4339-a666-63f24133e9c1",
      created_at: 1597448755,
      pool_purpose: "team",
      pool_id: "72976397-9606-48dc-9f85-188849d9cbcc",
      active: true,
      conditions: [
        { id: "8464fee2-eabc-4e73-aaf2-5862446ef445", type: "name_starts_with", meta_info: "failback_smoke_manag_cloud_agent" }
      ]
    },
    {
      priority: 7,
      pool_name: "Sunflower Inc",
      creator_name: "Jack Smith",
      owner_name: null,
      name: "Rule for Engineering resources",
      organization_id: "941508fc-2338-4716-b945-c227f87261b3",
      owner_id: null,
      id: "789c8cd7-3108-4208-b296-c8a422bc6850",
      creator_id: "950258f4-9924-4dc3-a900-34bc45933062",
      created_at: 1596059573,
      pool_purpose: "business_unit",
      pool_id: "991097b3-b47f-4c55-b0c8-5e9fad388dc8",
      active: false,
      conditions: [
        {
          id: "4330bb5c-8947-4767-97b6-ce3c6771dd1b",
          type: "tag_is",
          meta_info: '{"key":"orchid_owner_id","value":"9c458a6d-13b4-47d5-b921-b75ee8bf8101"}'
        },
        { id: "55d49bab-4e06-4866-b886-fe53fc725c26", type: "name_starts_with", meta_info: "Engineering" },
        {
          id: "cca32a09-bf7c-4af6-9d98-edf5b70f364c",
          type: "tag_is",
          meta_info: '{"key":"orchid_pool_id","value":"6731a6ef-7b52-44ed-bc69-a137c36f8840"}'
        }
      ]
    }
  ]
};

const AssignmentRulesMocked = () => <AssignmentRules rules={rules} entities={{}} onUpdatePriority={() => {}} />;

export default AssignmentRulesMocked;
