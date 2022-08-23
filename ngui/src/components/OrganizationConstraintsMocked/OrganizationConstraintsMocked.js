import React from "react";
import PropTypes from "prop-types";
import { useLocation } from "react-router-dom";
import OrganizationConstraints from "components/OrganizationConstraints/OrganizationConstraints";
import { QUOTAS_AND_BUDGETS, TAGGING_POLICIES } from "urls";

const mockedData = {
  [TAGGING_POLICIES]: [
    {
      deleted_at: 0,
      id: "c6856397-6831-4871-bc9c-750cc5234f6a",
      created_at: 1650969977,
      name: " QA resources tagging policy",
      organization_id: "07fd4b45-836d-42fe-8e31-0f7272f65dd5",
      type: "tagging_policy",
      definition: {
        conditions: {
          tag: "aqa_uuid",
          without_tag: "aqa"
        },
        start_date: 1648897200
      },
      filters: {
        active: [true],
        cloud_account: [
          {
            id: "2ceda346-26af-478c-bd9b-d1293e33dfae",
            name: "Azure QA",
            type: "azure_cnr"
          }
        ]
      },
      last_run: 1651064162
    },
    {
      deleted_at: 0,
      id: "f2cde2f3-c567-4cf1-a29b-0358eebefa8e",
      created_at: 1650971453,
      name: "Bucket tagging policy",
      organization_id: "07fd4b45-836d-42fe-8e31-0f7272f65dd5",
      type: "tagging_policy",
      definition: {
        conditions: {
          tag: "00000000-0000-0000-0000-000000000000"
        },
        start_date: 1648898100
      },
      filters: {
        resource_type: [
          {
            name: "Bucket",
            type: "regular"
          }
        ],
        active: [true],
        cloud_account: [
          {
            id: "32f4375a-dead-45e0-9f70-0635ff0f6b23",
            name: "AWS HQ",
            type: "aws_cnr"
          }
        ]
      },
      last_run: 1651064162
    }
  ],
  [QUOTAS_AND_BUDGETS]: [
    {
      deleted_at: 0,
      id: "7da10e98-b5c7-4e9f-ae31-465dac9a21a9",
      created_at: 1650519645,
      name: "Buckets count in us-east-1",
      organization_id: "dc31d34a-8684-42a3-88c7-fb0877b94eae",
      type: "resource_quota",
      definition: {
        max_value: 3
      },
      filters: {
        region: [
          {
            name: "us-east-1",
            cloud_type: "aws_cnr"
          }
        ],
        resource_type: [
          {
            name: "Bucket",
            type: "regular"
          }
        ]
      },
      last_run: 1651064162
    },
    {
      deleted_at: 0,
      id: "87dc4416-8edb-4440-ab41-d34dd60b69c1",
      created_at: 1650454091,
      name: "Monthly S3 expenses quota",
      organization_id: "dc31d34a-8684-42a3-88c7-fb0877b94eae",
      type: "recurring_budget",
      definition: {
        monthly_budget: 5300
      },
      filters: {
        service_name: [
          {
            name: "AmazonS3",
            cloud_type: "aws_cnr"
          }
        ]
      },
      last_run: 1651064162
    },
    {
      deleted_at: 0,
      id: "d20de4c9-0c54-4eaf-8eb2-969e3241c1d1",
      created_at: 1650386255,
      name: "Buckets count in eu-west-2",
      organization_id: "dc31d34a-8684-42a3-88c7-fb0877b94eae",
      type: "resource_quota",
      definition: {
        max_value: 10
      },
      filters: {
        region: [
          {
            name: "eu-west-2",
            cloud_type: "aws_cnr"
          }
        ],
        resource_type: [
          {
            name: "Bucket",
            type: "regular"
          }
        ]
      },
      last_run: 1651064162
    },
    {
      deleted_at: 0,
      id: "fb8b7985-0cc4-4ba6-b752-4892fbaaf775",
      created_at: 1650523436,
      name: "Environments total budget",
      organization_id: "dc31d34a-8684-42a3-88c7-fb0877b94eae",
      type: "expiring_budget",
      definition: {
        total_budget: 2650,
        start_date: 1646203500
      },
      filters: {
        pool: [
          {
            id: "e67869b2-035e-440a-8d54-bd91b86a4a48",
            name: "Environment",
            purpose: "budget"
          }
        ]
      },
      last_run: 1651064162
    }
  ]
};

const OrganizationConstraintsMocked = ({ actionBarDefinition }) => {
  const { pathname } = useLocation();
  const constraints = mockedData[pathname] || mockedData[TAGGING_POLICIES];

  return (
    <OrganizationConstraints
      actionBarDefinition={actionBarDefinition}
      constraints={constraints}
      isLoading={false}
      addButtonLink={""}
    />
  );
};

OrganizationConstraintsMocked.propTypes = {
  actionBarDefinition: PropTypes.object.isRequired
};

export default OrganizationConstraintsMocked;
