import DashboardGridLayout from "components/DashboardGridLayout";
import OrganizationConstraintsCard from "components/OrganizationConstraintsCard";
import OrganizationExpenses from "components/OrganizationExpenses";
import PageContentWrapper from "components/PageContentWrapper";
import RecentModelsCard from "components/RecentModelsCard";
import RecentTasksCard from "components/RecentTasksCard";
import RecommendationsCard from "components/RecommendationsCard";
import TopResourcesExpensesCard from "components/TopResourcesExpensesCard";
import { MOCKED_ORGANIZATION_POOL_ID } from "stories";
import { getLastMonthRange, millisecondsToSeconds, subMinutes } from "utils/datetime";

const cleanExpenses = [
  {
    resource_id: "672211a0-d08e-452d-880f-7d815b3c4d48",
    id: "672211a0-d08e-452d-880f-7d815b3c4d48",
    resource_type: "Instance",
    active: false,
    pool: {
      purpose: "business_unit",
      id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
      name: "Engineering"
    },
    region: "eu-central-1",
    owner: {
      id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
      name: "Amy Smith"
    },
    cloud_account_type: "aws_cnr",
    service_name: "AmazonEC2",
    cloud_resource_id: "i-0307c865e6f4f379f",
    cloud_account_id: "8c63e980-6572-4b36-be82-a2bc59705888",
    cloud_account_name: "AWS HQ",
    resource_name: "sunflower-us-east-2",
    cost: 22.5719317827
  },
  {
    resource_id: "3dd84f76-b16b-48e1-a22b-a6078a1c4ba4",
    id: "3dd84f76-b16b-48e1-a22b-a6078a1c4ba4",
    resource_type: "Instance",
    active: true,
    pool: {
      purpose: "business_unit",
      id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
      name: "Engineering"
    },
    region: "DE Zone 1",
    owner: {
      id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
      name: "Marie Briggs"
    },
    cloud_account_type: "azure_cnr",
    service_name: "Microsoft.Compute",
    cloud_resource_id:
      "/subscriptions/318bd278-e4ef-4230-9ab4-2ad6a29f578c/resourcegroups/ishtestgroup/providers/microsoft.compute/virtualmachines/spottest",
    cloud_account_id: "11fddd0e-3ece-410c-8e68-003abcc44576",
    cloud_account_name: "Azure trial",
    resource_name: "spottest",
    cost: 14.5
  },
  {
    resource_id: "258804b8-e684-42b9-a148-21795e749168",
    id: "258804b8-e684-42b9-a148-21795e749168",
    resource_type: "Instance",
    active: true,
    pool: {
      purpose: "team",
      id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
      name: "QA"
    },
    region: "eu-central-1",
    owner: {
      id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
      name: "Katy Ali"
    },
    cloud_account_type: "aws_cnr",
    service_name: "AmazonEC2",
    cloud_resource_id: "i-0701429a26d0d574c",
    cloud_account_id: "8c63e980-6572-4b36-be82-a2bc59705888",
    cloud_account_name: "AWS HQ",
    resource_name: "sunflower-us-east-1",
    cost: 28.7082291744
  },
  {
    resource_id: "c955ea30-349e-4fd1-8764-c766e676fd7a",
    id: "c955ea30-349e-4fd1-8764-c766e676fd7a",
    resource_type: "Instance",
    active: true,
    pool: {
      purpose: "business_unit",
      id: "8ce779dc-cc2a-4210-9770-00a2ce7ccf39",
      name: "Marketing"
    },
    region: "eu-central-1",
    owner: {
      id: "015c36f9-5c05-4da8-b445-932560a00191",
      name: "Sally Wong"
    },
    cloud_account_type: "aws_cnr",
    service_name: "AmazonEC2",
    cloud_resource_id: "i-095a8e515029f5153",
    cloud_account_id: "8c63e980-6572-4b36-be82-a2bc59705888",
    cloud_account_name: "AWS HQ",
    resource_name: "mail-server",
    cost: 24.639862891499998
  },
  {
    resource_id: "eb9c3b77-d5e6-48f8-b1f5-0a9c7a92e44a",
    id: "eb9c3b77-d5e6-48f8-b1f5-0a9c7a92e44a",
    resource_type: "Instance",
    active: false,
    pool: {
      purpose: "team",
      id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
      name: "Dev"
    },
    region: "eu-central-1",
    owner: {
      id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
      name: "Ella Price"
    },
    cloud_account_type: "aws_cnr",
    service_name: "AmazonEC2",
    cloud_resource_id: "i-041a8aaca5347338a",
    cloud_account_id: "8c63e980-6572-4b36-be82-a2bc59705888",
    cloud_account_name: "AWS HQ",
    resource_name: "jenkins-worker-1",
    cost: 24.6400322778
  }
].sort(({ cost: a }, { cost: b }) => b - a);

const getOrganizationExpenses = () => {
  const todayUnix = millisecondsToSeconds(+new Date());
  const lastMonthRangeEndUnix = getLastMonthRange(true).end;

  return {
    expenses: {
      this_month: {
        total: 118080.90259006835,
        date: todayUnix
      },
      this_month_forecast: {
        total: 141080.9,
        date: todayUnix
      },
      last_month: {
        total: 169000.02920730546,
        date: lastMonthRangeEndUnix
      }
    },
    total: 160000,
    pools: [
      {
        this_month_forecast: 118546.9,
        name: "Sunflower corporation",
        purpose: "business_unit",
        pool: 160000,
        this_month_expenses: 95546.0502165,
        id: MOCKED_ORGANIZATION_POOL_ID
      }
    ]
  };
};

const constraints = [
  {
    deleted_at: 0,
    id: "76fd955e-f627-4ab1-8b4c-2868452bbd80",
    created_at: 1680763589,
    name: "Buckets count in us-east-1",
    organization_id: "1f12f2c0-4103-4d84-a20e-5ddbd9425e48 ",
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
    last_run: 1705495803,
    last_run_result: {
      limit: 3,
      current: 9
    },
    limit_hits: [
      {
        deleted_at: 0,
        id: "1d32136f-b4c3-44ce-b186-79eca740d50c",
        organization_id: "283beada-26ed-4c48-89aa-21765ca8069e",
        constraint_id: "ba6a8f8b-cb53-4070-a905-dac7288d2316",
        constraint_limit: 3,
        value: 9,
        created_at: 1705278617,
        run_result: {
          limit: 3,
          current: 9
        }
      },
      {
        deleted_at: 0,
        id: "17f0f38e-8a2f-4892-b032-121796618582",
        organization_id: "9f9854cd-6718-4633-b266-d6d9ce7ed072",
        constraint_id: "550d4505-2c73-4da2-b55f-b9f4dc771fd3",
        constraint_limit: 3,
        value: 9,
        created_at: 1705368316,
        run_result: {
          limit: 3,
          current: 9
        }
      },
      {
        deleted_at: 0,
        id: "56d38190-c24c-4e3e-83e0-c26761f3267e",
        organization_id: "eef81546-95d6-4f9d-81eb-3eaacf6ad645",
        constraint_id: "a77ae2f4-bdc4-46d1-b1c7-d0fecb9c1f6a",
        constraint_limit: 3,
        value: 9,
        created_at: 1705450816,
        run_result: {
          limit: 3,
          current: 9
        }
      }
    ]
  },
  {
    deleted_at: 0,
    id: "045085bb-bf8d-4759-a796-f39117bb2c4f",
    created_at: 1680763770,
    name: "Monthly S3 expenses quota",
    organization_id: "e318d2e2-b7db-4d68-aa01-f00d31890dcc",
    type: "recurring_budget",
    definition: {
      monthly_budget: 100
    },
    filters: {
      service_name: [
        {
          name: "AmazonS3",
          cloud_type: "aws_cnr"
        }
      ]
    },
    last_run: 1705478713,
    last_run_result: {
      limit: 100,
      current: 161.28690293860004
    },
    limit_hits: []
  },
  {
    deleted_at: 0,
    id: "a3f6f8da-f4b9-427a-881b-cf6818810e5c",
    created_at: 1680764553,
    name: "QA resources tagging policy",
    organization_id: "674cee55-9f47-40a8-869f-574f25b8afba",
    type: "tagging_policy",
    definition: {
      start_date: 1672531200,
      conditions: {
        tag: "aqa_uuid",
        without_tag: "aqa"
      }
    },
    filters: {
      active: [true],
      cloud_account: [
        {
          id: "de0c6b2e-d442-4ded-8295-18d720c38ac4",
          name: "Azure QA",
          type: "azure_cnr"
        }
      ]
    },
    last_run: 1705498214,
    last_run_result: {
      value: 15
    },
    limit_hits: [
      {
        deleted_at: 0,
        id: "413d0573-38ec-4d9c-8fdf-825772adc783",
        organization_id: "64c576e3-a0a3-40c4-aee5-a3056363ea95",
        constraint_id: "c02be6ba-c113-44c2-a09f-3cef608a9a4c",
        constraint_limit: 0,
        value: 15,
        created_at: 1705277406,
        run_result: {
          value: 15
        }
      },
      {
        deleted_at: 0,
        id: "3212d7a4-afce-4450-b5c6-77b5b801882a",
        organization_id: "d56dcdf0-5433-4d80-915a-14c20e8de06b",
        constraint_id: "66c11434-bb22-4ac6-a2c0-0bd6e5c607e3",
        constraint_limit: 0,
        value: 15,
        created_at: 1705364411,
        run_result: {
          value: 15
        }
      },
      {
        deleted_at: 0,
        id: "d7b28398-f393-469c-be11-e04cf4653fd4",
        organization_id: "ee73f6ab-d99e-4600-a12e-0d8814d71989",
        constraint_id: "442535e6-57e6-4e5f-88cd-ed74d2c069f8",
        constraint_limit: 0,
        value: 15,
        created_at: 1705450816,
        run_result: {
          value: 15
        }
      }
    ]
  },
  {
    deleted_at: 0,
    id: "6aaa00e3-05e0-4305-a1d7-ebac5cb77bc4",
    created_at: 1680763395,
    name: "Instance count",
    organization_id: "e548f742-1c58-42fb-a858-e236edaef741",
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
    last_run: 1705487411,
    last_run_result: {
      average: 58.857142857142854,
      today: 57,
      breakdown: {
        "1704844800": 60,
        "1704931200": 57,
        "1705017600": 58,
        "1705104000": 60,
        "1705190400": 59,
        "1705276800": 60,
        "1705363200": 58
      }
    },
    limit_hits: []
  },
  {
    deleted_at: 0,
    id: "fb24ff7f-4902-4dd5-bf43-921a9fbc2aa6",
    created_at: 1680763419,
    name: "Marketing expenses",
    organization_id: "a8d7cd92-01cd-4078-b2a6-6ed24b22767a",
    type: "expense_anomaly",
    definition: {
      threshold_days: 30,
      threshold: 10
    },
    filters: {
      pool: [
        {
          id: "c1bfe08c-b8cb-448b-a3c5-d81800f05e41+",
          name: "Marketing",
          purpose: "business_unit"
        }
      ]
    },
    last_run: 1705478713,
    last_run_result: {
      average: 0.7481306436833334,
      today: 0,
      breakdown: {
        "1702857600": 0.7610729634,
        "1702944000": 0.7610467830000001,
        "1703030400": 0.7610712729,
        "1703116800": 0.761094707,
        "1703203200": 0.7610320347000001,
        "1703289600": 0.7610002900999999,
        "1703376000": 0.7610377546,
        "1703462400": 0.7610355477999999,
        "1703548800": 0.7611704073000001,
        "1703635200": 0.7611439121000001,
        "1703721600": 0.7610503184999999,
        "1703808000": 0.7610692886000001,
        "1703894400": 0.7609764653,
        "1703980800": 0.7610528399,
        "1704067200": 0.7610955804000001,
        "1704153600": 0.7610128524000002,
        "1704240000": 0.761031845,
        "1704326400": 0.7611846955000001,
        "1704412800": 0.7610920548,
        "1704499200": 0.7610632714000001,
        "1704585600": 0.7610676481,
        "1704672000": 0.7612101754,
        "1704758400": 0.7612096366000001,
        "1704844800": 0.7611570042,
        "1704931200": 0.7613664352,
        "1705017600": 0.7611901240000001,
        "1705104000": 0.7612058675000002,
        "1705190400": 0.7611413376,
        "1705276800": 0.7611680756000001,
        "1705363200": 0.37186812160000005
      }
    },
    limit_hits: []
  },
  {
    deleted_at: 0,
    id: "58815350-1437-4623-96a1-a38e9cdb2d66",
    created_at: 1680763395,
    name: "Instance count",
    organization_id: "16a39afb-626d-4429-abda-ae1dc45f510c",
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
    last_run: 1705487411,
    last_run_result: {
      average: 58.857142857142854,
      today: 120,
      breakdown: {
        "1704844800": 30,
        "1704931200": 45,
        "1705017600": 23,
        "1705104000": 45,
        "1705190400": 79,
        "1705276800": 20,
        "1705363200": 80
      }
    },
    limit_hits: []
  }
];

const tasks = [
  {
    name: "Digit Recognizer",
    id: "6569a65e-17bc-49e3-8439-44eb9e5f38b6",
    status: "completed",
    last_run: millisecondsToSeconds(+subMinutes(new Date(), 25)),
    last_run_reached_goals: {
      iter: {
        id: "4254aa87-0095-45bc-84e7-139a560d5729",
        tendency: "more",
        target_value: 3,
        name: "Iter",
        value: 57600,
        reached: true
      },
      loss: {
        id: "89b56825-6f37-41bb-9cea-6b5e88d0e416",
        tendency: "less",
        target_value: 1.1,
        name: "Data Loss",
        value: 0.7866795659065247,
        reached: true
      },
      epoch: {
        id: "ba8b5cbb-2e77-4326-91ea-756db9b43270",
        tendency: "less",
        target_value: 9,
        name: "Epochs",
        value: 10,
        reached: false
      }
    }
  },
  {
    name: "House Prices",
    id: "16a17169-7dbc-4557-9101-dbcba713b1d4",
    status: "completed",
    last_run: millisecondsToSeconds(+subMinutes(new Date(), 36)),
    last_run_reached_goals: {
      accuracy: {
        id: "95fded0b-dfdf-4a10-a154-7b2f390739f0",
        tendency: "more",
        target_value: 60,
        name: "Accuracy",
        value: 70.67,
        reached: true
      },
      loss: {
        id: "89b56825-6f37-41bb-9cea-6b5e88d0e416",
        tendency: "less",
        target_value: 1.1,
        name: "Data Loss",
        value: 0.7786335945129395,
        reached: true
      },
      iter: {
        id: "4254aa87-0095-45bc-84e7-139a560d5729",
        tendency: "more",
        target_value: 3,
        name: "Iter",
        value: 57600,
        reached: true
      }
    }
  },
  {
    name: "Flower Classification",
    id: "77d078a6-3381-40a0-8fd3-e6dc4c1b0448",
    status: "completed",
    last_run: millisecondsToSeconds(+subMinutes(new Date(), 42)),
    last_run_reached_goals: {
      iter: {
        id: "4254aa87-0095-45bc-84e7-139a560d5729",
        tendency: "more",
        target_value: 3,
        name: "Iter",
        value: 57600,
        reached: true
      },
      loss: {
        id: "89b56825-6f37-41bb-9cea-6b5e88d0e416",
        tendency: "less",
        target_value: 1.1,
        name: "Data Loss",
        value: 0.7814914584159851,
        reached: true
      },
      accuracy: {
        id: "95fded0b-dfdf-4a10-a154-7b2f390739f0",
        tendency: "more",
        target_value: 60,
        name: "Accuracy",
        value: 70.74000000000001,
        reached: true
      },
      epoch: {
        id: "ba8b5cbb-2e77-4326-91ea-756db9b43270",
        tendency: "less",
        target_value: 9,
        name: "Epochs",
        value: 10,
        reached: false
      }
    }
  }
];

const models = [
  {
    name: "House prices model ",
    description: "Model for House Prices task",
    tags: {
      environment: "staging",
      task: "House Prices"
    },
    key: "houses_prices_model",
    created_at: 1711707203,
    aliased_versions: [
      {
        path: "https://s3.amazonaws.com/ml-bucket/houses_model_7.csv",
        aliases: ["latest"],
        version: "7",
        tags: {
          validation_status: "+"
        },
        deleted_at: 0,
        run_id: "511d178d-3c00-4d07-b764-d8ca2eb5e5c9",
        model_id: "86f6684f-cd42-4e79-aaa6-30e48005740b",
        created_at: 1711976089,
        alias: "latest",
        id: "49cefad5-09b3-41f9-9767-83111bf4d248"
      },
      {
        path: "https://s3.amazonaws.com/ml-bucket/houses_model_6.pkl",
        aliases: ["staging"],
        version: "6",
        tags: {
          validation_status: "+"
        },
        deleted_at: 0,
        run_id: "fec45ced-ed0c-487c-97a2-a926e6fd4467",
        model_id: "86f6684f-cd42-4e79-aaa6-30e48005740b",
        created_at: 1711953447,
        alias: "staging",
        id: "6564da92-e28e-411b-83af-881af824750c"
      },
      {
        path: "https://s3.amazonaws.com/ml-bucket/houses_model_4.pkl",
        aliases: ["prod", "champion"],
        version: "4",
        tags: {
          validation_status: "+"
        },
        deleted_at: 0,
        run_id: "73e84364-5a59-4c19-add0-d1592e46baea",
        model_id: "86f6684f-cd42-4e79-aaa6-30e48005740b",
        created_at: 1711952367,
        alias: "prod",
        id: "63075ce9-9d8f-4e62-b534-400f1fd0aa2b"
      },
      {
        path: "https://s3.amazonaws.com/ml-bucket/houses_model_4.pkl",
        aliases: ["prod", "champion"],
        version: "4",
        tags: {
          validation_status: "+"
        },
        deleted_at: 0,
        run_id: "73e84364-5a59-4c19-add0-d1592e46baea",
        model_id: "86f6684f-cd42-4e79-aaa6-30e48005740b",
        created_at: 1711952367,
        alias: "champion",
        id: "63075ce9-9d8f-4e62-b534-400f1fd0aa2b"
      }
    ],
    last_version: {
      path: "https://s3.amazonaws.com/ml-bucket/houses_model_7.csv",
      aliases: ["latest"],
      version: "7",
      tags: {
        validation_status: "+"
      },
      deleted_at: 0,
      run_id: "511d178d-3c00-4d07-b764-d8ca2eb5e5c9",
      model_id: "86f6684f-cd42-4e79-aaa6-30e48005740b",
      created_at: 1711976089,
      id: "49cefad5-09b3-41f9-9767-83111bf4d248"
    },
    id: "86f6684f-cd42-4e79-aaa6-30e48005740b"
  },
  {
    name: "Iris model prod",
    description: "Model for Flowers Classification task on prod",
    tags: {
      environment: "production",
      task: "Flowers Classification"
    },
    key: "iris_model_prod",
    created_at: 1711707084,
    aliased_versions: [
      {
        path: "https://s3.amazonaws.com/ml-bucket/iris_model_prod_1.bin",
        aliases: ["champion"],
        version: "Version 1",
        tags: {
          validation_status: "+"
        },
        deleted_at: 0,
        run_id: "e8ab8ed1-94a9-4f5e-b07d-603ed3598a37",
        model_id: "db626a7e-164f-4226-8e2e-9a1951fbcd7b",
        created_at: 1711707697,
        alias: "champion",
        id: "ec6bd4f5-f7ef-4982-bf79-e38415f30f24"
      }
    ],
    last_version: {
      path: "https://s3.amazonaws.com/ml-bucket/iris_model_prod_1.bin",
      aliases: ["champion"],
      version: "Version 1",
      tags: {
        validation_status: "+"
      },
      deleted_at: 0,
      run_id: "e8ab8ed1-94a9-4f5e-b07d-603ed3598a37",
      model_id: "db626a7e-164f-4226-8e2e-9a1951fbcd7b",
      created_at: 1711707697,
      id: "ec6bd4f5-f7ef-4982-bf79-e38415f30f24"
    },
    id: "db626a7e-164f-4226-8e2e-9a1951fbcd7b"
  },
  {
    name: "Iris model testing",
    description: "Model for Flowers Classification task",
    tags: {
      task: "Flower Classification",
      environment: "staging"
    },
    key: "iris_model_testing",
    created_at: 1711698668,
    aliased_versions: [
      {
        path: "https://s3.amazonaws.com/ml-bucket/iris_model_2.pkl",
        aliases: ["champion"],
        version: "Version 2",
        tags: {
          task: "Flowers Classification",
          validation_status: "+"
        },
        deleted_at: 0,
        run_id: "96922c7b-bc80-400a-a846-4ddc8c32b8e0",
        model_id: "c8596b92-5ce1-4647-8e9d-7c0048aff8b6",
        created_at: 1717408535,
        alias: "champion",
        id: "f417eda9-0894-45b5-ac81-21f5da5d9579"
      },
      {
        path: "https://s3.amazonaws.com/ml-bucket/iris_model_1.pkl",
        aliases: ["challenger"],
        version: "Version 1",
        tags: {
          task: "Flower Classification",
          validation_status: "-"
        },
        deleted_at: 0,
        run_id: "4e2c4970-9c44-4823-9d1e-dda297df207d",
        model_id: "c8596b92-5ce1-4647-8e9d-7c0048aff8b6",
        created_at: 1717408063,
        alias: "challenger",
        id: "f49947b8-8d9b-4a95-9d7b-abee390264c7"
      }
    ],
    last_version: {
      path: "https://s3.amazonaws.com/ml-bucket/iris_model_5.pkl",
      aliases: [],
      version: "Version 5",
      tags: {
        validation_status: "+"
      },
      deleted_at: 0,
      run_id: "e352dd33-7742-4019-b0df-0d26a82e8261",
      model_id: "c8596b92-5ce1-4647-8e9d-7c0048aff8b6",
      created_at: 1717410085,
      id: "6f4c4c0a-188a-40c7-9066-02191614a3bb"
    },
    id: "c8596b92-5ce1-4647-8e9d-7c0048aff8b6"
  }
];

const DashboardMocked = () => (
  <PageContentWrapper>
    <DashboardGridLayout
      topResourcesExpensesCard={<TopResourcesExpensesCard cleanExpenses={cleanExpenses} />}
      policiesCard={<OrganizationConstraintsCard constraints={constraints} />}
      organizationExpenses={<OrganizationExpenses data={getOrganizationExpenses()} />}
      recommendationsCard={
        <RecommendationsCard
          possibleMonthlySavings={55108.924360775185}
          costRecommendationsCount={116}
          securityRecommendationsCount={21}
        />
      }
      recentTasksCard={<RecentTasksCard tasks={tasks} />}
      recentModelsCard={<RecentModelsCard models={models} />}
    />
  </PageContentWrapper>
);

export default DashboardMocked;
