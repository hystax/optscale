const MOCKED_DATA = {
  total_saving: 5806.920251782697,
  optimizations: {
    abandoned_instances: {
      count: 32,
      saving: 1909.1631072959997,
      options: {
        days_threshold: 7,
        cpu_percent_threshold: 5,
        network_bps_threshold: 1000,
        excluded_pools: {},
        skip_cloud_accounts: []
      },
      items: [
        {
          resource_id: "f0b98d89-13ee-4938-bfe3-34342cbcd7b1",
          resource_name: "aqa-instance-generation-upgrade",
          cloud_resource_id: "i-gw87l0czzy3lr9es2npa",
          region: "Germany (Frankfurt)",
          cloud_account_id: "5c75d0f5-3c30-4f5d-a92f-d0ea150af205",
          cloud_type: "alibaba_cnr",
          owner: { id: "33e28316-f72f-4592-96c6-4766c963519b", name: "Lincoln Morton" },
          pool: { id: "71f91ed4-9c63-4c36-9e2b-5686accf9ba0", name: "Ali dev", purpose: "budget" },
          is_excluded: false,
          saving: 186.10285714285718,
          detected_at: 1682054418,
          cloud_account_name: "Ali dev"
        },
        {
          resource_id: "a945f0a3-9f5a-4490-bd1e-39ab1009a79f",
          resource_name: "aqa-instance-generation-upgrade-x1",
          cloud_resource_id: "i-gw87l0czzy3lr9es2npa-x1",
          region: "Germany (Frankfurt)",
          cloud_account_id: "5c75d0f5-3c30-4f5d-a92f-d0ea150af205",
          cloud_type: "alibaba_cnr",
          owner: { id: "33e28316-f72f-4592-96c6-4766c963519b", name: "Lincoln Morton" },
          pool: { id: "71f91ed4-9c63-4c36-9e2b-5686accf9ba0", name: "Ali dev", purpose: "budget" },
          is_excluded: false,
          saving: 186.10285714285718,
          detected_at: 1682054418,
          cloud_account_name: "Ali dev"
        },
        {
          resource_id: "aed1a586-2c3d-4813-922d-52c5ebdf646e",
          resource_name: "aqa-instance-generation-upgrade-x2",
          cloud_resource_id: "i-gw87l0czzy3lr9es2npa-x2",
          region: "Germany (Frankfurt)",
          cloud_account_id: "5c75d0f5-3c30-4f5d-a92f-d0ea150af205",
          cloud_type: "alibaba_cnr",
          owner: { id: "33e28316-f72f-4592-96c6-4766c963519b", name: "Lincoln Morton" },
          pool: { id: "71f91ed4-9c63-4c36-9e2b-5686accf9ba0", name: "Ali dev", purpose: "budget" },
          is_excluded: false,
          saving: 186.10285714285718,
          detected_at: 1682054418,
          cloud_account_name: "Ali dev"
        }
      ],
      limit: 3
    },
    abandoned_kinesis_streams: {
      count: 1,
      saving: 25.919999999999995,
      options: { days_threshold: 7, excluded_pools: {}, skip_cloud_accounts: [] },
      items: [
        {
          cloud_resource_id: "OMtest",
          resource_name: null,
          resource_id: "813c64ef-0fca-460f-86a2-ee6f8c5f30a8",
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          region: "us-west-2",
          owner: { id: "33e28316-f72f-4592-96c6-4766c963519b", name: "Lincoln Morton" },
          pool: { id: "6c936baf-5045-4326-9c8e-52337e56a19c", name: "AWS HQ", purpose: "budget" },
          is_excluded: false,
          shardhours_capacity: 1,
          shardhours_price: 0.018,
          saving: 25.919999999999995,
          detected_at: 1681967718,
          cloud_account_name: "AWS HQ"
        }
      ],
      limit: 3
    },
    inactive_console_users: {
      count: 4,
      options: { days_threshold: 91, skip_cloud_accounts: [] },
      items: [
        {
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          user_name: "aqa-user",
          user_id: "AIDAIKFDVXZELQ5NVB2EQ",
          last_used: 1652869334,
          detected_at: 1682054418,
          cloud_account_name: "AWS HQ"
        },
        {
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          user_name: "pk-full",
          user_id: "AIDAIPPYCHRYQONGDLRJS",
          last_used: 1629370721,
          detected_at: 1682054418,
          cloud_account_name: "AWS HQ"
        },
        {
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          user_name: "sd-full",
          user_id: "AIDAQUWY5LJ4UVW7CRF5Y",
          last_used: 1671603701,
          detected_at: 1682054418,
          cloud_account_name: "AWS HQ"
        }
      ],
      limit: 3
    },
    inactive_users: {
      count: 29,
      options: { days_threshold: 91, skip_cloud_accounts: [] },
      items: [
        {
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          user_name: "ani-full-user",
          user_id: "AIDAQUWY5LJ43UZ5EL2U6",
          last_used: 1661759335,
          detected_at: 1682054418,
          cloud_account_name: "AWS HQ"
        },
        {
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          user_name: "ani-s3-user",
          user_id: "AIDAQUWY5LJ47ZTO26I6P",
          last_used: 1645774440,
          detected_at: 1682054418,
          cloud_account_name: "AWS HQ"
        },
        {
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          user_name: "archive_dev_user",
          user_id: "AIDAQUWY5LJ426CC2RH2V",
          last_used: 0,
          detected_at: 1682054418,
          cloud_account_name: "AWS HQ"
        }
      ],
      limit: 3
    },
    insecure_security_groups: {
      count: 22,
      options: {
        excluded_pools: {},
        insecure_ports: [
          { protocol: "tcp", port: 22 },
          { protocol: "tcp", port: 3389 },
          { protocol: "tcp", port: 1080 }
        ],
        skip_cloud_accounts: []
      },
      items: [
        {
          cloud_resource_id: "i-0f71db3810085eff8",
          resource_name: "test_prefix_kind_lamarr",
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          resource_id: null,
          cloud_type: "aws_cnr",
          security_group_name: "orchid_sg_02f07515-53a6-415c-bd3e-fb8008bd5705",
          security_group_id: "sg-09a275e75309e133a",
          region: "us-west-2",
          is_excluded: false,
          insecure_ports: [{ port: "*", protocol: null }],
          detected_at: 1684226578,
          cloud_account_name: "AWS HQ"
        },
        {
          cloud_resource_id:
            "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/rpage-rg/providers/microsoft.compute/virtualmachines/rpage-arcee",
          resource_name: "rpage-arcee",
          cloud_account_id: "0e01e929-459d-44d5-8dd2-2e320ef463ce",
          resource_id: "c15c0b05-8981-49db-9b9a-a4d6ccf8bb32",
          cloud_type: "azure_cnr",
          security_group_name: "rpagearceensg204",
          security_group_id:
            "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/rpage-rg/providers/Microsoft.Network/networkSecurityGroups/rpagearceensg204",
          region: "East US",
          is_excluded: false,
          insecure_ports: [{ port: 22, protocol: "tcp" }],
          detected_at: 1682995378,
          cloud_account_name: "Dev environment"
        },
        {
          cloud_resource_id:
            "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/rpage-rg/providers/microsoft.compute/virtualmachines/rpage-dev",
          resource_name: "rpage-dev",
          cloud_account_id: "0e01e929-459d-44d5-8dd2-2e320ef463ce",
          resource_id: "d095a9bf-6988-41f4-83f9-ca7b6f734548",
          cloud_type: "azure_cnr",
          security_group_name: "rpagedevnsg971",
          security_group_id:
            "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/rpage-rg/providers/Microsoft.Network/networkSecurityGroups/rpagedevnsg971",
          region: "East US",
          is_excluded: false,
          insecure_ports: [{ port: 22, protocol: "tcp" }],
          detected_at: 1682995378,
          cloud_account_name: "Dev environment"
        }
      ],
      limit: 3
    },
    instance_generation_upgrade: {
      count: 3,
      saving: 11.519999999999984,
      options: { excluded_pools: {}, skip_cloud_accounts: [] },
      items: [
        {
          cloud_resource_id: "i-gw87l0czzy3lr9es2npa",
          resource_name: "aqa-instance-generation-upgrade",
          resource_id: "f0b98d89-13ee-4938-bfe3-34342cbcd7b1",
          cloud_account_id: "5c75d0f5-3c30-4f5d-a92f-d0ea150af205",
          cloud_type: "alibaba_cnr",
          region: "Germany (Frankfurt)",
          owner: { id: "33e28316-f72f-4592-96c6-4766c963519b", name: "Lincoln Morton" },
          pool: { id: "71f91ed4-9c63-4c36-9e2b-5686accf9ba0", name: "Ali dev", purpose: "budget" },
          saving: 11.519999999999984,
          recommended_flavor: "ecs.g7.large",
          is_excluded: false,
          flavor: "ecs.g6.large",
          detected_at: 1681968318,
          cloud_account_name: "Ali dev"
        },
        {
          cloud_resource_id:
            "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/sunflower_env/providers/microsoft.compute/virtualmachines/repo-docker-runner",
          resource_name: "repo-docker-runner",
          resource_id: "958e44e2-c83d-4dfd-bdda-5a3878003c47",
          cloud_account_id: "0e01e929-459d-44d5-8dd2-2e320ef463ce",
          cloud_type: "azure_cnr",
          region: "West US 2",
          owner: { id: "592f435e-0fb9-4719-b110-6a5211b94931", name: "Melody Jackson" },
          pool: { id: "9a4e9cd8-2962-4913-9f75-46db72665999", name: "Dev environment", purpose: "budget" },
          saving: 0.0,
          recommended_flavor: "Standard_D4s_v5",
          is_excluded: false,
          flavor: "Standard_D4s_v3",
          detected_at: 1683794578,
          cloud_account_name: "Dev environment"
        },
        {
          cloud_resource_id:
            "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchid-env/providers/microsoft.compute/virtualmachines/repo-ngui-runner",
          resource_name: "repo-ngui-runner",
          resource_id: "d268dfbb-731e-4058-9c82-13b41b76de68",
          cloud_account_id: "0e01e929-459d-44d5-8dd2-2e320ef463ce",
          cloud_type: "azure_cnr",
          region: "North Europe",
          owner: { id: "592f435e-0fb9-4719-b110-6a5211b94931", name: "Melody Jackson" },
          pool: { id: "9a4e9cd8-2962-4913-9f75-46db72665999", name: "Dev environment", purpose: "budget" },
          saving: 0.0,
          recommended_flavor: "Standard_D4s_v5",
          is_excluded: false,
          flavor: "Standard_D4s_v3",
          detected_at: 1682995378,
          cloud_account_name: "Dev environment"
        }
      ],
      limit: 3
    },
    instance_migration: {
      count: 2,
      saving: 6.9119999999999635,
      options: { excluded_pools: { "f6fafb13-747b-4cb3-bee6-0cb91bc56fbb": true }, skip_cloud_accounts: [] },
      items: [
        {
          saving: 5.7599999999999625,
          flavor: "ecs.g6.large",
          current_region: "Germany (Frankfurt)",
          recommended_region: "UK (London)",
          cloud_resource_id: "i-gw87l0czzy3lr9es2npa",
          resource_name: "aqa-instance-generation-upgrade",
          resource_id: "f0b98d89-13ee-4938-bfe3-34342cbcd7b1",
          cloud_account_id: "5c75d0f5-3c30-4f5d-a92f-d0ea150af205",
          cloud_type: "alibaba_cnr",
          is_excluded: false,
          detected_at: 1683880978,
          cloud_account_name: "Ali dev"
        },
        {
          saving: 1.152000000000001,
          flavor: "t2.micro",
          current_region: "us-west-2",
          recommended_region: "eu-west-1",
          cloud_resource_id: "i-0e5b4e45dbe5f926c",
          resource_name: "sf-test-instance",
          resource_id: "fe815fde-a10e-419f-82f0-26808ddda025",
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          is_excluded: false,
          detected_at: 1682411718,
          cloud_account_name: "AWS HQ"
        }
      ],
      limit: 3
    },
    instance_subscription: {
      count: 4,
      saving: 103.92,
      options: { days_threshold: 90, excluded_pools: {}, skip_cloud_accounts: [] },
      items: [
        {
          monthly_saving: 45.18000000000001,
          annually_monthly_saving: 62.595,
          saving: 62.595,
          invoice_discount: 0.0,
          flavor: "ecs.g6.large",
          region: "Germany (Frankfurt)",
          cloud_resource_id: "i-gw87l0czzy3lr9es2npa",
          resource_name: "aqa-instance-generation-upgrade",
          resource_id: "f0b98d89-13ee-4938-bfe3-34342cbcd7b1",
          cloud_account_id: "5c75d0f5-3c30-4f5d-a92f-d0ea150af205",
          cloud_type: "alibaba_cnr",
          is_excluded: false,
          detected_at: 1681968018,
          cloud_account_name: "Ali dev"
        },
        {
          monthly_saving: 20.080000000000005,
          annually_monthly_saving: 28.73166666666667,
          saving: 28.73166666666667,
          invoice_discount: 0.0,
          flavor: "ecs.n4.large",
          region: "Germany (Frankfurt)",
          cloud_resource_id: "i-gw8bwy1fbwc2spcyqhdy",
          resource_name: "aqa-eu-underutilized-instance",
          resource_id: "c3a0703f-b327-42ce-be0d-6201d0053611",
          cloud_account_id: "5c75d0f5-3c30-4f5d-a92f-d0ea150af205",
          cloud_type: "alibaba_cnr",
          is_excluded: false,
          detected_at: 1681968018,
          cloud_account_name: "Ali dev"
        },
        {
          monthly_saving: 5.699999999999999,
          annually_monthly_saving: 7.868333333333334,
          saving: 7.868333333333334,
          invoice_discount: 0.0,
          flavor: "ecs.xn4.small",
          region: "Germany (Frankfurt)",
          cloud_resource_id: "i-gw82aj70q09wmkmr18l0",
          resource_name: "aqa-alibaba-short-living-instance",
          resource_id: "45fb006d-1133-470c-bb67-eb583bd3b59a",
          cloud_account_id: "5c75d0f5-3c30-4f5d-a92f-d0ea150af205",
          cloud_type: "alibaba_cnr",
          is_excluded: false,
          detected_at: 1681968018,
          cloud_account_name: "Ali dev"
        }
      ],
      limit: 3
    },
    instances_for_shutdown: {
      count: 14,
      saving: 696.6241708191084,
      options: {
        days_threshold: 15,
        cpu_percent_threshold: 6,
        network_bps_threshold: 1001,
        excluded_pools: {},
        skip_cloud_accounts: []
      },
      items: [
        {
          resource_id: "f0b98d89-13ee-4938-bfe3-34342cbcd7b1",
          resource_name: "aqa-instance-generation-upgrade",
          cloud_resource_id: "i-gw87l0czzy3lr9es2npa",
          region: "Germany (Frankfurt)",
          cloud_account_id: "5c75d0f5-3c30-4f5d-a92f-d0ea150af205",
          cloud_type: "alibaba_cnr",
          owner: { id: "33e28316-f72f-4592-96c6-4766c963519b", name: "Lincoln Morton" },
          pool: { id: "71f91ed4-9c63-4c36-9e2b-5686accf9ba0", name: "Ali dev", purpose: "budget" },
          is_excluded: false,
          inactivity_periods: [
            { start: { day_of_week: 0, hour: 0 }, end: { day_of_week: 3, hour: 11 } },
            { start: { day_of_week: 3, hour: 13 }, end: { day_of_week: 6, hour: 23 } }
          ],
          saving: 176.4156190476191,
          detected_at: 1681972518,
          cloud_account_name: "Ali dev"
        },
        {
          resource_id: "958e44e2-c83d-4dfd-bdda-5a3878003c47",
          resource_name: "repo-docker-runner",
          cloud_resource_id:
            "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/sunflower_env/providers/microsoft.compute/virtualmachines/repo-docker-runner",
          region: "West US 2",
          cloud_account_id: "0e01e929-459d-44d5-8dd2-2e320ef463ce",
          cloud_type: "azure_cnr",
          owner: { id: "592f435e-0fb9-4719-b110-6a5211b94931", name: "Melody Jackson" },
          pool: { id: "9a4e9cd8-2962-4913-9f75-46db72665999", name: "Dev environment", purpose: "budget" },
          is_excluded: false,
          inactivity_periods: [
            { start: { day_of_week: 0, hour: 0 }, end: { day_of_week: 0, hour: 4 } },
            { start: { day_of_week: 0, hour: 10 }, end: { day_of_week: 0, hour: 10 } },
            { start: { day_of_week: 0, hour: 13 }, end: { day_of_week: 0, hour: 14 } },
            { start: { day_of_week: 0, hour: 16 }, end: { day_of_week: 0, hour: 23 } },
            { start: { day_of_week: 1, hour: 1 }, end: { day_of_week: 1, hour: 4 } },
            { start: { day_of_week: 1, hour: 15 }, end: { day_of_week: 1, hour: 20 } },
            { start: { day_of_week: 1, hour: 22 }, end: { day_of_week: 2, hour: 3 } },
            { start: { day_of_week: 2, hour: 14 }, end: { day_of_week: 2, hour: 14 } },
            { start: { day_of_week: 2, hour: 17 }, end: { day_of_week: 3, hour: 0 } },
            { start: { day_of_week: 3, hour: 4 }, end: { day_of_week: 3, hour: 4 } },
            { start: { day_of_week: 3, hour: 16 }, end: { day_of_week: 3, hour: 23 } },
            { start: { day_of_week: 4, hour: 1 }, end: { day_of_week: 4, hour: 4 } },
            { start: { day_of_week: 4, hour: 15 }, end: { day_of_week: 4, hour: 15 } },
            { start: { day_of_week: 4, hour: 17 }, end: { day_of_week: 5, hour: 5 } },
            { start: { day_of_week: 5, hour: 12 }, end: { day_of_week: 5, hour: 12 } },
            { start: { day_of_week: 5, hour: 16 }, end: { day_of_week: 5, hour: 17 } },
            { start: { day_of_week: 5, hour: 20 }, end: { day_of_week: 6, hour: 23 } }
          ],
          saving: 162.641389459265,
          detected_at: 1682995378,
          cloud_account_name: "Dev environment"
        },
        {
          resource_id: "83a0c055-870b-49d5-a662-eac2794f89af",
          resource_name: "finops-practice",
          cloud_resource_id: "i-0e464cfbf9650bd21",
          region: "us-west-2",
          cloud_account_id: "55411117-fa1f-4e21-b119-a33faf04d070",
          cloud_type: "aws_cnr",
          owner: { id: "592f435e-0fb9-4719-b110-6a5211b94931", name: "Melody Jackson" },
          pool: { id: "0558f556-ef63-4e0d-bbde-c786f5aef441", name: "AWS Marketing", purpose: "budget" },
          is_excluded: false,
          inactivity_periods: [
            { start: { day_of_week: 0, hour: 0 }, end: { day_of_week: 0, hour: 8 } },
            { start: { day_of_week: 0, hour: 10 }, end: { day_of_week: 0, hour: 12 } },
            { start: { day_of_week: 0, hour: 14 }, end: { day_of_week: 0, hour: 14 } },
            { start: { day_of_week: 0, hour: 17 }, end: { day_of_week: 0, hour: 23 } },
            { start: { day_of_week: 1, hour: 1 }, end: { day_of_week: 1, hour: 5 } },
            { start: { day_of_week: 1, hour: 7 }, end: { day_of_week: 1, hour: 7 } },
            { start: { day_of_week: 1, hour: 10 }, end: { day_of_week: 1, hour: 11 } },
            { start: { day_of_week: 1, hour: 19 }, end: { day_of_week: 2, hour: 7 } },
            { start: { day_of_week: 2, hour: 10 }, end: { day_of_week: 2, hour: 10 } },
            { start: { day_of_week: 2, hour: 16 }, end: { day_of_week: 2, hour: 17 } },
            { start: { day_of_week: 2, hour: 19 }, end: { day_of_week: 3, hour: 5 } },
            { start: { day_of_week: 3, hour: 8 }, end: { day_of_week: 3, hour: 8 } },
            { start: { day_of_week: 3, hour: 11 }, end: { day_of_week: 3, hour: 11 } },
            { start: { day_of_week: 3, hour: 13 }, end: { day_of_week: 3, hour: 13 } },
            { start: { day_of_week: 3, hour: 15 }, end: { day_of_week: 3, hour: 16 } },
            { start: { day_of_week: 3, hour: 21 }, end: { day_of_week: 4, hour: 5 } },
            { start: { day_of_week: 4, hour: 7 }, end: { day_of_week: 4, hour: 7 } },
            { start: { day_of_week: 4, hour: 9 }, end: { day_of_week: 4, hour: 9 } },
            { start: { day_of_week: 4, hour: 11 }, end: { day_of_week: 4, hour: 11 } },
            { start: { day_of_week: 4, hour: 13 }, end: { day_of_week: 4, hour: 14 } },
            { start: { day_of_week: 4, hour: 16 }, end: { day_of_week: 4, hour: 17 } },
            { start: { day_of_week: 4, hour: 19 }, end: { day_of_week: 4, hour: 19 } },
            { start: { day_of_week: 4, hour: 21 }, end: { day_of_week: 5, hour: 7 } },
            { start: { day_of_week: 5, hour: 9 }, end: { day_of_week: 5, hour: 12 } },
            { start: { day_of_week: 5, hour: 14 }, end: { day_of_week: 5, hour: 15 } },
            { start: { day_of_week: 5, hour: 17 }, end: { day_of_week: 6, hour: 23 } }
          ],
          saving: 99.36719791517858,
          detected_at: 1682628178,
          cloud_account_name: "AWS Marketing"
        }
      ],
      limit: 3
    },
    instances_in_stopped_state_for_a_long_time: {
      count: 3,
      saving: 64.2361089135484,
      options: { days_threshold: 1, excluded_pools: {}, skip_cloud_accounts: [] },
      items: [
        {
          cloud_resource_id:
            "/subscriptions/318bd278-e4ef-4230-9ab4-2ad6a29f578c/resourcegroups/aqa/providers/microsoft.compute/virtualmachines/aqa-stopped-not-deallocated",
          resource_name: "aqa-stopped-not-deallocated",
          resource_id: "2a91acd8-b3b7-45e6-abd6-193e065a0952",
          cloud_account_id: "7fe9deb8-2577-4b8b-b5ed-175bc3181450",
          cloud_type: "azure_cnr",
          cost_in_stopped_state: 69.54090816297142,
          saving: 34.278970343225815,
          region: "Germany West Central",
          is_excluded: false,
          last_seen_active: 0,
          detected_at: 1682584978,
          cloud_account_name: "Azure QA"
        },
        {
          cloud_resource_id:
            "/subscriptions/318bd278-e4ef-4230-9ab4-2ad6a29f578c/resourcegroups/aqa/providers/microsoft.compute/virtualmachines/stop-not-deallocated-test",
          resource_name: "stop-not-deallocated-test",
          resource_id: "f4da51a1-d65f-4d86-b029-33172aeff325",
          cloud_account_id: "7fe9deb8-2577-4b8b-b5ed-175bc3181450",
          cloud_type: "azure_cnr",
          cost_in_stopped_state: 34.756604927999994,
          saving: 17.13213857032258,
          region: "Germany West Central",
          is_excluded: false,
          last_seen_active: 0,
          detected_at: 1682584978,
          cloud_account_name: "Azure QA"
        },
        {
          cloud_resource_id: "i-gw8692qiefklcvhgc75e",
          resource_name: "aqa-stopped-not-deallocated",
          resource_id: "e58786ee-d883-4d7e-b5f2-dbb031abce56",
          cloud_account_id: "5c75d0f5-3c30-4f5d-a92f-d0ea150af205",
          cloud_type: "alibaba_cnr",
          cost_in_stopped_state: 26.280000000000015,
          saving: 12.825000000000003,
          region: "Germany (Frankfurt)",
          is_excluded: false,
          last_seen_active: 0,
          detected_at: 1681968318,
          cloud_account_name: "Ali dev"
        }
      ],
      limit: 3
    },
    obsolete_images: {
      count: 87,
      saving: 156.72873782219997,
      options: { days_threshold: 7, skip_cloud_accounts: [] },
      items: [
        {
          cloud_resource_id: "ami-06f4e737af7d45d1b",
          resource_name: "sunflower_lily_VA_DR_AWS_3_9_2066-release_3_9",
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          region: "us-west-2",
          last_used: 0,
          saving: 5.4391921906,
          snapshots: [
            {
              cloud_resource_id: "snap-0b14b0f5690db4384",
              resource_id: "ace55d86-cd32-4185-8a05-4d538751dd18",
              cost: 2.7195960953
            }
          ],
          first_seen: 1663761975,
          detected_at: 1681967718,
          cloud_account_name: "AWS HQ"
        },
        {
          cloud_resource_id: "ami-007af5b6be13d6765",
          resource_name: "sunflower_lily_VA_MGR_AWS_3_7_1701-release_3_7",
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          region: "us-west-2",
          last_used: 0,
          saving: 5.1208488258,
          snapshots: [
            {
              cloud_resource_id: "snap-0ccbccb24d31ffd6f",
              resource_id: "de08f9d4-8a4f-4794-8c0a-c665994bf29d",
              cost: 2.5604244129
            }
          ],
          first_seen: 1631175628,
          detected_at: 1681967718,
          cloud_account_name: "AWS HQ"
        },
        {
          cloud_resource_id: "ami-0bbceb7fb22af85bd",
          resource_name: "sunflower_lily_VA_DR_AWS_3_9_2066-release_3_9",
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          region: "us-east-2",
          last_used: 0,
          saving: 5.0362890656,
          snapshots: [
            {
              cloud_resource_id: "snap-09e187c95dfdaa1ee",
              resource_id: "03ff8041-03bb-4cab-ab7a-57c7ab6ff77d",
              cost: 2.5181445328
            }
          ],
          first_seen: 1660299423,
          detected_at: 1681967718,
          cloud_account_name: "AWS HQ"
        }
      ],
      limit: 3
    },
    obsolete_ips: {
      count: 27,
      saving: 160.41066040496275,
      options: { days_threshold: 7, excluded_pools: {}, skip_cloud_accounts: [] },
      items: [
        {
          cloud_resource_id: "eip-gw80wgx89t7t7p3x2ah7y",
          resource_name: "aqa-obsolete-ip",
          resource_id: "110149d3-87ff-45e6-940e-eab72ba29105",
          cloud_account_id: "5c75d0f5-3c30-4f5d-a92f-d0ea150af205",
          cloud_type: "alibaba_cnr",
          cost_not_active_ip: 17.520000000000007,
          saving: 8.55,
          region: "Germany (Frankfurt)",
          is_excluded: false,
          last_seen_active: 0,
          detected_at: 1681968018,
          cloud_account_name: "Ali dev"
        },
        {
          cloud_resource_id: "eip-gw8f117dmb0k4e4nkobsl",
          resource_name: "ds-test",
          resource_id: "789d0671-b43c-413e-81b1-b569c23089d4",
          cloud_account_id: "5c75d0f5-3c30-4f5d-a92f-d0ea150af205",
          cloud_type: "alibaba_cnr",
          cost_not_active_ip: 17.520000000000007,
          saving: 8.55,
          region: "Germany (Frankfurt)",
          is_excluded: false,
          last_seen_active: 0,
          detected_at: 1681968018,
          cloud_account_name: "Ali dev"
        },
        {
          cloud_resource_id:
            "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/tm-arcee_group/providers/microsoft.network/publicipaddresses/tm-arcee1-ip",
          resource_name: "tm-arcee1-ip",
          resource_id: "ee638e41-7fff-4250-a525-a2960fc6ed64",
          cloud_account_id: "0e01e929-459d-44d5-8dd2-2e320ef463ce",
          cloud_type: "azure_cnr",
          cost_not_active_ip: 7.405000000000004,
          saving: 7.200000000000003,
          region: "North Europe",
          is_excluded: false,
          last_seen_active: 0,
          detected_at: 1681968018,
          cloud_account_name: "Dev environment"
        }
      ],
      limit: 3
    },
    obsolete_snapshot_chains: {
      count: 4,
      saving: 3.4367706,
      options: { days_threshold: 3, excluded_pools: {}, skip_cloud_accounts: [] },
      items: [
        {
          cloud_resource_id: "sl-gw8f5fd047rk84g9t973",
          resource_name: null,
          resource_id: "6e4cd878-6576-46e6-9279-0f9cfc617508",
          cloud_account_id: "5c75d0f5-3c30-4f5d-a92f-d0ea150af205",
          cloud_type: "alibaba_cnr",
          saving: 1.5765479999999998,
          region: "Germany (Frankfurt)",
          last_used: 0,
          is_excluded: false,
          child_snapshots: [
            {
              cloud_resource_id: "s-gw8h0b454q5zxeyeulsm",
              name: "sunflower_lily_VA_MGR_Alibaba_3_9_om20221228-feature_cloud7_en",
              cloud_console_link:
                "https://ecs.console.aliyun.com/#/snapshot/region/eu-central-1?snapshotIds=s-gw8h0b454q5zxeyeulsm"
            }
          ],
          first_seen: 1681344000,
          last_seen: 1683936000,
          detected_at: 1681968018,
          cloud_account_name: "Ali dev"
        },
        {
          cloud_resource_id: "sl-gw84m857olspqve95jb9",
          resource_name: null,
          resource_id: "2b508d50-41d6-477b-9015-6aa11805b0c8",
          cloud_account_id: "5c75d0f5-3c30-4f5d-a92f-d0ea150af205",
          cloud_type: "alibaba_cnr",
          saving: 1.5207642,
          region: "Germany (Frankfurt)",
          last_used: 0,
          is_excluded: false,
          child_snapshots: [
            {
              cloud_resource_id: "s-gw8f5fd047rk6z0mpkx8",
              name: "sunflower_lily_VA_DR_Alibaba_3_9_om20221228-feature_cloud7_en",
              cloud_console_link:
                "https://ecs.console.aliyun.com/#/snapshot/region/eu-central-1?snapshotIds=s-gw8f5fd047rk6z0mpkx8"
            }
          ],
          first_seen: 1681344000,
          last_seen: 1683936000,
          detected_at: 1681968018,
          cloud_account_name: "Ali dev"
        },
        {
          cloud_resource_id: "sl-gw8d2sicdq9oq331hb05",
          resource_name: null,
          resource_id: "a98efeb7-1058-477e-9f24-d71a0bbc732e",
          cloud_account_id: "5c75d0f5-3c30-4f5d-a92f-d0ea150af205",
          cloud_type: "alibaba_cnr",
          saving: 0.17989560000000004,
          region: "Germany (Frankfurt)",
          last_used: 0,
          is_excluded: false,
          child_snapshots: [
            {
              cloud_resource_id: "s-gw85a66uwrbpu8ef27r4",
              name: "ds-test",
              cloud_console_link:
                "https://ecs.console.aliyun.com/#/snapshot/region/eu-central-1?snapshotIds=s-gw85a66uwrbpu8ef27r4"
            }
          ],
          first_seen: 1681344000,
          last_seen: 1683936000,
          detected_at: 1681968018,
          cloud_account_name: "Ali dev"
        }
      ],
      limit: 3
    },
    obsolete_snapshots: {
      count: 45,
      saving: 102.1023174072,
      options: { days_threshold: 4, excluded_pools: {}, skip_cloud_accounts: [] },
      items: [
        {
          cloud_resource_id: "snap-05ee454deeffe599a",
          resource_name: null,
          resource_id: "83013424-b63d-467c-9978-047cd71c817a",
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          saving: 4.799169875999999,
          region: "us-west-2",
          last_used: 0,
          is_excluded: false,
          child_snapshots: null,
          first_seen: 1681257600,
          last_seen: 1683849600,
          detected_at: 1682054418,
          cloud_account_name: "AWS HQ"
        },
        {
          cloud_resource_id: "snap-04b96eca0fa400096",
          resource_name: null,
          resource_id: "ca7b14dc-03e4-4287-a74b-861458932ec9",
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          saving: 4.571728201199999,
          region: "us-east-1",
          last_used: 0,
          is_excluded: false,
          child_snapshots: null,
          first_seen: 1681257600,
          last_seen: 1683849600,
          detected_at: 1682054418,
          cloud_account_name: "AWS HQ"
        },
        {
          cloud_resource_id: "snap-0f8f3562ed71e18b5",
          resource_name: null,
          resource_id: "cb2a5e8e-a2b1-436c-8812-2de1ddf4f929",
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          saving: 4.4941959126,
          region: "us-east-1",
          last_used: 0,
          is_excluded: false,
          child_snapshots: null,
          first_seen: 1681257600,
          last_seen: 1683849600,
          detected_at: 1682054418,
          cloud_account_name: "AWS HQ"
        }
      ],
      limit: 3
    },
    reserved_instances: {
      count: 6,
      saving: 22.175999999999977,
      options: { days_threshold: 90, excluded_pools: {}, skip_cloud_accounts: [] },
      items: [
        {
          saving: 7.055999999999983,
          average_saving: 14.732666666666667,
          flavor: "t2.large",
          region: "us-west-2",
          cloud_resource_id: "i-0e464cfbf9650bd21",
          resource_name: "finops-practice",
          resource_id: "83a0c055-870b-49d5-a662-eac2794f89af",
          cloud_account_id: "55411117-fa1f-4e21-b119-a33faf04d070",
          cloud_type: "aws_cnr",
          is_excluded: false,
          detected_at: 1682628178,
          cloud_account_name: "AWS Marketing"
        },
        {
          saving: 4.032,
          average_saving: 3.519333333333333,
          flavor: "t2.micro",
          region: "us-west-1",
          cloud_resource_id: "i-0436ee72bb653bf8a",
          resource_name: "aqa_us_instance_for_migration",
          resource_id: "34c9fbae-b66f-484b-8cfa-dae16b6f7dd5",
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          is_excluded: false,
          detected_at: 1681967718,
          cloud_account_name: "AWS HQ"
        },
        {
          saving: 3.5999999999999943,
          average_saving: 7.408000000000001,
          flavor: "t2.medium",
          region: "us-east-1",
          cloud_resource_id: "i-0729a34d6f5b91f83",
          resource_name: "aqa_us_underutilized_instance",
          resource_id: "25eef7ae-6d85-403c-9587-24c0f168d881",
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          is_excluded: false,
          detected_at: 1681967718,
          cloud_account_name: "AWS HQ"
        }
      ],
      limit: 3
    },
    rightsizing_instances: {
      count: 30,
      saving: 2217.16,
      options: {
        days_threshold: 3,
        metric: { type: "avg", limit: 80 },
        excluded_flavor_regex: "",
        excluded_pools: { "3a248797-84f6-46b8-b6b9-9aa612105d1e": true, "9ef6f469-434d-4937-80b0-6eea3085deb6": true },
        recommended_flavor_cpu_min: 1,
        skip_cloud_accounts: []
      },
      items: [
        {
          cloud_resource_id: "7507845845786615869",
          resource_name: "ml-profiling-cluster",
          resource_id: null,
          cloud_account_id: "d284bef4-962c-4d92-a0ce-ca7064854ad4",
          cloud_type: "gcp_cnr",
          region: "us-central1",
          flavor: "e2-standard-4",
          recommended_flavor: "e2-highcpu-2",
          saving: 121.76,
          saving_percent: 63.09,
          current_cost: 96.5,
          recommended_flavor_cost: 35.62,
          cpu: 4,
          recommended_flavor_cpu: 2,
          recommended_flavor_ram: 2.0,
          cpu_usage: 31.11,
          is_excluded: false,
          cpu_peak: 62.1,
          cpu_quantile_50: 30.24,
          cpu_quantile_99: 61.53,
          project_cpu_avg: 62.23,
          project_cpu_peak: 100,
          projected_cpu_qtl_50: 60.47,
          projected_cpu_qtl_99: 100,
          detected_at: 1683578578,
          cloud_account_name: "GCP dev"
        },
        {
          cloud_resource_id: "i-082b1a163698b8ede",
          resource_name: "sunflowerWebSite",
          resource_id: "c86f18d4-c8be-48a2-97e2-72a998096c3b",
          cloud_account_id: "55411117-fa1f-4e21-b119-a33faf04d070",
          cloud_type: "aws_cnr",
          region: "us-west-2",
          flavor: "t2.large",
          recommended_flavor: "t2.small",
          saving: 100.52,
          saving_percent: 244.27,
          current_cost: 20.57,
          recommended_flavor_cost: 16.56,
          cpu: 2,
          recommended_flavor_cpu: 1,
          recommended_flavor_ram: 2048,
          cpu_usage: 1.61,
          is_excluded: false,
          cpu_peak: 8.98,
          cpu_quantile_50: 1.41,
          cpu_quantile_99: 6.34,
          project_cpu_avg: 3.23,
          project_cpu_peak: 17.97,
          projected_cpu_qtl_50: 2.82,
          projected_cpu_qtl_99: 12.67,
          detected_at: 1682628178,
          cloud_account_name: "AWS Marketing"
        },
        {
          cloud_resource_id: "i-0e464cfbf9650bd21",
          resource_name: "finops-practice",
          resource_id: "83a0c055-870b-49d5-a662-eac2794f89af",
          cloud_account_id: "55411117-fa1f-4e21-b119-a33faf04d070",
          cloud_type: "aws_cnr",
          region: "us-west-2",
          flavor: "t2.large",
          recommended_flavor: "t2.small",
          saving: 100.52,
          saving_percent: 244.27,
          current_cost: 20.57,
          recommended_flavor_cost: 16.56,
          cpu: 2,
          recommended_flavor_cpu: 1,
          recommended_flavor_ram: 2048,
          cpu_usage: 0.58,
          is_excluded: false,
          cpu_peak: 5.85,
          cpu_quantile_50: 0.51,
          cpu_quantile_99: 1.69,
          project_cpu_avg: 1.17,
          project_cpu_peak: 11.7,
          projected_cpu_qtl_50: 1.02,
          projected_cpu_qtl_99: 3.39,
          detected_at: 1682628178,
          cloud_account_name: "AWS Marketing"
        }
      ],
      limit: 3
    },
    rightsizing_rds: {
      count: 0,
      saving: 0,
      options: {
        days_threshold: 7,
        metric: { type: "avg", limit: 81 },
        excluded_flavor_regex: "",
        excluded_pools: {},
        recommended_flavor_cpu_min: 1,
        skip_cloud_accounts: []
      },
      items: []
    },
    s3_abandoned_buckets: {
      count: 45,
      saving: 41.86222697914286,
      options: {
        days_threshold: 7,
        data_size_threshold: 1024,
        tier_1_request_quantity_threshold: 100,
        tier_2_request_quantity_threshold: 2000,
        excluded_pools: {},
        skip_cloud_accounts: []
      },
      items: [
        {
          cloud_resource_id: "yv-bucket",
          resource_name: "yv-bucket",
          resource_id: "186d40d1-07d4-4663-bdf5-c22e40670a70",
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          region: "us-west-2",
          owner: { id: "33e28316-f72f-4592-96c6-4766c963519b", name: "Lincoln Morton" },
          pool: { id: "6c936baf-5045-4326-9c8e-52337e56a19c", name: "AWS HQ", purpose: "budget" },
          is_excluded: false,
          avg_data_size: 3.441327367314286,
          tier_1_request_quantity: 1,
          tier_2_request_quantity: 0,
          saving: 19.520247625714287,
          detected_at: 1682390118,
          cloud_account_name: "AWS HQ"
        },
        {
          cloud_resource_id: "sunflower-ap-south-1",
          resource_name: "sunflower-ap-south-1",
          resource_id: "8d68af60-81ef-40f5-89ef-9197d589ace7",
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          region: "ap-south-1",
          owner: { id: "33e28316-f72f-4592-96c6-4766c963519b", name: "Lincoln Morton" },
          pool: { id: "6c936baf-5045-4326-9c8e-52337e56a19c", name: "AWS HQ", purpose: "budget" },
          is_excluded: false,
          avg_data_size: 3.900675130514286,
          tier_1_request_quantity: 1,
          tier_2_request_quantity: 0,
          saving: 2.529079726285714,
          detected_at: 1681967718,
          cloud_account_name: "AWS HQ"
        },
        {
          cloud_resource_id: "sunflower-us-east-1",
          resource_name: "sunflower-us-east-1",
          resource_id: "38b362fa-afaa-4eea-b24c-2d6a6aa287b5",
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          region: "us-east-1",
          owner: { id: "33e28316-f72f-4592-96c6-4766c963519b", name: "Lincoln Morton" },
          pool: { id: "6c936baf-5045-4326-9c8e-52337e56a19c", name: "AWS HQ", purpose: "budget" },
          is_excluded: false,
          avg_data_size: 3.9984587190857144,
          tier_1_request_quantity: 1,
          tier_2_request_quantity: 0,
          saving: 2.207960509714286,
          detected_at: 1681967718,
          cloud_account_name: "AWS HQ"
        }
      ],
      limit: 3
    },
    s3_public_buckets: {
      count: 2,
      options: { excluded_pools: {}, skip_cloud_accounts: [] },
      items: [
        {
          cloud_resource_id: "ds-report-bucket",
          resource_name: "ds-report-bucket",
          resource_id: "f40d2f82-a036-4e98-93c4-8e064eeffd3e",
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          region: "us-west-2",
          owner: { id: "33e28316-f72f-4592-96c6-4766c963519b", name: "Lincoln Morton" },
          pool: { id: "6c936baf-5045-4326-9c8e-52337e56a19c", name: "AWS HQ", purpose: "budget" },
          is_excluded: false,
          is_public_policy: true,
          is_public_acls: true,
          detected_at: 1681967718,
          cloud_account_name: "AWS HQ"
        },
        {
          cloud_resource_id: "sunflower-static-files",
          resource_name: "sunflower-static-files",
          resource_id: "e8a171d5-6e05-4101-adb2-a474868eaf57",
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          region: "us-east-1",
          owner: { id: "33e28316-f72f-4592-96c6-4766c963519b", name: "Lincoln Morton" },
          pool: { id: "6c936baf-5045-4326-9c8e-52337e56a19c", name: "AWS HQ", purpose: "budget" },
          is_excluded: false,
          is_public_policy: true,
          is_public_acls: false,
          detected_at: 1681967718,
          cloud_account_name: "AWS HQ"
        }
      ],
      limit: 3
    },
    short_living_instances: {
      count: 10,
      saving: 0.11753962963199999,
      options: { days_threshold: 3, excluded_pools: {}, skip_cloud_accounts: [] },
      items: [
        {
          cloud_resource_id:
            "/subscriptions/318bd278-e4ef-4230-9ab4-2ad6a29f578c/resourcegroups/aqa/providers/microsoft.compute/virtualmachines/aqa-azure-short-living-instance-905",
          resource_name: "aqa-azure-short-living-instance-905",
          resource_id: null,
          cloud_account_id: "7fe9deb8-2577-4b8b-b5ed-175bc3181450",
          cloud_type: "azure_cnr",
          total_cost: 0.012400251017485,
          saving: 0.01785635712,
          region: "Germany West Central",
          is_excluded: false,
          first_seen: 1684108800,
          last_seen: 0,
          detected_at: 1684237378,
          cloud_account_name: "Azure QA"
        },
        {
          cloud_resource_id:
            "/subscriptions/318bd278-e4ef-4230-9ab4-2ad6a29f578c/resourcegroups/aqa/providers/microsoft.compute/virtualmachines/aqa-azure-short-living-instance-233",
          resource_name: "aqa-azure-short-living-instance-233",
          resource_id: null,
          cloud_account_id: "7fe9deb8-2577-4b8b-b5ed-175bc3181450",
          cloud_type: "azure_cnr",
          total_cost: 0.012400250011657002,
          saving: 0.01785635712,
          region: "Germany West Central",
          is_excluded: false,
          first_seen: 1684022400,
          last_seen: 1684108800,
          detected_at: 1684150978,
          cloud_account_name: "Azure QA"
        },
        {
          cloud_resource_id:
            "/subscriptions/318bd278-e4ef-4230-9ab4-2ad6a29f578c/resourcegroups/aqa/providers/microsoft.compute/virtualmachines/aqa-azure-short-living-instance-904",
          resource_name: "aqa-azure-short-living-instance-904",
          resource_id: null,
          cloud_account_id: "7fe9deb8-2577-4b8b-b5ed-175bc3181450",
          cloud_type: "azure_cnr",
          total_cost: 0.012400248,
          saving: 0.01785635712,
          region: "Germany West Central",
          is_excluded: false,
          first_seen: 1684022400,
          last_seen: 1684108800,
          detected_at: 1684140178,
          cloud_account_name: "Azure QA"
        }
      ],
      limit: 3
    },
    volumes_not_attached_for_a_long_time: {
      count: 41,
      saving: 284.6306119109032,
      options: {
        days_threshold: 3,
        excluded_pools: {
          "bbf504b7-a1a4-483a-bc6a-a27c6bdcc0dc": true,
          "cd7714e5-9bdd-4408-b380-1fc2bec648a9": true,
          "54704172-af6c-4c91-bf78-5e59ad3ace11": true,
          "cbefe6bf-5515-4f26-9a6d-75b2259ba158": true,
          "f6fafb13-747b-4cb3-bee6-0cb91bc56fbb": true
        },
        skip_cloud_accounts: []
      },
      items: [
        {
          cloud_resource_id:
            "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/mgr-demo-stand/providers/microsoft.compute/disks/ubuntu-slave3_8b8fed63-fe45-f9a9-bcaa-a1d1e8b4cdbd_kepkmczmbcvafassdryeff",
          resource_name: "ubuntu-slave3_8b8fed63-fe45-f9a9-bcaa-a1d1e8b4cdbd_kEPkmczMbCvafAsSdrYefF",
          resource_id: "1870f0de-f583-4251-bf0f-bc9c57001d8c",
          cloud_account_id: "0e01e929-459d-44d5-8dd2-2e320ef463ce",
          cloud_type: "azure_cnr",
          cost_in_detached_state: 34.09182720000001,
          saving: 81.82038528000004,
          region: "Germany West Central",
          is_excluded: false,
          last_seen_in_attached_state: 1682067635,
          detected_at: 1682163318,
          cloud_account_name: "Dev environment"
        },
        {
          cloud_resource_id: "vol-0afae39442f921eb2",
          resource_name: "tulipVPN_0",
          resource_id: "e3ae7b79-3020-4dda-a15e-ea155c1ac113",
          cloud_account_id: "1ef6f7ed-4600-4541-a6d7-43fc151feeb9",
          cloud_type: "aws_cnr",
          cost_in_detached_state: 61.17231262979999,
          saving: 29.954153374838707,
          region: "us-west-2",
          is_excluded: false,
          last_seen_in_attached_state: 0,
          detected_at: 1682228118,
          cloud_account_name: "AWS HQ"
        },
        {
          cloud_resource_id:
            "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/sunflower_env/providers/microsoft.compute/disks/repo-docker-runner_c97e0b19-2a9c-a9fa-a6b7-37e1f11f2bb9_9wytopsxpykgbu77ig8byi",
          resource_name: "repo-docker-runner_c97e0b19-2a9c-a9fa-a6b7-37e1f11f2bb9_9WyToPSxpYkgbU77iG8BYi",
          resource_id: "b3c8686b-a6bd-4e39-8fc4-5ce07875f0cb",
          cloud_account_id: "0e01e929-459d-44d5-8dd2-2e320ef463ce",
          cloud_type: "azure_cnr",
          cost_in_detached_state: 45.676127231999985,
          saving: 22.63413330580645,
          region: "West US 2",
          is_excluded: false,
          last_seen_in_attached_state: 0,
          detected_at: 1681968318,
          cloud_account_name: "Dev environment"
        }
      ],
      limit: 3
    }
  },
  dismissed_optimizations: {
    instances_in_stopped_state_for_a_long_time: { count: 1, saving: 17.13213857032258 },
    s3_public_buckets: { count: 1 },
    volumes_not_attached_for_a_long_time: { count: 3, saving: 69.88859608064516 }
  },
  excluded_optimizations: {
    instance_migration: { count: 2, saving: 4.32 },
    rightsizing_instances: { count: 39, saving: 6610.8 },
    volumes_not_attached_for_a_long_time: { count: 1, saving: 3.0490571148387096 }
  },
  deleted_at: 0,
  id: "8b348dc0-510c-48d0-9c28-2b521e0b5eb0",
  created_at: 1681967418,
  organization_id: "f3360466-1b66-4276-9dbc-3f456ee2065a",
  last_run: 1684237378,
  next_run: 1684248178,
  last_completed: 1684237378
};

export { MOCKED_DATA };
