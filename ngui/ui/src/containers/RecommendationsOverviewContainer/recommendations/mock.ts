const mock = {
  total_saving: 260.47940127190583,
  optimizations: {
    abandoned_instances: {
      count: 4,
      saving: 50.801531420571436
    },
    abandoned_kinesis_streams: {
      count: 1,
      saving: 12.959999999999997
    },
    inactive_console_users: {
      count: 4
    },
    inactive_users: {
      count: 26
    },
    insecure_security_groups: {
      count: 13
    },
    instance_generation_upgrade: {
      count: 0,
      saving: 0
    },
    instance_migration: {
      count: 1,
      saving: 0.5760000000000005
    },
    // # TODO: update after live demo dataset is updated
    nebius_migration: {
      count: 2,
      saving: 3.12355512
    },
    instance_subscription: {
      count: 0,
      saving: 0
    },
    instances_for_shutdown: {
      count: 3,
      saving: 11.955731333654445
    },
    instances_in_stopped_state_for_a_long_time: {
      count: 2,
      saving: 16.941826211566777
    },
    obsolete_images: {
      count: 42,
      saving: 52.86517971180001,
      options: {
        days_threshold: 7,
        skip_cloud_accounts: []
      },
      items: [
        {
          cloud_resource_id: "ami-06f4e737af7d45d1b",
          resource_name: "Hystax_Acura_VA_DR_AWS_3_9_2066-release_3_9",
          cloud_account_id: "5b6267b0-b174-4572-aa5e-6e540ed208c1",
          cloud_type: "aws_cnr",
          first_seen: 1662552374,
          region: "eu-central-1",
          last_used: 1662724808,
          saving: 2.6318671865,
          snapshots: [
            {
              cloud_resource_id: "snap-0b14b0f5690db4384",
              resource_id: "95428d22-0bfa-4d31-9564-122097d516d9",
              cost: 2.6318671865
            }
          ],
          detected_at: 1676272275,
          cloud_account_name: "AWS Main"
        },
        {
          cloud_resource_id: "ami-007af5b6be13d6765",
          resource_name: "Hystax_Acura_VA_MGR_AWS_3_7_1701-release_3_7",
          cloud_account_id: "5b6267b0-b174-4572-aa5e-6e540ed208c1",
          cloud_type: "aws_cnr",
          first_seen: 1629966028,
          region: "eu-central-1",
          last_used: 1631698035,
          saving: 2.4778300775,
          snapshots: [
            {
              cloud_resource_id: "snap-0ccbccb24d31ffd6f",
              resource_id: "d7bac614-bf2d-4bd3-8b5d-730dabc7ee16",
              cost: 2.4778300775
            }
          ],
          detected_at: 1676272275,
          cloud_account_name: "AWS Main"
        }
      ],
      limit: 2
    },
    obsolete_ips: {
      count: 1,
      saving: 3.5327788225083183
    },
    obsolete_snapshot_chains: {
      count: 0,
      saving: 0
    },
    obsolete_snapshots: {
      count: 41,
      saving: 49.63374663390001
    },
    reserved_instances: {
      count: 4,
      saving: 5.543999999999997
    },
    rightsizing_instances: {
      count: 0,
      saving: 0
    },
    rightsizing_rds: {
      count: 0,
      saving: 0
    },
    s3_abandoned_buckets: {
      count: 45,
      saving: 14.76982733014286
    },
    s3_public_buckets: {
      count: 1,
      options: {
        excluded_pools: {},
        skip_cloud_accounts: []
      },
      items: [
        {
          cloud_resource_id: "ds-report-bucket",
          resource_name: "ds-report-bucket",
          resource_id: "e6e8f75e-77cf-43f3-9b4b-7b935fcbd6d9",
          cloud_account_id: "5b6267b0-b174-4572-aa5e-6e540ed208c1",
          cloud_type: "aws_cnr",
          region: "eu-central-1",
          owner: {
            id: "257fbe7c-03c9-46aa-b3e7-e3b84bd6e850",
            name: "Max Bozhenko"
          },
          pool: {
            id: "c288ecdf-db08-4b36-ab1c-9e6e4ddf42e2",
            name: "Hystax",
            purpose: "business_unit"
          },
          is_excluded: false,
          is_public_policy: true,
          is_public_acls: true,
          detected_at: 1670921449,
          cloud_account_name: "AWS Main"
        }
      ],
      limit: 2
    },
    short_living_instances: {
      count: 5,
      saving: 0.023013319104
    },
    volumes_not_attached_for_a_long_time: {
      count: 9,
      saving: 40.87576648865805
    }
  },
  dismissed_optimizations: {
    instance_migration: {
      count: 2,
      saving: 2.16
    },
    instances_in_stopped_state_for_a_long_time: {
      count: 1,
      saving: 16.956410849168325
    },
    obsolete_snapshots: {
      count: 1,
      saving: 0.09021674340000002
    },
    reserved_instances: {
      count: 1,
      saving: 2.016
    },
    s3_public_buckets: {
      count: 2
    },
    volumes_not_attached_for_a_long_time: {
      count: 2,
      saving: 2.282386150866583
    }
  },
  excluded_optimizations: {},
  deleted_at: 0,
  id: "7e224af5-5850-4166-a776-604ab5ff16b4",
  created_at: 1601470024,
  organization_id: "2bc0c8ce-67f7-429f-986e-b7677ae2c353",
  last_run: 1680160953,
  next_run: 1680171753,
  last_completed: 1680160953
};
export default mock;
