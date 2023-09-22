const { millisecondsToSeconds } = require("utils/datetime");

export const BUCKETS = [
  {
    cloud_account_id: "9d34d88a-8d52-4eca-9dd5-f35fe4876d1d",
    cloud_resource_id: "sunflower-eu-fra",
    applied_rules: [
      {
        id: "55e6f5b5-9261-405e-8e56-a06cd2759a54",
        name: "Rule for AWS HQ_1680757985",
        pool_id: "e327edaa-9f2d-4205-a3f1-e20532cd43d9"
      }
    ],
    employee_id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
    first_seen: 1672531200,
    pool_id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
    region: "us-west-2",
    resource_type: "Bucket",
    service_name: "AmazonS3",
    tags: {
      "aws:createdBy": "IAMUser:AIDAIWGUBPAVMAWKKOLBA:s3-user"
    },
    last_expense: {
      date: 1682899200,
      cost: 0.006650830000000001
    },
    total_cost: 721.8798723085999,
    meta: {
      cloud_console_link: "https://console.aws.amazon.com/s3/buckets/sunflower-eu-fra?region=eu-central-1&tab=objects",
      is_public_policy: false,
      is_public_acls: true
    },
    active: true,
    constraint_violated: true,
    created_at: 1684905197,
    last_seen: 1687762758,
    deleted_at: 0,
    id: "1a7c005c-083b-490f-bdf4-2c2e97fd8596",
    is_environment: false,
    saving: 0,
    cost: 254.86900482779996,
    cloud_account_name: "AWS HQ",
    cloud_account_type: "aws_cnr",
    owner: {
      id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
      name: "Lincoln Morton"
    },
    pool: {
      id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
      name: "AWS HQ",
      purpose: "budget"
    },
    resource_id: "1a7c005c-083b-490f-bdf4-2c2e97fd8596",
    resource_name: "sunflower-eu-fra",
    shareable: false,
    traffic_expenses: [
      {
        from: "us-west-2",
        to: "External",
        usage: 2021.6524389862004,
        cost: 169.9123596588
      },
      {
        from: "us-west-2",
        to: "ap-southeast-1",
        usage: 0.0008995683999999999,
        cost: 0.000017991199999999998
      },
      {
        from: "us-east-1",
        to: "ap-southeast-1",
        usage: 0.0000016876,
        cost: 3.36e-8
      },
      {
        from: "us-west-2",
        to: "eu-west-1",
        usage: 7.7624077274,
        cost: 0.1552481546
      },
      {
        from: "us-west-2",
        to: "us-east-1",
        usage: 0.074371824,
        cost: 0.0014874368
      }
    ],
    "pool/owner": "AWS HQ Lincoln Morton",
    resource: "sunflower-eu-fra sunflower-eu-fra",
    tagsString: "aws:createdBy: IAMUser:AIDAIWGUBPAVMAWKKOLBA:s3-user",
    metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
    locationString: "AWS HQ aws_cnr Region: us-west-2,Service: AmazonS3",
    resourceType: "Bucket"
  },
  {
    cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
    cloud_resource_id:
      "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/lilygoldenimageus2/providers/microsoft.storage/storageaccounts/lilygoldenimageus2diag",
    active: true,
    applied_rules: [
      {
        id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
        name: "Rule for Dev environment_1680757920",
        pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
      }
    ],
    employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
    first_seen: 1672531200,
    meta: {
      cloud_console_link:
        "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/lilyGoldenImageUS2/providers/Microsoft.Storage/storageAccounts/lilygoldenimageus2diag/overview",
      is_public_policy: false,
      is_public_acls: false
    },
    pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
    region: "West US 2",
    resource_type: "Bucket",
    tags: {},
    service_name: "Microsoft.Storage",
    last_expense: {
      date: 1682899200,
      cost: 0.7927370759999999
    },
    total_cost: 96.713911756,
    created_at: 1684905330,
    last_seen: 1687762759,
    deleted_at: 0,
    id: "70bee4fe-eb10-4a7d-8407-ec33feb76126",
    is_environment: false,
    saving: 0,
    cost: 29.436969411999996,
    cloud_account_name: "Dev environment",
    cloud_account_type: "azure_cnr",
    owner: {
      id: "ff368cee-680c-42f4-a3a8-3d629353f554",
      name: "Demo User"
    },
    pool: {
      id: "345cf03f-1049-467b-84b3-4c39c3932896",
      name: "Dev environment",
      purpose: "budget"
    },
    resource_id: "70bee4fe-eb10-4a7d-8407-ec33feb76126",
    resource_name: "lilygoldenimageus2diag",
    shareable: false,
    constraint_violated: false,
    traffic_expenses: [
      {
        from: "westus2",
        to: "North America",
        usage: 0.004320000000000001,
        cost: 0.00008639999999999999
      }
    ],
    "pool/owner": "Dev environment Demo User",
    resource:
      "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/lilygoldenimageus2/providers/microsoft.storage/storageaccounts/lilygoldenimageus2diag lilygoldenimageus2diag",
    tagsString: "",
    metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
    locationString: "Dev environment azure_cnr Region: West US 2,Service: Microsoft.Storage",
    resourceType: "Bucket"
  },
  {
    cloud_account_id: "9d34d88a-8d52-4eca-9dd5-f35fe4876d1d",
    cloud_resource_id: "yv-bucket",
    applied_rules: [
      {
        id: "55e6f5b5-9261-405e-8e56-a06cd2759a54",
        name: "Rule for AWS HQ_1680757985",
        pool_id: "e327edaa-9f2d-4205-a3f1-e20532cd43d9"
      }
    ],
    employee_id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
    first_seen: 1672531200,
    pool_id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
    region: "us-west-2",
    resource_type: "Bucket",
    service_name: "AmazonS3",
    tags: {
      "aws:createdBy": "IAMUser:AIDAILS3JXIC55HPSQVYG:sf-full"
    },
    last_expense: {
      date: 1682899200,
      cost: 0.00646932
    },
    total_cost: 362.22024085239997,
    meta: {
      cloud_console_link: "https://console.aws.amazon.com/s3/buckets/yv-bucket?region=eu-central-1&tab=objects",
      is_public_policy: false,
      is_public_acls: false
    },
    active: true,
    created_at: 1684905197,
    last_seen: 1687762758,
    deleted_at: 0,
    id: "82085696-8795-48c5-803c-8a4bd3c979ea",
    is_environment: false,
    saving: 19.520247625714287,
    cost: 12.8935799502,
    cloud_account_name: "AWS HQ",
    cloud_account_type: "aws_cnr",
    owner: {
      id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
      name: "Lincoln Morton"
    },
    pool: {
      id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
      name: "AWS HQ",
      purpose: "budget"
    },
    resource_id: "82085696-8795-48c5-803c-8a4bd3c979ea",
    resource_name: "yv-bucket",
    shareable: false,
    constraint_violated: false,
    traffic_expenses: [
      {
        from: "us-west-2",
        to: "External",
        usage: 0.1509017578,
        cost: 0.0126827238
      }
    ],
    "pool/owner": "AWS HQ Lincoln Morton",
    resource: "yv-bucket yv-bucket",
    tagsString: "aws:createdBy: IAMUser:AIDAILS3JXIC55HPSQVYG:sf-full",
    metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
    locationString: "AWS HQ aws_cnr Region: us-west-2,Service: AmazonS3",
    resourceType: "Bucket"
  },
  {
    cloud_account_id: "9d34d88a-8d52-4eca-9dd5-f35fe4876d1d",
    cloud_resource_id: "aws-cloudtrail-logs-044478323321-88eecf70",
    applied_rules: [
      {
        id: "55e6f5b5-9261-405e-8e56-a06cd2759a54",
        name: "Rule for AWS HQ_1680757985",
        pool_id: "e327edaa-9f2d-4205-a3f1-e20532cd43d9"
      }
    ],
    employee_id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
    first_seen: 1672531200,
    pool_id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
    region: "eu-west-1",
    resource_type: "Bucket",
    service_name: "AmazonS3",
    tags: {
      "aws:createdBy": "Root:044478323321"
    },
    last_expense: {
      date: 1682899200,
      cost: 0.08845876640000001
    },
    total_cost: 40.617113497,
    meta: {
      cloud_console_link:
        "https://console.aws.amazon.com/s3/buckets/aws-cloudtrail-logs-044478323321-88eecf70?region=eu-west-1&tab=objects",
      is_public_policy: false,
      is_public_acls: false
    },
    active: true,
    created_at: 1684905197,
    last_seen: 1687762758,
    deleted_at: 0,
    id: "100058b3-8dad-496c-9ed7-b3d5c089e99c",
    is_environment: false,
    saving: 0,
    cost: 12.020204510000001,
    cloud_account_name: "AWS HQ",
    cloud_account_type: "aws_cnr",
    owner: {
      id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
      name: "Lincoln Morton"
    },
    pool: {
      id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
      name: "AWS HQ",
      purpose: "budget"
    },
    resource_id: "100058b3-8dad-496c-9ed7-b3d5c089e99c",
    resource_name: "aws-cloudtrail-logs-044478323321-88eecf70",
    shareable: false,
    constraint_violated: false,
    traffic_expenses: [
      {
        from: "eu-west-1",
        to: "ap-northeast-2",
        usage: 0.010274799200000002,
        cost: 0.0002054878
      },
      {
        from: "eu-west-1",
        to: "ap-southeast-2",
        usage: 0.0161730676,
        cost: 0.00032345640000000004
      },
      {
        from: "eu-west-1",
        to: "sa-east-1",
        usage: 0.012021845799999998,
        cost: 0.0002404328
      },
      {
        from: "eu-west-1",
        to: "ap-northeast-3",
        usage: 0.009333807999999999,
        cost: 0.00018666819999999998
      },
      {
        from: "eu-west-1",
        to: "ap-southeast-3",
        usage: 0.0092865494,
        cost: 0.000185725
      },
      {
        from: "eu-west-1",
        to: "ap-southeast-1",
        usage: 0.009641144999999999,
        cost: 0.00019281639999999998
      },
      {
        from: "eu-west-1",
        to: "ap-northeast-1",
        usage: 0.010266058,
        cost: 0.00020531599999999993
      },
      {
        from: "eu-west-1",
        to: "ca-central-1",
        usage: 0.0093819566,
        cost: 0.00018763100000000003
      },
      {
        from: "eu-west-1",
        to: "eu-north-1",
        usage: 0.0093655644,
        cost: 0.0001873052
      },
      {
        from: "eu-west-1",
        to: "us-west-2",
        usage: 0.0239434264,
        cost: 0.0004788726
      },
      {
        from: "eu-west-1",
        to: "us-west-1",
        usage: 0.009838734799999999,
        cost: 0.00019677140000000002
      },
      {
        from: "eu-west-1",
        to: "eu-west-2",
        usage: 0.013179472799999998,
        cost: 0.00026358260000000004
      },
      {
        from: "eu-west-1",
        to: "eu-south-1",
        usage: 0.004891768400000001,
        cost: 0.0000978318
      },
      {
        from: "eu-west-1",
        to: "ap-south-1",
        usage: 0.0119871434,
        cost: 0.00023973700000000004
      },
      {
        from: "eu-west-1",
        to: "eu-west-3",
        usage: 0.009370686999999999,
        cost: 0.0001874064
      },
      {
        from: "eu-west-1",
        to: "us-east-1",
        usage: 0.025368446200000002,
        cost: 0.0005073704
      },
      {
        from: "eu-west-1",
        to: "us-east-2",
        usage: 0.0096585584,
        cost: 0.00019316640000000004
      }
    ],
    "pool/owner": "AWS HQ Lincoln Morton",
    resource: "aws-cloudtrail-logs-044478323321-88eecf70 aws-cloudtrail-logs-044478323321-88eecf70",
    tagsString: "aws:createdBy: Root:044478323321",
    metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
    locationString: "AWS HQ aws_cnr Region: eu-west-1,Service: AmazonS3",
    resourceType: "Bucket"
  },
  {
    cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
    cloud_resource_id:
      "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchidgoldenimageus2/providers/microsoft.storage/storageaccounts/orchidgoldenimageus2",
    active: true,
    applied_rules: [
      {
        id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
        name: "Rule for Dev environment_1680757920",
        pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
      }
    ],
    employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
    first_seen: 1672531200,
    meta: {
      cloud_console_link:
        "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/orchidGoldenImageUS2/providers/Microsoft.Storage/storageAccounts/orchidgoldenimageus2/overview",
      is_public_policy: false,
      is_public_acls: false
    },
    pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
    region: "West US 2",
    resource_type: "Bucket",
    tags: {},
    service_name: "Microsoft.Storage",
    last_expense: {
      date: 1682899200,
      cost: 0.23339784000000002
    },
    total_cost: 29.157781186,
    created_at: 1684905330,
    last_seen: 1687762759,
    deleted_at: 0,
    id: "5e40c606-025d-4b72-b2fb-eb26ada9aa51",
    is_environment: false,
    saving: 0,
    cost: 8.666847014,
    cloud_account_name: "Dev environment",
    cloud_account_type: "azure_cnr",
    owner: {
      id: "ff368cee-680c-42f4-a3a8-3d629353f554",
      name: "Demo User"
    },
    pool: {
      id: "345cf03f-1049-467b-84b3-4c39c3932896",
      name: "Dev environment",
      purpose: "budget"
    },
    resource_id: "5e40c606-025d-4b72-b2fb-eb26ada9aa51",
    resource_name: "orchidgoldenimageus2",
    shareable: false,
    constraint_violated: false,
    traffic_expenses: [
      {
        from: "westus2",
        to: "North America",
        usage: 0.004328000000000001,
        cost: 0.00008655999999999998
      }
    ],
    "pool/owner": "Dev environment Demo User",
    resource:
      "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchidgoldenimageus2/providers/microsoft.storage/storageaccounts/orchidgoldenimageus2 orchidgoldenimageus2",
    tagsString: "",
    metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
    locationString: "Dev environment azure_cnr Region: West US 2,Service: Microsoft.Storage",
    resourceType: "Bucket"
  },
  {
    cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
    cloud_resource_id:
      "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.storage/storageaccounts/aqadiag",
    active: true,
    applied_rules: [
      {
        id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
        name: "Rule for Dev environment_1680757920",
        pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
      }
    ],
    employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
    first_seen: 1672531200,
    meta: {
      cloud_console_link:
        "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/aqa-europe/providers/Microsoft.Storage/storageAccounts/aqadiag/overview",
      is_public_policy: false,
      is_public_acls: false
    },
    pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
    region: "West Europe",
    resource_type: "Bucket",
    tags: {},
    service_name: "Microsoft.Storage",
    last_expense: {
      date: 1682899200,
      cost: 0.21031812
    },
    total_cost: 25.353391458,
    created_at: 1684905330,
    last_seen: 1687762759,
    deleted_at: 0,
    id: "2ebf2837-7302-4bf8-9325-105f159ffb74",
    is_environment: false,
    saving: 0,
    cost: 7.80982866,
    cloud_account_name: "Dev environment",
    cloud_account_type: "azure_cnr",
    owner: {
      id: "ff368cee-680c-42f4-a3a8-3d629353f554",
      name: "Demo User"
    },
    pool: {
      id: "345cf03f-1049-467b-84b3-4c39c3932896",
      name: "Dev environment",
      purpose: "budget"
    },
    resource_id: "2ebf2837-7302-4bf8-9325-105f159ffb74",
    resource_name: "aqadiag",
    shareable: false,
    constraint_violated: false,
    "pool/owner": "Dev environment Demo User",
    resource:
      "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.storage/storageaccounts/aqadiag aqadiag",
    tagsString: "",
    metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
    locationString: "Dev environment azure_cnr Region: West Europe,Service: Microsoft.Storage",
    resourceType: "Bucket"
  },
  {
    cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
    cloud_resource_id:
      "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchid-engineering/providers/microsoft.storage/storageaccounts/orchidengineeringdiag",
    active: true,
    applied_rules: [
      {
        id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
        name: "Rule for Dev environment_1680757920",
        pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
      }
    ],
    employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
    first_seen: 1672531200,
    meta: {
      cloud_console_link:
        "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/orchid-engineering/providers/Microsoft.Storage/storageAccounts/orchidengineeringdiag/overview",
      is_public_policy: false,
      is_public_acls: false
    },
    pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
    region: "West US 2",
    resource_type: "Bucket",
    tags: {},
    service_name: "Microsoft.Storage",
    last_expense: {
      date: 1682899200,
      cost: 0.17345780100000002
    },
    total_cost: 22.066792974000006,
    created_at: 1684905330,
    last_seen: 1687762759,
    deleted_at: 0,
    id: "d3823173-f372-4dfb-9afe-ae355e89f0d4",
    is_environment: false,
    saving: 0,
    cost: 6.706009116,
    cloud_account_name: "Dev environment",
    cloud_account_type: "azure_cnr",
    owner: {
      id: "ff368cee-680c-42f4-a3a8-3d629353f554",
      name: "Demo User"
    },
    pool: {
      id: "345cf03f-1049-467b-84b3-4c39c3932896",
      name: "Dev environment",
      purpose: "budget"
    },
    resource_id: "d3823173-f372-4dfb-9afe-ae355e89f0d4",
    resource_name: "orchidengineeringdiag",
    shareable: false,
    constraint_violated: false,
    "pool/owner": "Dev environment Demo User",
    resource:
      "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchid-engineering/providers/microsoft.storage/storageaccounts/orchidengineeringdiag orchidengineeringdiag",
    tagsString: "",
    metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
    locationString: "Dev environment azure_cnr Region: West US 2,Service: Microsoft.Storage",
    resourceType: "Bucket"
  },
  {
    cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
    cloud_resource_id:
      "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.storage/storageaccounts/aqadiag765",
    active: true,
    applied_rules: [
      {
        id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
        name: "Rule for Dev environment_1680757920",
        pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
      }
    ],
    employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
    first_seen: 1672531200,
    meta: {
      cloud_console_link:
        "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/aqa-europe/providers/Microsoft.Storage/storageAccounts/aqadiag765/overview",
      is_public_policy: false,
      is_public_acls: false
    },
    pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
    region: "West US",
    resource_type: "Bucket",
    tags: {},
    service_name: "Microsoft.Storage",
    last_expense: {
      date: 1682899200,
      cost: 0.149275071
    },
    total_cost: 19.057458491999995,
    created_at: 1684905330,
    last_seen: 1687762759,
    deleted_at: 0,
    id: "3fe6e85c-e716-4f21-bfbf-8624c23ca902",
    is_environment: false,
    saving: 0,
    cost: 5.771115287999999,
    cloud_account_name: "Dev environment",
    cloud_account_type: "azure_cnr",
    owner: {
      id: "ff368cee-680c-42f4-a3a8-3d629353f554",
      name: "Demo User"
    },
    pool: {
      id: "345cf03f-1049-467b-84b3-4c39c3932896",
      name: "Dev environment",
      purpose: "budget"
    },
    resource_id: "3fe6e85c-e716-4f21-bfbf-8624c23ca902",
    resource_name: "aqadiag765",
    shareable: false,
    constraint_violated: false,
    "pool/owner": "Dev environment Demo User",
    resource:
      "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.storage/storageaccounts/aqadiag765 aqadiag765",
    tagsString: "",
    metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
    locationString: "Dev environment azure_cnr Region: West US,Service: Microsoft.Storage",
    resourceType: "Bucket"
  },
  {
    cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
    cloud_resource_id:
      "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/dr-demo-stand/providers/microsoft.storage/storageaccounts/storagerdemostand",
    active: true,
    applied_rules: [
      {
        id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
        name: "Rule for Dev environment_1680757920",
        pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
      }
    ],
    employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
    first_seen: 1672531200,
    meta: {
      cloud_console_link:
        "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/DR-DEMO-STAND/providers/Microsoft.Storage/storageAccounts/storagerdemostand/overview",
      is_public_policy: false,
      is_public_acls: false
    },
    pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
    region: "Germany West Central",
    resource_type: "Bucket",
    tags: {},
    service_name: "Microsoft.Storage",
    last_expense: {
      date: 1682899200,
      cost: 0.071937952
    },
    total_cost: 10.787204683999999,
    created_at: 1684905330,
    last_seen: 1687762759,
    deleted_at: 0,
    id: "f0fa65c7-6d59-457c-8c77-54cc92ac2965",
    is_environment: false,
    saving: 0,
    cost: 2.687917128,
    cloud_account_name: "Dev environment",
    cloud_account_type: "azure_cnr",
    owner: {
      id: "ff368cee-680c-42f4-a3a8-3d629353f554",
      name: "Demo User"
    },
    pool: {
      id: "345cf03f-1049-467b-84b3-4c39c3932896",
      name: "Dev environment",
      purpose: "budget"
    },
    resource_id: "f0fa65c7-6d59-457c-8c77-54cc92ac2965",
    resource_name: "storagerdemostand",
    shareable: false,
    constraint_violated: false,
    traffic_expenses: [
      {
        from: "germanywestcentral",
        to: "northeurope",
        usage: 0.0043440000000000015,
        cost: 0.00008687999999999998
      }
    ],
    "pool/owner": "Dev environment Demo User",
    resource:
      "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/dr-demo-stand/providers/microsoft.storage/storageaccounts/storagerdemostand storagerdemostand",
    tagsString: "",
    metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
    locationString: "Dev environment azure_cnr Region: Germany West Central,Service: Microsoft.Storage",
    resourceType: "Bucket"
  },
  {
    cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
    cloud_resource_id:
      "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/mgr-demo-stand/providers/microsoft.storage/storageaccounts/storagemgrdemostand",
    active: true,
    applied_rules: [
      {
        id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
        name: "Rule for Dev environment_1680757920",
        pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
      }
    ],
    employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
    first_seen: 1672531200,
    meta: {
      cloud_console_link:
        "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/MGR-DEMO-STAND/providers/Microsoft.Storage/storageAccounts/storagemgrdemostand/overview",
      is_public_policy: false,
      is_public_acls: false
    },
    pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
    region: "Germany West Central",
    resource_type: "Bucket",
    tags: {},
    service_name: "Microsoft.Storage",
    last_expense: {
      date: 1682899200,
      cost: 0.071606032
    },
    total_cost: 10.673333763999999,
    created_at: 1684905330,
    last_seen: 1687762759,
    deleted_at: 0,
    id: "694feb6b-0e5e-4d71-b547-610fead4281e",
    is_environment: false,
    saving: 0,
    cost: 2.675488532,
    cloud_account_name: "Dev environment",
    cloud_account_type: "azure_cnr",
    owner: {
      id: "ff368cee-680c-42f4-a3a8-3d629353f554",
      name: "Demo User"
    },
    pool: {
      id: "345cf03f-1049-467b-84b3-4c39c3932896",
      name: "Dev environment",
      purpose: "budget"
    },
    resource_id: "694feb6b-0e5e-4d71-b547-610fead4281e",
    resource_name: "storagemgrdemostand",
    shareable: false,
    constraint_violated: false,
    traffic_expenses: [
      {
        from: "germanywestcentral",
        to: "northeurope",
        usage: 0.004320000000000001,
        cost: 0.00008639999999999999
      }
    ],
    "pool/owner": "Dev environment Demo User",
    resource:
      "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/mgr-demo-stand/providers/microsoft.storage/storageaccounts/storagemgrdemostand storagemgrdemostand",
    tagsString: "",
    metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
    locationString: "Dev environment azure_cnr Region: Germany West Central,Service: Microsoft.Storage",
    resourceType: "Bucket"
  }
];

// export const MOCKED_DATA = Array.from(Array(7), (e, i) => {
//   const getPropsByStatus = (obj) => {
//     if (i === 0) {
//       return {
//         status: "progress"
//       };
//     }

//     if (i === 3 || i === 6) {
//       return {
//         status: "failed",
//         error: "Buckets removed while check was in progress"
//       };
//     }

//     const duplicates = Math.floor(obj.buckets.length * (300 + Math.random() * 500));
//     return {
//       status: "completed",
//       duration: 600 - Math.random() * 400,
//       objects: Math.floor(obj.buckets.length * (3000 + Math.random() * 5000)),
//       duplicates,
//       size: duplicates * (Math.random() * 500 + 1024),
//       saving: duplicates / 10
//     };
//   };

//   const base = {
//     id: i,
//     buckets: BUCKETS.sort(() => 0.5 - Math.random()).slice(0, 1 + Math.floor(Math.random() * BUCKETS.length)),
//     started: millisecondsToSeconds(+new Date()) - 60 * 60 * 24 * i - Math.random() * 60 * 60 * 5 * (i === 0 ? 0.01 : 1)
//   };

//   return { ...base, ...getPropsByStatus(base) };
// });

export const GENERATED_MOCK = [
  {
    id: 0,
    buckets: [
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchid-engineering/providers/microsoft.storage/storageaccounts/orchidengineeringdiag",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/orchid-engineering/providers/Microsoft.Storage/storageAccounts/orchidengineeringdiag/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "West US 2",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.17345780100000002
        },
        total_cost: 22.066792974000006,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "d3823173-f372-4dfb-9afe-ae355e89f0d4",
        is_environment: false,
        saving: 0,
        cost: 6.706009116,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "d3823173-f372-4dfb-9afe-ae355e89f0d4",
        resource_name: "orchidengineeringdiag",
        shareable: false,
        constraint_violated: false,
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchid-engineering/providers/microsoft.storage/storageaccounts/orchidengineeringdiag orchidengineeringdiag",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: West US 2,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.storage/storageaccounts/aqadiag765",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/aqa-europe/providers/Microsoft.Storage/storageAccounts/aqadiag765/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "West US",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.149275071
        },
        total_cost: 19.057458491999995,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "3fe6e85c-e716-4f21-bfbf-8624c23ca902",
        is_environment: false,
        saving: 0,
        cost: 5.771115287999999,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "3fe6e85c-e716-4f21-bfbf-8624c23ca902",
        resource_name: "aqadiag765",
        shareable: false,
        constraint_violated: false,
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.storage/storageaccounts/aqadiag765 aqadiag765",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: West US,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/mgr-demo-stand/providers/microsoft.storage/storageaccounts/storagemgrdemostand",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/MGR-DEMO-STAND/providers/Microsoft.Storage/storageAccounts/storagemgrdemostand/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "Germany West Central",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.071606032
        },
        total_cost: 10.673333763999999,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "694feb6b-0e5e-4d71-b547-610fead4281e",
        is_environment: false,
        saving: 0,
        cost: 2.675488532,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "694feb6b-0e5e-4d71-b547-610fead4281e",
        resource_name: "storagemgrdemostand",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "germanywestcentral",
            to: "northeurope",
            usage: 0.004320000000000001,
            cost: 0.00008639999999999999
          }
        ],
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/mgr-demo-stand/providers/microsoft.storage/storageaccounts/storagemgrdemostand storagemgrdemostand",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: Germany West Central,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/dr-demo-stand/providers/microsoft.storage/storageaccounts/storagerdemostand",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/DR-DEMO-STAND/providers/Microsoft.Storage/storageAccounts/storagerdemostand/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "Germany West Central",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.071937952
        },
        total_cost: 10.787204683999999,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "f0fa65c7-6d59-457c-8c77-54cc92ac2965",
        is_environment: false,
        saving: 0,
        cost: 2.687917128,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "f0fa65c7-6d59-457c-8c77-54cc92ac2965",
        resource_name: "storagerdemostand",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "germanywestcentral",
            to: "northeurope",
            usage: 0.0043440000000000015,
            cost: 0.00008687999999999998
          }
        ],
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/dr-demo-stand/providers/microsoft.storage/storageaccounts/storagerdemostand storagerdemostand",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: Germany West Central,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/lilygoldenimageus2/providers/microsoft.storage/storageaccounts/lilygoldenimageus2diag",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/lilyGoldenImageUS2/providers/Microsoft.Storage/storageAccounts/lilygoldenimageus2diag/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "West US 2",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.7927370759999999
        },
        total_cost: 96.713911756,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "70bee4fe-eb10-4a7d-8407-ec33feb76126",
        is_environment: false,
        saving: 0,
        cost: 29.436969411999996,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "70bee4fe-eb10-4a7d-8407-ec33feb76126",
        resource_name: "lilygoldenimageus2diag",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "westus2",
            to: "North America",
            usage: 0.004320000000000001,
            cost: 0.00008639999999999999
          }
        ],
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/lilygoldenimageus2/providers/microsoft.storage/storageaccounts/lilygoldenimageus2diag lilygoldenimageus2diag",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: West US 2,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "9d34d88a-8d52-4eca-9dd5-f35fe4876d1d",
        cloud_resource_id: "yv-bucket",
        applied_rules: [
          {
            id: "55e6f5b5-9261-405e-8e56-a06cd2759a54",
            name: "Rule for AWS HQ_1680757985",
            pool_id: "e327edaa-9f2d-4205-a3f1-e20532cd43d9"
          }
        ],
        employee_id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
        first_seen: 1672531200,
        pool_id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
        region: "us-west-2",
        resource_type: "Bucket",
        service_name: "AmazonS3",
        tags: {
          "aws:createdBy": "IAMUser:AIDAILS3JXIC55HPSQVYG:sf-full"
        },
        last_expense: {
          date: 1682899200,
          cost: 0.00646932
        },
        total_cost: 362.22024085239997,
        meta: {
          cloud_console_link: "https://console.aws.amazon.com/s3/buckets/yv-bucket?region=eu-central-1&tab=objects",
          is_public_policy: false,
          is_public_acls: false
        },
        active: true,
        created_at: 1684905197,
        last_seen: 1687762758,
        deleted_at: 0,
        id: "82085696-8795-48c5-803c-8a4bd3c979ea",
        is_environment: false,
        saving: 19.520247625714287,
        cost: 12.8935799502,
        cloud_account_name: "AWS HQ",
        cloud_account_type: "aws_cnr",
        owner: {
          id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
          name: "Lincoln Morton"
        },
        pool: {
          id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
          name: "AWS HQ",
          purpose: "budget"
        },
        resource_id: "82085696-8795-48c5-803c-8a4bd3c979ea",
        resource_name: "yv-bucket",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "us-west-2",
            to: "External",
            usage: 0.1509017578,
            cost: 0.0126827238
          }
        ],
        "pool/owner": "AWS HQ Lincoln Morton",
        resource: "yv-bucket yv-bucket",
        tagsString: "aws:createdBy: IAMUser:AIDAILS3JXIC55HPSQVYG:sf-full",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "AWS HQ aws_cnr Region: us-west-2,Service: AmazonS3",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.storage/storageaccounts/aqadiag",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/aqa-europe/providers/Microsoft.Storage/storageAccounts/aqadiag/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "West Europe",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.21031812
        },
        total_cost: 25.353391458,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "2ebf2837-7302-4bf8-9325-105f159ffb74",
        is_environment: false,
        saving: 0,
        cost: 7.80982866,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "2ebf2837-7302-4bf8-9325-105f159ffb74",
        resource_name: "aqadiag",
        shareable: false,
        constraint_violated: false,
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.storage/storageaccounts/aqadiag aqadiag",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: West Europe,Service: Microsoft.Storage",
        resourceType: "Bucket"
      }
    ],
    started: 1687183534.0927637,
    status: "progress"
  },
  {
    id: 1,
    buckets: [
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchid-engineering/providers/microsoft.storage/storageaccounts/orchidengineeringdiag",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/orchid-engineering/providers/Microsoft.Storage/storageAccounts/orchidengineeringdiag/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "West US 2",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.17345780100000002
        },
        total_cost: 22.066792974000006,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "d3823173-f372-4dfb-9afe-ae355e89f0d4",
        is_environment: false,
        saving: 0,
        cost: 6.706009116,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "d3823173-f372-4dfb-9afe-ae355e89f0d4",
        resource_name: "orchidengineeringdiag",
        shareable: false,
        constraint_violated: false,
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchid-engineering/providers/microsoft.storage/storageaccounts/orchidengineeringdiag orchidengineeringdiag",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: West US 2,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "9d34d88a-8d52-4eca-9dd5-f35fe4876d1d",
        cloud_resource_id: "yv-bucket",
        applied_rules: [
          {
            id: "55e6f5b5-9261-405e-8e56-a06cd2759a54",
            name: "Rule for AWS HQ_1680757985",
            pool_id: "e327edaa-9f2d-4205-a3f1-e20532cd43d9"
          }
        ],
        employee_id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
        first_seen: 1672531200,
        pool_id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
        region: "us-west-2",
        resource_type: "Bucket",
        service_name: "AmazonS3",
        tags: {
          "aws:createdBy": "IAMUser:AIDAILS3JXIC55HPSQVYG:sf-full"
        },
        last_expense: {
          date: 1682899200,
          cost: 0.00646932
        },
        total_cost: 362.22024085239997,
        meta: {
          cloud_console_link: "https://console.aws.amazon.com/s3/buckets/yv-bucket?region=eu-central-1&tab=objects",
          is_public_policy: false,
          is_public_acls: false
        },
        active: true,
        created_at: 1684905197,
        last_seen: 1687762758,
        deleted_at: 0,
        id: "82085696-8795-48c5-803c-8a4bd3c979ea",
        is_environment: false,
        saving: 19.520247625714287,
        cost: 12.8935799502,
        cloud_account_name: "AWS HQ",
        cloud_account_type: "aws_cnr",
        owner: {
          id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
          name: "Lincoln Morton"
        },
        pool: {
          id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
          name: "AWS HQ",
          purpose: "budget"
        },
        resource_id: "82085696-8795-48c5-803c-8a4bd3c979ea",
        resource_name: "yv-bucket",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "us-west-2",
            to: "External",
            usage: 0.1509017578,
            cost: 0.0126827238
          }
        ],
        "pool/owner": "AWS HQ Lincoln Morton",
        resource: "yv-bucket yv-bucket",
        tagsString: "aws:createdBy: IAMUser:AIDAILS3JXIC55HPSQVYG:sf-full",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "AWS HQ aws_cnr Region: us-west-2,Service: AmazonS3",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchidgoldenimageus2/providers/microsoft.storage/storageaccounts/orchidgoldenimageus2",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/orchidGoldenImageUS2/providers/Microsoft.Storage/storageAccounts/orchidgoldenimageus2/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "West US 2",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.23339784000000002
        },
        total_cost: 29.157781186,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "5e40c606-025d-4b72-b2fb-eb26ada9aa51",
        is_environment: false,
        saving: 0,
        cost: 8.666847014,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "5e40c606-025d-4b72-b2fb-eb26ada9aa51",
        resource_name: "orchidgoldenimageus2",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "westus2",
            to: "North America",
            usage: 0.004328000000000001,
            cost: 0.00008655999999999998
          }
        ],
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchidgoldenimageus2/providers/microsoft.storage/storageaccounts/orchidgoldenimageus2 orchidgoldenimageus2",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: West US 2,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.storage/storageaccounts/aqadiag765",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/aqa-europe/providers/Microsoft.Storage/storageAccounts/aqadiag765/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "West US",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.149275071
        },
        total_cost: 19.057458491999995,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "3fe6e85c-e716-4f21-bfbf-8624c23ca902",
        is_environment: false,
        saving: 0,
        cost: 5.771115287999999,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "3fe6e85c-e716-4f21-bfbf-8624c23ca902",
        resource_name: "aqadiag765",
        shareable: false,
        constraint_violated: false,
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.storage/storageaccounts/aqadiag765 aqadiag765",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: West US,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "9d34d88a-8d52-4eca-9dd5-f35fe4876d1d",
        cloud_resource_id: "aws-cloudtrail-logs-044478323321-88eecf70",
        applied_rules: [
          {
            id: "55e6f5b5-9261-405e-8e56-a06cd2759a54",
            name: "Rule for AWS HQ_1680757985",
            pool_id: "e327edaa-9f2d-4205-a3f1-e20532cd43d9"
          }
        ],
        employee_id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
        first_seen: 1672531200,
        pool_id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
        region: "eu-west-1",
        resource_type: "Bucket",
        service_name: "AmazonS3",
        tags: {
          "aws:createdBy": "Root:044478323321"
        },
        last_expense: {
          date: 1682899200,
          cost: 0.08845876640000001
        },
        total_cost: 40.617113497,
        meta: {
          cloud_console_link:
            "https://console.aws.amazon.com/s3/buckets/aws-cloudtrail-logs-044478323321-88eecf70?region=eu-west-1&tab=objects",
          is_public_policy: false,
          is_public_acls: false
        },
        active: true,
        created_at: 1684905197,
        last_seen: 1687762758,
        deleted_at: 0,
        id: "100058b3-8dad-496c-9ed7-b3d5c089e99c",
        is_environment: false,
        saving: 0,
        cost: 12.020204510000001,
        cloud_account_name: "AWS HQ",
        cloud_account_type: "aws_cnr",
        owner: {
          id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
          name: "Lincoln Morton"
        },
        pool: {
          id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
          name: "AWS HQ",
          purpose: "budget"
        },
        resource_id: "100058b3-8dad-496c-9ed7-b3d5c089e99c",
        resource_name: "aws-cloudtrail-logs-044478323321-88eecf70",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "eu-west-1",
            to: "ap-northeast-2",
            usage: 0.010274799200000002,
            cost: 0.0002054878
          },
          {
            from: "eu-west-1",
            to: "ap-southeast-2",
            usage: 0.0161730676,
            cost: 0.00032345640000000004
          },
          {
            from: "eu-west-1",
            to: "sa-east-1",
            usage: 0.012021845799999998,
            cost: 0.0002404328
          },
          {
            from: "eu-west-1",
            to: "ap-northeast-3",
            usage: 0.009333807999999999,
            cost: 0.00018666819999999998
          },
          {
            from: "eu-west-1",
            to: "ap-southeast-3",
            usage: 0.0092865494,
            cost: 0.000185725
          },
          {
            from: "eu-west-1",
            to: "ap-southeast-1",
            usage: 0.009641144999999999,
            cost: 0.00019281639999999998
          },
          {
            from: "eu-west-1",
            to: "ap-northeast-1",
            usage: 0.010266058,
            cost: 0.00020531599999999993
          },
          {
            from: "eu-west-1",
            to: "ca-central-1",
            usage: 0.0093819566,
            cost: 0.00018763100000000003
          },
          {
            from: "eu-west-1",
            to: "eu-north-1",
            usage: 0.0093655644,
            cost: 0.0001873052
          },
          {
            from: "eu-west-1",
            to: "us-west-2",
            usage: 0.0239434264,
            cost: 0.0004788726
          },
          {
            from: "eu-west-1",
            to: "us-west-1",
            usage: 0.009838734799999999,
            cost: 0.00019677140000000002
          },
          {
            from: "eu-west-1",
            to: "eu-west-2",
            usage: 0.013179472799999998,
            cost: 0.00026358260000000004
          },
          {
            from: "eu-west-1",
            to: "eu-south-1",
            usage: 0.004891768400000001,
            cost: 0.0000978318
          },
          {
            from: "eu-west-1",
            to: "ap-south-1",
            usage: 0.0119871434,
            cost: 0.00023973700000000004
          },
          {
            from: "eu-west-1",
            to: "eu-west-3",
            usage: 0.009370686999999999,
            cost: 0.0001874064
          },
          {
            from: "eu-west-1",
            to: "us-east-1",
            usage: 0.025368446200000002,
            cost: 0.0005073704
          },
          {
            from: "eu-west-1",
            to: "us-east-2",
            usage: 0.0096585584,
            cost: 0.00019316640000000004
          }
        ],
        "pool/owner": "AWS HQ Lincoln Morton",
        resource: "aws-cloudtrail-logs-044478323321-88eecf70 aws-cloudtrail-logs-044478323321-88eecf70",
        tagsString: "aws:createdBy: Root:044478323321",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "AWS HQ aws_cnr Region: eu-west-1,Service: AmazonS3",
        resourceType: "Bucket"
      }
    ],
    started: 1687081094.3336148,
    status: "completed",
    duration: 208.83268447131263,
    objects: 8903,
    duplicates: 1993,
    saving: 199.3,
    size: 15,
    total_size: 15 * 4
  },
  {
    id: 2,
    buckets: [
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchid-engineering/providers/microsoft.storage/storageaccounts/orchidengineeringdiag",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/orchid-engineering/providers/Microsoft.Storage/storageAccounts/orchidengineeringdiag/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "West US 2",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.17345780100000002
        },
        total_cost: 22.066792974000006,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "d3823173-f372-4dfb-9afe-ae355e89f0d4",
        is_environment: false,
        saving: 0,
        cost: 6.706009116,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "d3823173-f372-4dfb-9afe-ae355e89f0d4",
        resource_name: "orchidengineeringdiag",
        shareable: false,
        constraint_violated: false,
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchid-engineering/providers/microsoft.storage/storageaccounts/orchidengineeringdiag orchidengineeringdiag",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: West US 2,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "9d34d88a-8d52-4eca-9dd5-f35fe4876d1d",
        cloud_resource_id: "yv-bucket",
        applied_rules: [
          {
            id: "55e6f5b5-9261-405e-8e56-a06cd2759a54",
            name: "Rule for AWS HQ_1680757985",
            pool_id: "e327edaa-9f2d-4205-a3f1-e20532cd43d9"
          }
        ],
        employee_id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
        first_seen: 1672531200,
        pool_id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
        region: "us-west-2",
        resource_type: "Bucket",
        service_name: "AmazonS3",
        tags: {
          "aws:createdBy": "IAMUser:AIDAILS3JXIC55HPSQVYG:sf-full"
        },
        last_expense: {
          date: 1682899200,
          cost: 0.00646932
        },
        total_cost: 362.22024085239997,
        meta: {
          cloud_console_link: "https://console.aws.amazon.com/s3/buckets/yv-bucket?region=eu-central-1&tab=objects",
          is_public_policy: false,
          is_public_acls: false
        },
        active: true,
        created_at: 1684905197,
        last_seen: 1687762758,
        deleted_at: 0,
        id: "82085696-8795-48c5-803c-8a4bd3c979ea",
        is_environment: false,
        saving: 19.520247625714287,
        cost: 12.8935799502,
        cloud_account_name: "AWS HQ",
        cloud_account_type: "aws_cnr",
        owner: {
          id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
          name: "Lincoln Morton"
        },
        pool: {
          id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
          name: "AWS HQ",
          purpose: "budget"
        },
        resource_id: "82085696-8795-48c5-803c-8a4bd3c979ea",
        resource_name: "yv-bucket",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "us-west-2",
            to: "External",
            usage: 0.1509017578,
            cost: 0.0126827238
          }
        ],
        "pool/owner": "AWS HQ Lincoln Morton",
        resource: "yv-bucket yv-bucket",
        tagsString: "aws:createdBy: IAMUser:AIDAILS3JXIC55HPSQVYG:sf-full",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "AWS HQ aws_cnr Region: us-west-2,Service: AmazonS3",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchidgoldenimageus2/providers/microsoft.storage/storageaccounts/orchidgoldenimageus2",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/orchidGoldenImageUS2/providers/Microsoft.Storage/storageAccounts/orchidgoldenimageus2/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "West US 2",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.23339784000000002
        },
        total_cost: 29.157781186,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "5e40c606-025d-4b72-b2fb-eb26ada9aa51",
        is_environment: false,
        saving: 0,
        cost: 8.666847014,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "5e40c606-025d-4b72-b2fb-eb26ada9aa51",
        resource_name: "orchidgoldenimageus2",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "westus2",
            to: "North America",
            usage: 0.004328000000000001,
            cost: 0.00008655999999999998
          }
        ],
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchidgoldenimageus2/providers/microsoft.storage/storageaccounts/orchidgoldenimageus2 orchidgoldenimageus2",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: West US 2,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/mgr-demo-stand/providers/microsoft.storage/storageaccounts/storagemgrdemostand",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/MGR-DEMO-STAND/providers/Microsoft.Storage/storageAccounts/storagemgrdemostand/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "Germany West Central",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.071606032
        },
        total_cost: 10.673333763999999,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "694feb6b-0e5e-4d71-b547-610fead4281e",
        is_environment: false,
        saving: 0,
        cost: 2.675488532,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "694feb6b-0e5e-4d71-b547-610fead4281e",
        resource_name: "storagemgrdemostand",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "germanywestcentral",
            to: "northeurope",
            usage: 0.004320000000000001,
            cost: 0.00008639999999999999
          }
        ],
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/mgr-demo-stand/providers/microsoft.storage/storageaccounts/storagemgrdemostand storagemgrdemostand",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: Germany West Central,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.storage/storageaccounts/aqadiag765",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/aqa-europe/providers/Microsoft.Storage/storageAccounts/aqadiag765/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "West US",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.149275071
        },
        total_cost: 19.057458491999995,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "3fe6e85c-e716-4f21-bfbf-8624c23ca902",
        is_environment: false,
        saving: 0,
        cost: 5.771115287999999,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "3fe6e85c-e716-4f21-bfbf-8624c23ca902",
        resource_name: "aqadiag765",
        shareable: false,
        constraint_violated: false,
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.storage/storageaccounts/aqadiag765 aqadiag765",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: West US,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "9d34d88a-8d52-4eca-9dd5-f35fe4876d1d",
        cloud_resource_id: "aws-cloudtrail-logs-044478323321-88eecf70",
        applied_rules: [
          {
            id: "55e6f5b5-9261-405e-8e56-a06cd2759a54",
            name: "Rule for AWS HQ_1680757985",
            pool_id: "e327edaa-9f2d-4205-a3f1-e20532cd43d9"
          }
        ],
        employee_id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
        first_seen: 1672531200,
        pool_id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
        region: "eu-west-1",
        resource_type: "Bucket",
        service_name: "AmazonS3",
        tags: {
          "aws:createdBy": "Root:044478323321"
        },
        last_expense: {
          date: 1682899200,
          cost: 0.08845876640000001
        },
        total_cost: 40.617113497,
        meta: {
          cloud_console_link:
            "https://console.aws.amazon.com/s3/buckets/aws-cloudtrail-logs-044478323321-88eecf70?region=eu-west-1&tab=objects",
          is_public_policy: false,
          is_public_acls: false
        },
        active: true,
        created_at: 1684905197,
        last_seen: 1687762758,
        deleted_at: 0,
        id: "100058b3-8dad-496c-9ed7-b3d5c089e99c",
        is_environment: false,
        saving: 0,
        cost: 12.020204510000001,
        cloud_account_name: "AWS HQ",
        cloud_account_type: "aws_cnr",
        owner: {
          id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
          name: "Lincoln Morton"
        },
        pool: {
          id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
          name: "AWS HQ",
          purpose: "budget"
        },
        resource_id: "100058b3-8dad-496c-9ed7-b3d5c089e99c",
        resource_name: "aws-cloudtrail-logs-044478323321-88eecf70",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "eu-west-1",
            to: "ap-northeast-2",
            usage: 0.010274799200000002,
            cost: 0.0002054878
          },
          {
            from: "eu-west-1",
            to: "ap-southeast-2",
            usage: 0.0161730676,
            cost: 0.00032345640000000004
          },
          {
            from: "eu-west-1",
            to: "sa-east-1",
            usage: 0.012021845799999998,
            cost: 0.0002404328
          },
          {
            from: "eu-west-1",
            to: "ap-northeast-3",
            usage: 0.009333807999999999,
            cost: 0.00018666819999999998
          },
          {
            from: "eu-west-1",
            to: "ap-southeast-3",
            usage: 0.0092865494,
            cost: 0.000185725
          },
          {
            from: "eu-west-1",
            to: "ap-southeast-1",
            usage: 0.009641144999999999,
            cost: 0.00019281639999999998
          },
          {
            from: "eu-west-1",
            to: "ap-northeast-1",
            usage: 0.010266058,
            cost: 0.00020531599999999993
          },
          {
            from: "eu-west-1",
            to: "ca-central-1",
            usage: 0.0093819566,
            cost: 0.00018763100000000003
          },
          {
            from: "eu-west-1",
            to: "eu-north-1",
            usage: 0.0093655644,
            cost: 0.0001873052
          },
          {
            from: "eu-west-1",
            to: "us-west-2",
            usage: 0.0239434264,
            cost: 0.0004788726
          },
          {
            from: "eu-west-1",
            to: "us-west-1",
            usage: 0.009838734799999999,
            cost: 0.00019677140000000002
          },
          {
            from: "eu-west-1",
            to: "eu-west-2",
            usage: 0.013179472799999998,
            cost: 0.00026358260000000004
          },
          {
            from: "eu-west-1",
            to: "eu-south-1",
            usage: 0.004891768400000001,
            cost: 0.0000978318
          },
          {
            from: "eu-west-1",
            to: "ap-south-1",
            usage: 0.0119871434,
            cost: 0.00023973700000000004
          },
          {
            from: "eu-west-1",
            to: "eu-west-3",
            usage: 0.009370686999999999,
            cost: 0.0001874064
          },
          {
            from: "eu-west-1",
            to: "us-east-1",
            usage: 0.025368446200000002,
            cost: 0.0005073704
          },
          {
            from: "eu-west-1",
            to: "us-east-2",
            usage: 0.0096585584,
            cost: 0.00019316640000000004
          }
        ],
        "pool/owner": "AWS HQ Lincoln Morton",
        resource: "aws-cloudtrail-logs-044478323321-88eecf70 aws-cloudtrail-logs-044478323321-88eecf70",
        tagsString: "aws:createdBy: Root:044478323321",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "AWS HQ aws_cnr Region: eu-west-1,Service: AmazonS3",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.storage/storageaccounts/aqadiag",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/aqa-europe/providers/Microsoft.Storage/storageAccounts/aqadiag/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "West Europe",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.21031812
        },
        total_cost: 25.353391458,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "2ebf2837-7302-4bf8-9325-105f159ffb74",
        is_environment: false,
        saving: 0,
        cost: 7.80982866,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "2ebf2837-7302-4bf8-9325-105f159ffb74",
        resource_name: "aqadiag",
        shareable: false,
        constraint_violated: false,
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.storage/storageaccounts/aqadiag aqadiag",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: West Europe,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/dr-demo-stand/providers/microsoft.storage/storageaccounts/storagerdemostand",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/DR-DEMO-STAND/providers/Microsoft.Storage/storageAccounts/storagerdemostand/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "Germany West Central",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.071937952
        },
        total_cost: 10.787204683999999,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "f0fa65c7-6d59-457c-8c77-54cc92ac2965",
        is_environment: false,
        saving: 0,
        cost: 2.687917128,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "f0fa65c7-6d59-457c-8c77-54cc92ac2965",
        resource_name: "storagerdemostand",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "germanywestcentral",
            to: "northeurope",
            usage: 0.0043440000000000015,
            cost: 0.00008687999999999998
          }
        ],
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/dr-demo-stand/providers/microsoft.storage/storageaccounts/storagerdemostand storagerdemostand",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: Germany West Central,Service: Microsoft.Storage",
        resourceType: "Bucket"
      }
    ],
    started: 1687009204.821877,
    status: "completed",
    duration: 247.6270020409636,
    objects: 56137,
    duplicates: 4998,
    size: 12,
    total_size: 12 * 4,
    saving: 499.8
  },
  {
    id: 3,
    buckets: [
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchid-engineering/providers/microsoft.storage/storageaccounts/orchidengineeringdiag",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/orchid-engineering/providers/Microsoft.Storage/storageAccounts/orchidengineeringdiag/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "West US 2",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.17345780100000002
        },
        total_cost: 22.066792974000006,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "d3823173-f372-4dfb-9afe-ae355e89f0d4",
        is_environment: false,
        saving: 0,
        cost: 6.706009116,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "d3823173-f372-4dfb-9afe-ae355e89f0d4",
        resource_name: "orchidengineeringdiag",
        shareable: false,
        constraint_violated: false,
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchid-engineering/providers/microsoft.storage/storageaccounts/orchidengineeringdiag orchidengineeringdiag",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: West US 2,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/dr-demo-stand/providers/microsoft.storage/storageaccounts/storagerdemostand",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/DR-DEMO-STAND/providers/Microsoft.Storage/storageAccounts/storagerdemostand/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "Germany West Central",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.071937952
        },
        total_cost: 10.787204683999999,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "f0fa65c7-6d59-457c-8c77-54cc92ac2965",
        is_environment: false,
        saving: 0,
        cost: 2.687917128,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "f0fa65c7-6d59-457c-8c77-54cc92ac2965",
        resource_name: "storagerdemostand",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "germanywestcentral",
            to: "northeurope",
            usage: 0.0043440000000000015,
            cost: 0.00008687999999999998
          }
        ],
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/dr-demo-stand/providers/microsoft.storage/storageaccounts/storagerdemostand storagerdemostand",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: Germany West Central,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "9d34d88a-8d52-4eca-9dd5-f35fe4876d1d",
        cloud_resource_id: "yv-bucket",
        applied_rules: [
          {
            id: "55e6f5b5-9261-405e-8e56-a06cd2759a54",
            name: "Rule for AWS HQ_1680757985",
            pool_id: "e327edaa-9f2d-4205-a3f1-e20532cd43d9"
          }
        ],
        employee_id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
        first_seen: 1672531200,
        pool_id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
        region: "us-west-2",
        resource_type: "Bucket",
        service_name: "AmazonS3",
        tags: {
          "aws:createdBy": "IAMUser:AIDAILS3JXIC55HPSQVYG:sf-full"
        },
        last_expense: {
          date: 1682899200,
          cost: 0.00646932
        },
        total_cost: 362.22024085239997,
        meta: {
          cloud_console_link: "https://console.aws.amazon.com/s3/buckets/yv-bucket?region=eu-central-1&tab=objects",
          is_public_policy: false,
          is_public_acls: false
        },
        active: true,
        created_at: 1684905197,
        last_seen: 1687762758,
        deleted_at: 0,
        id: "82085696-8795-48c5-803c-8a4bd3c979ea",
        is_environment: false,
        saving: 19.520247625714287,
        cost: 12.8935799502,
        cloud_account_name: "AWS HQ",
        cloud_account_type: "aws_cnr",
        owner: {
          id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
          name: "Lincoln Morton"
        },
        pool: {
          id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
          name: "AWS HQ",
          purpose: "budget"
        },
        resource_id: "82085696-8795-48c5-803c-8a4bd3c979ea",
        resource_name: "yv-bucket",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "us-west-2",
            to: "External",
            usage: 0.1509017578,
            cost: 0.0126827238
          }
        ],
        "pool/owner": "AWS HQ Lincoln Morton",
        resource: "yv-bucket yv-bucket",
        tagsString: "aws:createdBy: IAMUser:AIDAILS3JXIC55HPSQVYG:sf-full",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "AWS HQ aws_cnr Region: us-west-2,Service: AmazonS3",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchidgoldenimageus2/providers/microsoft.storage/storageaccounts/orchidgoldenimageus2",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/orchidGoldenImageUS2/providers/Microsoft.Storage/storageAccounts/orchidgoldenimageus2/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "West US 2",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.23339784000000002
        },
        total_cost: 29.157781186,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "5e40c606-025d-4b72-b2fb-eb26ada9aa51",
        is_environment: false,
        saving: 0,
        cost: 8.666847014,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "5e40c606-025d-4b72-b2fb-eb26ada9aa51",
        resource_name: "orchidgoldenimageus2",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "westus2",
            to: "North America",
            usage: 0.004328000000000001,
            cost: 0.00008655999999999998
          }
        ],
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchidgoldenimageus2/providers/microsoft.storage/storageaccounts/orchidgoldenimageus2 orchidgoldenimageus2",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: West US 2,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.storage/storageaccounts/aqadiag765",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/aqa-europe/providers/Microsoft.Storage/storageAccounts/aqadiag765/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "West US",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.149275071
        },
        total_cost: 19.057458491999995,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "3fe6e85c-e716-4f21-bfbf-8624c23ca902",
        is_environment: false,
        saving: 0,
        cost: 5.771115287999999,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "3fe6e85c-e716-4f21-bfbf-8624c23ca902",
        resource_name: "aqadiag765",
        shareable: false,
        constraint_violated: false,
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.storage/storageaccounts/aqadiag765 aqadiag765",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: West US,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/mgr-demo-stand/providers/microsoft.storage/storageaccounts/storagemgrdemostand",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/MGR-DEMO-STAND/providers/Microsoft.Storage/storageAccounts/storagemgrdemostand/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "Germany West Central",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.071606032
        },
        total_cost: 10.673333763999999,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "694feb6b-0e5e-4d71-b547-610fead4281e",
        is_environment: false,
        saving: 0,
        cost: 2.675488532,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "694feb6b-0e5e-4d71-b547-610fead4281e",
        resource_name: "storagemgrdemostand",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "germanywestcentral",
            to: "northeurope",
            usage: 0.004320000000000001,
            cost: 0.00008639999999999999
          }
        ],
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/mgr-demo-stand/providers/microsoft.storage/storageaccounts/storagemgrdemostand storagemgrdemostand",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: Germany West Central,Service: Microsoft.Storage",
        resourceType: "Bucket"
      }
    ],
    started: 1686915313.71628,
    status: "failed",
    error: "Buckets removed while check was in progress"
  },
  {
    id: 4,
    buckets: [
      {
        cloud_account_id: "9d34d88a-8d52-4eca-9dd5-f35fe4876d1d",
        cloud_resource_id: "sunflower-eu-fra",
        applied_rules: [
          {
            id: "55e6f5b5-9261-405e-8e56-a06cd2759a54",
            name: "Rule for AWS HQ_1680757985",
            pool_id: "e327edaa-9f2d-4205-a3f1-e20532cd43d9"
          }
        ],
        employee_id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
        first_seen: 1672531200,
        pool_id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
        region: "us-west-2",
        resource_type: "Bucket",
        service_name: "AmazonS3",
        tags: {
          "aws:createdBy": "IAMUser:AIDAIWGUBPAVMAWKKOLBA:s3-user"
        },
        last_expense: {
          date: 1682899200,
          cost: 0.006650830000000001
        },
        total_cost: 721.8798723085999,
        meta: {
          cloud_console_link: "https://console.aws.amazon.com/s3/buckets/sunflower-eu-fra?region=eu-central-1&tab=objects",
          is_public_policy: false,
          is_public_acls: true
        },
        active: true,
        constraint_violated: true,
        created_at: 1684905197,
        last_seen: 1687762758,
        deleted_at: 0,
        id: "1a7c005c-083b-490f-bdf4-2c2e97fd8596",
        is_environment: false,
        saving: 0,
        cost: 254.86900482779996,
        cloud_account_name: "AWS HQ",
        cloud_account_type: "aws_cnr",
        owner: {
          id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
          name: "Lincoln Morton"
        },
        pool: {
          id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
          name: "AWS HQ",
          purpose: "budget"
        },
        resource_id: "1a7c005c-083b-490f-bdf4-2c2e97fd8596",
        resource_name: "sunflower-eu-fra",
        shareable: false,
        traffic_expenses: [
          {
            from: "us-west-2",
            to: "External",
            usage: 2021.6524389862004,
            cost: 169.9123596588
          },
          {
            from: "us-west-2",
            to: "ap-southeast-1",
            usage: 0.0008995683999999999,
            cost: 0.000017991199999999998
          },
          {
            from: "us-east-1",
            to: "ap-southeast-1",
            usage: 0.0000016876,
            cost: 3.36e-8
          },
          {
            from: "us-west-2",
            to: "eu-west-1",
            usage: 7.7624077274,
            cost: 0.1552481546
          },
          {
            from: "us-west-2",
            to: "us-east-1",
            usage: 0.074371824,
            cost: 0.0014874368
          }
        ],
        "pool/owner": "AWS HQ Lincoln Morton",
        resource: "sunflower-eu-fra sunflower-eu-fra",
        tagsString: "aws:createdBy: IAMUser:AIDAIWGUBPAVMAWKKOLBA:s3-user",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "AWS HQ aws_cnr Region: us-west-2,Service: AmazonS3",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/lilygoldenimageus2/providers/microsoft.storage/storageaccounts/lilygoldenimageus2diag",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/lilyGoldenImageUS2/providers/Microsoft.Storage/storageAccounts/lilygoldenimageus2diag/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "West US 2",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.7927370759999999
        },
        total_cost: 96.713911756,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "70bee4fe-eb10-4a7d-8407-ec33feb76126",
        is_environment: false,
        saving: 0,
        cost: 29.436969411999996,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "70bee4fe-eb10-4a7d-8407-ec33feb76126",
        resource_name: "lilygoldenimageus2diag",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "westus2",
            to: "North America",
            usage: 0.004320000000000001,
            cost: 0.00008639999999999999
          }
        ],
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/lilygoldenimageus2/providers/microsoft.storage/storageaccounts/lilygoldenimageus2diag lilygoldenimageus2diag",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: West US 2,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "9d34d88a-8d52-4eca-9dd5-f35fe4876d1d",
        cloud_resource_id: "aws-cloudtrail-logs-044478323321-88eecf70",
        applied_rules: [
          {
            id: "55e6f5b5-9261-405e-8e56-a06cd2759a54",
            name: "Rule for AWS HQ_1680757985",
            pool_id: "e327edaa-9f2d-4205-a3f1-e20532cd43d9"
          }
        ],
        employee_id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
        first_seen: 1672531200,
        pool_id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
        region: "eu-west-1",
        resource_type: "Bucket",
        service_name: "AmazonS3",
        tags: {
          "aws:createdBy": "Root:044478323321"
        },
        last_expense: {
          date: 1682899200,
          cost: 0.08845876640000001
        },
        total_cost: 40.617113497,
        meta: {
          cloud_console_link:
            "https://console.aws.amazon.com/s3/buckets/aws-cloudtrail-logs-044478323321-88eecf70?region=eu-west-1&tab=objects",
          is_public_policy: false,
          is_public_acls: false
        },
        active: true,
        created_at: 1684905197,
        last_seen: 1687762758,
        deleted_at: 0,
        id: "100058b3-8dad-496c-9ed7-b3d5c089e99c",
        is_environment: false,
        saving: 0,
        cost: 12.020204510000001,
        cloud_account_name: "AWS HQ",
        cloud_account_type: "aws_cnr",
        owner: {
          id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
          name: "Lincoln Morton"
        },
        pool: {
          id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
          name: "AWS HQ",
          purpose: "budget"
        },
        resource_id: "100058b3-8dad-496c-9ed7-b3d5c089e99c",
        resource_name: "aws-cloudtrail-logs-044478323321-88eecf70",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "eu-west-1",
            to: "ap-northeast-2",
            usage: 0.010274799200000002,
            cost: 0.0002054878
          },
          {
            from: "eu-west-1",
            to: "ap-southeast-2",
            usage: 0.0161730676,
            cost: 0.00032345640000000004
          },
          {
            from: "eu-west-1",
            to: "sa-east-1",
            usage: 0.012021845799999998,
            cost: 0.0002404328
          },
          {
            from: "eu-west-1",
            to: "ap-northeast-3",
            usage: 0.009333807999999999,
            cost: 0.00018666819999999998
          },
          {
            from: "eu-west-1",
            to: "ap-southeast-3",
            usage: 0.0092865494,
            cost: 0.000185725
          },
          {
            from: "eu-west-1",
            to: "ap-southeast-1",
            usage: 0.009641144999999999,
            cost: 0.00019281639999999998
          },
          {
            from: "eu-west-1",
            to: "ap-northeast-1",
            usage: 0.010266058,
            cost: 0.00020531599999999993
          },
          {
            from: "eu-west-1",
            to: "ca-central-1",
            usage: 0.0093819566,
            cost: 0.00018763100000000003
          },
          {
            from: "eu-west-1",
            to: "eu-north-1",
            usage: 0.0093655644,
            cost: 0.0001873052
          },
          {
            from: "eu-west-1",
            to: "us-west-2",
            usage: 0.0239434264,
            cost: 0.0004788726
          },
          {
            from: "eu-west-1",
            to: "us-west-1",
            usage: 0.009838734799999999,
            cost: 0.00019677140000000002
          },
          {
            from: "eu-west-1",
            to: "eu-west-2",
            usage: 0.013179472799999998,
            cost: 0.00026358260000000004
          },
          {
            from: "eu-west-1",
            to: "eu-south-1",
            usage: 0.004891768400000001,
            cost: 0.0000978318
          },
          {
            from: "eu-west-1",
            to: "ap-south-1",
            usage: 0.0119871434,
            cost: 0.00023973700000000004
          },
          {
            from: "eu-west-1",
            to: "eu-west-3",
            usage: 0.009370686999999999,
            cost: 0.0001874064
          },
          {
            from: "eu-west-1",
            to: "us-east-1",
            usage: 0.025368446200000002,
            cost: 0.0005073704
          },
          {
            from: "eu-west-1",
            to: "us-east-2",
            usage: 0.0096585584,
            cost: 0.00019316640000000004
          }
        ],
        "pool/owner": "AWS HQ Lincoln Morton",
        resource: "aws-cloudtrail-logs-044478323321-88eecf70 aws-cloudtrail-logs-044478323321-88eecf70",
        tagsString: "aws:createdBy: Root:044478323321",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "AWS HQ aws_cnr Region: eu-west-1,Service: AmazonS3",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "9d34d88a-8d52-4eca-9dd5-f35fe4876d1d",
        cloud_resource_id: "yv-bucket",
        applied_rules: [
          {
            id: "55e6f5b5-9261-405e-8e56-a06cd2759a54",
            name: "Rule for AWS HQ_1680757985",
            pool_id: "e327edaa-9f2d-4205-a3f1-e20532cd43d9"
          }
        ],
        employee_id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
        first_seen: 1672531200,
        pool_id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
        region: "us-west-2",
        resource_type: "Bucket",
        service_name: "AmazonS3",
        tags: {
          "aws:createdBy": "IAMUser:AIDAILS3JXIC55HPSQVYG:sf-full"
        },
        last_expense: {
          date: 1682899200,
          cost: 0.00646932
        },
        total_cost: 362.22024085239997,
        meta: {
          cloud_console_link: "https://console.aws.amazon.com/s3/buckets/yv-bucket?region=eu-central-1&tab=objects",
          is_public_policy: false,
          is_public_acls: false
        },
        active: true,
        created_at: 1684905197,
        last_seen: 1687762758,
        deleted_at: 0,
        id: "82085696-8795-48c5-803c-8a4bd3c979ea",
        is_environment: false,
        saving: 19.520247625714287,
        cost: 12.8935799502,
        cloud_account_name: "AWS HQ",
        cloud_account_type: "aws_cnr",
        owner: {
          id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
          name: "Lincoln Morton"
        },
        pool: {
          id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
          name: "AWS HQ",
          purpose: "budget"
        },
        resource_id: "82085696-8795-48c5-803c-8a4bd3c979ea",
        resource_name: "yv-bucket",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "us-west-2",
            to: "External",
            usage: 0.1509017578,
            cost: 0.0126827238
          }
        ],
        "pool/owner": "AWS HQ Lincoln Morton",
        resource: "yv-bucket yv-bucket",
        tagsString: "aws:createdBy: IAMUser:AIDAILS3JXIC55HPSQVYG:sf-full",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "AWS HQ aws_cnr Region: us-west-2,Service: AmazonS3",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchid-engineering/providers/microsoft.storage/storageaccounts/orchidengineeringdiag",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/orchid-engineering/providers/Microsoft.Storage/storageAccounts/orchidengineeringdiag/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "West US 2",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.17345780100000002
        },
        total_cost: 22.066792974000006,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "d3823173-f372-4dfb-9afe-ae355e89f0d4",
        is_environment: false,
        saving: 0,
        cost: 6.706009116,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "d3823173-f372-4dfb-9afe-ae355e89f0d4",
        resource_name: "orchidengineeringdiag",
        shareable: false,
        constraint_violated: false,
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchid-engineering/providers/microsoft.storage/storageaccounts/orchidengineeringdiag orchidengineeringdiag",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: West US 2,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/mgr-demo-stand/providers/microsoft.storage/storageaccounts/storagemgrdemostand",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/MGR-DEMO-STAND/providers/Microsoft.Storage/storageAccounts/storagemgrdemostand/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "Germany West Central",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.071606032
        },
        total_cost: 10.673333763999999,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "694feb6b-0e5e-4d71-b547-610fead4281e",
        is_environment: false,
        saving: 0,
        cost: 2.675488532,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "694feb6b-0e5e-4d71-b547-610fead4281e",
        resource_name: "storagemgrdemostand",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "germanywestcentral",
            to: "northeurope",
            usage: 0.004320000000000001,
            cost: 0.00008639999999999999
          }
        ],
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/mgr-demo-stand/providers/microsoft.storage/storageaccounts/storagemgrdemostand storagemgrdemostand",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: Germany West Central,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchidgoldenimageus2/providers/microsoft.storage/storageaccounts/orchidgoldenimageus2",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/orchidGoldenImageUS2/providers/Microsoft.Storage/storageAccounts/orchidgoldenimageus2/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "West US 2",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.23339784000000002
        },
        total_cost: 29.157781186,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "5e40c606-025d-4b72-b2fb-eb26ada9aa51",
        is_environment: false,
        saving: 0,
        cost: 8.666847014,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "5e40c606-025d-4b72-b2fb-eb26ada9aa51",
        resource_name: "orchidgoldenimageus2",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "westus2",
            to: "North America",
            usage: 0.004328000000000001,
            cost: 0.00008655999999999998
          }
        ],
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchidgoldenimageus2/providers/microsoft.storage/storageaccounts/orchidgoldenimageus2 orchidgoldenimageus2",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: West US 2,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.storage/storageaccounts/aqadiag765",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/aqa-europe/providers/Microsoft.Storage/storageAccounts/aqadiag765/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "West US",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.149275071
        },
        total_cost: 19.057458491999995,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "3fe6e85c-e716-4f21-bfbf-8624c23ca902",
        is_environment: false,
        saving: 0,
        cost: 5.771115287999999,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "3fe6e85c-e716-4f21-bfbf-8624c23ca902",
        resource_name: "aqadiag765",
        shareable: false,
        constraint_violated: false,
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.storage/storageaccounts/aqadiag765 aqadiag765",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: West US,Service: Microsoft.Storage",
        resourceType: "Bucket"
      },
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.storage/storageaccounts/aqadiag",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/aqa-europe/providers/Microsoft.Storage/storageAccounts/aqadiag/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "West Europe",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.21031812
        },
        total_cost: 25.353391458,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "2ebf2837-7302-4bf8-9325-105f159ffb74",
        is_environment: false,
        saving: 0,
        cost: 7.80982866,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "2ebf2837-7302-4bf8-9325-105f159ffb74",
        resource_name: "aqadiag",
        shareable: false,
        constraint_violated: false,
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.storage/storageaccounts/aqadiag aqadiag",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: West Europe,Service: Microsoft.Storage",
        resourceType: "Bucket"
      }
    ],
    started: 1686831925.8214445,
    status: "completed",
    duration: 273.61869646498695,
    objects: 65705,
    duplicates: 25,
    size: 1.5,
    total_size: 1505,
    saving: 433.8
  },
  {
    id: 5,
    buckets: [
      {
        cloud_account_id: "9d34d88a-8d52-4eca-9dd5-f35fe4876d1d",
        cloud_resource_id: "sunflower-eu-fra",
        applied_rules: [
          {
            id: "55e6f5b5-9261-405e-8e56-a06cd2759a54",
            name: "Rule for AWS HQ_1680757985",
            pool_id: "e327edaa-9f2d-4205-a3f1-e20532cd43d9"
          }
        ],
        employee_id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
        first_seen: 1672531200,
        pool_id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
        region: "us-west-2",
        resource_type: "Bucket",
        service_name: "AmazonS3",
        tags: {
          "aws:createdBy": "IAMUser:AIDAIWGUBPAVMAWKKOLBA:s3-user"
        },
        last_expense: {
          date: 1682899200,
          cost: 0.006650830000000001
        },
        total_cost: 721.8798723085999,
        meta: {
          cloud_console_link: "https://console.aws.amazon.com/s3/buckets/sunflower-eu-fra?region=eu-central-1&tab=objects",
          is_public_policy: false,
          is_public_acls: true
        },
        active: true,
        constraint_violated: true,
        created_at: 1684905197,
        last_seen: 1687762758,
        deleted_at: 0,
        id: "1a7c005c-083b-490f-bdf4-2c2e97fd8596",
        is_environment: false,
        saving: 0,
        cost: 254.86900482779996,
        cloud_account_name: "AWS HQ",
        cloud_account_type: "aws_cnr",
        owner: {
          id: "fcf3d377-b59c-4169-9fea-6303024d37c6",
          name: "Lincoln Morton"
        },
        pool: {
          id: "91c322f4-9fa4-46fd-af77-bbcdf3d5fb69",
          name: "AWS HQ",
          purpose: "budget"
        },
        resource_id: "1a7c005c-083b-490f-bdf4-2c2e97fd8596",
        resource_name: "sunflower-eu-fra",
        shareable: false,
        traffic_expenses: [
          {
            from: "us-west-2",
            to: "External",
            usage: 2021.6524389862004,
            cost: 169.9123596588
          },
          {
            from: "us-west-2",
            to: "ap-southeast-1",
            usage: 0.0008995683999999999,
            cost: 0.000017991199999999998
          },
          {
            from: "us-east-1",
            to: "ap-southeast-1",
            usage: 0.0000016876,
            cost: 3.36e-8
          },
          {
            from: "us-west-2",
            to: "eu-west-1",
            usage: 7.7624077274,
            cost: 0.1552481546
          },
          {
            from: "us-west-2",
            to: "us-east-1",
            usage: 0.074371824,
            cost: 0.0014874368
          }
        ],
        "pool/owner": "AWS HQ Lincoln Morton",
        resource: "sunflower-eu-fra sunflower-eu-fra",
        tagsString: "aws:createdBy: IAMUser:AIDAIWGUBPAVMAWKKOLBA:s3-user",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "AWS HQ aws_cnr Region: us-west-2,Service: AmazonS3",
        resourceType: "Bucket"
      }
    ],
    started: 1686735054.5118084,
    status: "completed",
    duration: 366.5959327142142,
    objects: 5976,
    duplicates: 505,
    size: 3.1,
    total_size: 3.1 * 10.5,
    saving: 50.5
  },
  {
    id: 6,
    buckets: [
      {
        cloud_account_id: "711739d7-3cd0-4495-a812-1599a4605b9d",
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/mgr-demo-stand/providers/microsoft.storage/storageaccounts/storagemgrdemostand",
        active: true,
        applied_rules: [
          {
            id: "0a55a962-5ad9-499c-b7e0-de4715da6307",
            name: "Rule for Dev environment_1680757920",
            pool_id: "9ef6f469-434d-4937-80b0-6eea3085deb6"
          }
        ],
        employee_id: "ff368cee-680c-42f4-a3a8-3d629353f554",
        first_seen: 1672531200,
        meta: {
          cloud_console_link:
            "https://portal.azure.com/#resource/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/MGR-DEMO-STAND/providers/Microsoft.Storage/storageAccounts/storagemgrdemostand/overview",
          is_public_policy: false,
          is_public_acls: false
        },
        pool_id: "345cf03f-1049-467b-84b3-4c39c3932896",
        region: "Germany West Central",
        resource_type: "Bucket",
        tags: {},
        service_name: "Microsoft.Storage",
        last_expense: {
          date: 1682899200,
          cost: 0.071606032
        },
        total_cost: 10.673333763999999,
        created_at: 1684905330,
        last_seen: 1687762759,
        deleted_at: 0,
        id: "694feb6b-0e5e-4d71-b547-610fead4281e",
        is_environment: false,
        saving: 0,
        cost: 2.675488532,
        cloud_account_name: "Dev environment",
        cloud_account_type: "azure_cnr",
        owner: {
          id: "ff368cee-680c-42f4-a3a8-3d629353f554",
          name: "Demo User"
        },
        pool: {
          id: "345cf03f-1049-467b-84b3-4c39c3932896",
          name: "Dev environment",
          purpose: "budget"
        },
        resource_id: "694feb6b-0e5e-4d71-b547-610fead4281e",
        resource_name: "storagemgrdemostand",
        shareable: false,
        constraint_violated: false,
        traffic_expenses: [
          {
            from: "germanywestcentral",
            to: "northeurope",
            usage: 0.004320000000000001,
            cost: 0.00008639999999999999
          }
        ],
        "pool/owner": "Dev environment Demo User",
        resource:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/mgr-demo-stand/providers/microsoft.storage/storageaccounts/storagemgrdemostand storagemgrdemostand",
        tagsString: "",
        metadataString: ["First seen: 01/01/2023", "Last seen: 06/26/2023"],
        locationString: "Dev environment azure_cnr Region: Germany West Central,Service: Microsoft.Storage",
        resourceType: "Bucket"
      }
    ],
    started: 1686662935.570389,
    status: "failed",
    error: "Buckets removed while check was in progress"
  }
].map((base, i) => ({
  ...base,
  started: millisecondsToSeconds(+new Date()) - 60 * 60 * 24 * i - Math.random() * 60 * 60 * 5 * (i === 0 ? 0.01 : 1),
  saving: base.saving ?? 0,
  duplicates: base.duplicates ?? 0
}));
