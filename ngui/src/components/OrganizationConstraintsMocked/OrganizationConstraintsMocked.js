import React from "react";
import PropTypes from "prop-types";
import { useLocation } from "react-router-dom";
import OrganizationConstraints from "components/OrganizationConstraints/OrganizationConstraints";
import { ANOMALIES, QUOTAS_AND_BUDGETS, TAGGING_POLICIES } from "urls";

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
  ],
  [ANOMALIES]: [
    {
      deleted_at: 0,
      id: "4decea30-a86e-4d17-812c-eb3b4d5b500e",
      created_at: 1658576668,
      name: "AWS/Engineering policy",
      organization_id: "f5e43ac0-87b0-4a81-8eba-b6e4f6324879",
      type: "expense_anomaly",
      definition: {
        threshold_days: 4,
        threshold: 10
      },
      filters: {
        cloud_account: [
          {
            id: "be176e7c-e233-4225-9fef-6df899567875",
            name: "AWS HQ",
            type: "aws_cnr"
          }
        ],
        pool: [
          {
            id: "8ac078ee-69cb-43d3-9814-41d21280ecbf+",
            name: "Engineering",
            purpose: "business_unit"
          }
        ]
      },
      last_run: 1660285844,
      last_run_result: {
        average: 14.0827872279,
        today: 0,
        breakdown: {
          1659916800: 18.5225175343,
          1660003200: 16.339856684600004,
          1660089600: 12.989782186100001,
          1660176000: 8.478992506600001
        }
      },
      limit_hits: []
    },
    {
      deleted_at: 0,
      id: "9762943f-5536-4b52-8515-ffc891e45b1b",
      created_at: 1648020282,
      name: "Instance count",
      organization_id: "f5e43ac0-87b0-4a81-8eba-b6e4f6324879",
      type: "resource_count_anomaly",
      definition: {
        threshold_days: 7,
        threshold: 20
      },
      filters: {
        resource_type: [
          {
            name: "Instance",
            type: "regular"
          }
        ]
      },
      last_run: 1660285844,
      last_run_result: {
        average: 62,
        today: 44,
        breakdown: {
          1659657600: 49,
          1659744000: 49,
          1659830400: 49,
          1659916800: 65,
          1660003200: 94,
          1660089600: 79,
          1660176000: 49
        }
      },
      limit_hits: [
        {
          deleted_at: 0,
          id: "d9dcd862-7260-4b61-a28f-4b7d0a18a056",
          organization_id: "f5e43ac0-87b0-4a81-8eba-b6e4f6324879",
          constraint_id: "9762943f-5536-4b52-8515-ffc891e45b1b",
          constraint_limit: 57.5714,
          value: 78,
          created_at: 1660138812,
          run_result: {
            average: 57.57142857142857,
            today: 78,
            breakdown: {
              1659484800: 49,
              1659571200: 48,
              1659657600: 49,
              1659744000: 49,
              1659830400: 49,
              1659916800: 65,
              1660003200: 94
            }
          }
        }
      ]
    },
    {
      deleted_at: 0,
      id: "d1ec25ab-aa71-4313-8541-6b0cca90bb99",
      created_at: 1648023435,
      name: "Marketing expenses",
      organization_id: "f5e43ac0-87b0-4a81-8eba-b6e4f6324879",
      type: "expense_anomaly",
      definition: {
        threshold_days: 30,
        threshold: 10
      },
      filters: {
        pool: [
          {
            id: "f85a2ef0-0c03-41f2-9973-a6057076516b+",
            name: "Marketing",
            purpose: "business_unit"
          }
        ]
      },
      last_run: 1660285844,
      last_run_result: {
        average: 0.06362612984333335,
        today: 0,
        breakdown: {
          1657670400: 0.0676947153,
          1657756800: 0.06636138200000001,
          1657843200: 0.06636138200000001,
          1657929600: 0.06636138200000001,
          1658016000: 0.06636138200000001,
          1658102400: 0.06636133200000001,
          1658188800: 0.06422037,
          1658275200: 0.06422027,
          1658361600: 0.06422027,
          1658448000: 0.06422027,
          1658534400: 0.06422027,
          1658620800: 0.06422027,
          1658707200: 0.06422027,
          1658793600: 0.06422027,
          1658880000: 0.06422027,
          1658966400: 0.06422027,
          1659052800: 0.06422027,
          1659139200: 0.06400832,
          1659225600: 0.06422027,
          1659312000: 0.06422027,
          1659398400: 0.06422027,
          1659484800: 0.06422027,
          1659571200: 0.06422027,
          1659657600: 0.06422027,
          1659744000: 0.06422027,
          1659830400: 0.06422027000000001,
          1659916800: 0.06422027,
          1660003200: 0.06422027,
          1660089600: 0.06422027,
          1660176000: 0.03242796
        }
      },
      limit_hits: []
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
