import React, { useState } from "react";
import {
  RECOMMENDATION_SHORT_LIVING_INSTANCES,
  RECOMMENDATION_VOLUMES_NOT_ATTACHED_FOR_LONG_TIME,
  RECOMMENDATION_INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME,
  RECOMMENDATION_INSTANCE_MIGRATION,
  RECOMMENDATION_OBSOLETE_IMAGES,
  RECOMMENDATION_OBSOLETE_SNAPSHOTS,
  RECOMMENDATION_OBSOLETE_SNAPSHOT_CHAINS,
  RECOMMENDATION_RESERVED_INSTANCES,
  RECOMMENDATION_INSTANCE_SUBSCRIPTION,
  RECOMMENDATION_RIGHTSIZING_INSTANCES,
  RECOMMENDATION_ABANDONED_INSTANCES,
  RECOMMENDATION_INSTANCES_FOR_SHUTDOWN,
  RECOMMENDATION_INACTIVE_USERS,
  RECOMMENDATION_INACTIVE_CONSOLE_USERS,
  RECOMMENDATION_INSECURE_SECURITY_GROUPS,
  RECOMMENDATIONS_TABS,
  RECOMMENDATION_OBSOLETE_IPS,
  RECOMMENDATION_PUBLIC_S3_BUCKETS,
  RECOMMENDATION_INSTANCES_GENERATION_UPGRADE,
  RECOMMENDATION_ABANDONED_S3_BUCKETS,
  RECOMMENDATION_ABANDONED_KINESIS_STREAMS,
  RECOMMENDATION_RIGHTSIZING_RDS_INSTANCES
} from "utils/constants";
import { subMinutes, datetimeToUnix } from "utils/datetime";
import { mockCategorizedRecommendations } from "utils/recommendationCategories";
import { ALL_CATEGORY } from "./constants";
import RelevantRecommendations from "./RelevantRecommendations";

const optimizations = {
  [RECOMMENDATION_ABANDONED_INSTANCES]: {
    count: 32,
    saving: 48656.581632937705
  },
  [RECOMMENDATION_ABANDONED_KINESIS_STREAMS]: {
    count: 1,
    saving: 686.8799999999999
  },
  [RECOMMENDATION_INACTIVE_CONSOLE_USERS]: {
    count: 3
  },
  [RECOMMENDATION_INACTIVE_USERS]: {
    count: 22
  },
  [RECOMMENDATION_INSECURE_SECURITY_GROUPS]: {
    count: 20
  },
  [RECOMMENDATION_INSTANCES_GENERATION_UPGRADE]: {
    count: 5,
    saving: 1240.2000000000003
  },
  [RECOMMENDATION_INSTANCE_MIGRATION]: {
    count: 1,
    saving: 152.63999999999902
  },
  [RECOMMENDATION_INSTANCE_SUBSCRIPTION]: {
    count: 2,
    saving: 886.6016666666667
  },
  [RECOMMENDATION_INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME]: {
    count: 1,
    saving: 266.76096774193553
  },
  [RECOMMENDATION_OBSOLETE_IMAGES]: {
    count: 56,
    saving: 2762.5747444583667
  },
  [RECOMMENDATION_INSTANCES_FOR_SHUTDOWN]: {
    count: 3,
    saving: 101.8
  },
  [RECOMMENDATION_OBSOLETE_IPS]: {
    count: 13,
    saving: 2013.463161290323
  },
  [RECOMMENDATION_OBSOLETE_SNAPSHOT_CHAINS]: {
    count: 2,
    saving: 8.927850000000001
  },
  [RECOMMENDATION_OBSOLETE_SNAPSHOTS]: {
    count: 44,
    saving: 2873.6916930459997
  },
  [RECOMMENDATION_RESERVED_INSTANCES]: {
    count: 9,
    saving: 789.9119999999988
  },
  [RECOMMENDATION_RIGHTSIZING_INSTANCES]: {
    count: 20,
    saving: 35109.31999999999
  },
  [RECOMMENDATION_RIGHTSIZING_RDS_INSTANCES]: {
    count: 1,
    saving: 1217.4099999999999
  },
  [RECOMMENDATION_ABANDONED_S3_BUCKETS]: {
    count: 44,
    saving: 2555.1578474417147
  },
  [RECOMMENDATION_PUBLIC_S3_BUCKETS]: {
    count: 2
  },
  [RECOMMENDATION_SHORT_LIVING_INSTANCES]: {
    count: 12,
    saving: 6.851599624223999
  },
  [RECOMMENDATION_VOLUMES_NOT_ATTACHED_FOR_LONG_TIME]: {
    count: 26,
    saving: 2586.9289236688364,
    options: {
      days_threshold: 1,
      excluded_pools: {},
      skip_cloud_accounts: []
    },
    items: [
      {
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/mgr-demo-stand/providers/microsoft.compute/disks/ad-lily-demo_osdisk_1_262f674ad39f4a37a7a5ba498cf00fe3",
        resource_name: "ad-lily-demo_OsDisk_1_262f674ad39f4a37a7a5ba498cf00fe3",
        resource_id: "5fb5ecc1-5193-43d0-ac6e-43007ccda1a8",
        cloud_account_id: "8c4e1b39-399e-4ede-a87a-134ef872d5a4",
        cloud_account_name: "Dev environment",
        cloud_type: "azure_cnr",
        cost_in_detached_state: 24.423638208000018,
        saving: 333.75313570064503,
        region: "France Central",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1653563904
      },
      {
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/mgr-demo-stand/providers/microsoft.compute/disks/iis-lily-demo_osdisk_1_b4983e400f0b42098b20c155bff2dd2d",
        resource_name: "iis-lily-demo_OsDisk_1_b4983e400f0b42098b20c155bff2dd2d",
        resource_id: "34adb4e4-73e5-44ed-9c5b-7cb6458727bb",
        cloud_account_id: "8c4e1b39-399e-4ede-a87a-134ef872d5a4",
        cloud_account_name: "Dev environment",
        cloud_type: "azure_cnr",
        cost_in_detached_state: 24.423638208000018,
        saving: 333.75313570064503,
        region: "France Central",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1653563904
      },
      {
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchid-engineering/providers/microsoft.compute/disks/orchid-stand",
        resource_name: "orchid-stand",
        resource_id: "76a154d5-4b24-4b26-a50d-856bfdbe94e6",
        cloud_account_id: "8c4e1b39-399e-4ede-a87a-134ef872d5a4",
        cloud_account_name: "Dev environment",
        cloud_type: "azure_cnr",
        cost_in_detached_state: 18.109209600000007,
        saving: 247.70813109677408,
        region: "West US 2",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1653563904
      },
      {
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/mgr-demo-stand/providers/microsoft.compute/disks/ad-lily-demo_0_k626dkpbbiuqc8yrtpo7td",
        resource_name: "AD-lily-DEMO_0_k626dKpBBiuQc8yrTpo7TD",
        resource_id: "20de7ef8-699c-40c8-af04-7b0b9d590995",
        cloud_account_id: "8c4e1b39-399e-4ede-a87a-134ef872d5a4",
        cloud_account_name: "Dev environment",
        cloud_type: "azure_cnr",
        cost_in_detached_state: 6.694199987999998,
        saving: 155.02307476645163,
        region: "Germany West Central",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1653563904
      },
      {
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/mgr-demo-stand/providers/microsoft.compute/disks/iis-lily-demo_0_ajxiwczfx5b5xi3qzh6g9b",
        resource_name: "IIS-lily-DEMO_0_AJXiwCZFx5b5xi3QZH6G9b",
        resource_id: "267c20ea-30c7-43da-b2b3-bd0ebc37b2f0",
        cloud_account_id: "8c4e1b39-399e-4ede-a87a-134ef872d5a4",
        cloud_account_name: "Dev environment",
        cloud_type: "azure_cnr",
        cost_in_detached_state: 2.0087092240000004,
        saving: 152.08798410285715,
        region: "Germany West Central",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1653563904
      },
      {
        cloud_resource_id: "vol-085618f0e6df491b1",
        resource_name: "ubuntu16045_666dffd3-360f-c266-0976-9e4925558f9b",
        resource_id: "cab24734-8161-4573-ada5-5000d576fac0",
        cloud_account_id: "be7eb0cc-0c0a-4079-ab74-e06620621715",
        cloud_account_name: "AWS HQ",
        cloud_type: "aws_cnr",
        cost_in_detached_state: 2.3310990898000026,
        saving: 90.7090260261291,
        region: "eu-north-1",
        is_excluded: false,
        last_seen_in_attached_state: 1650026760,
        detected_at: 1650118142
      },
      {
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/dr-demo-stand/providers/microsoft.compute/disks/mem3_6000c29a-b9b7-0d51-a0d5-de47eb2669ee_j3kfnkoz32ra4mpe5pghxv",
        resource_name: "mem3_6000C29a-b9b7-0d51-a0d5-de47eb2669ee_j3kfNKoz32ra4MPe5pGhXV",
        resource_id: "2e00bc77-ca10-4ca4-9bea-d7e983bfae73",
        cloud_account_id: "8c4e1b39-399e-4ede-a87a-134ef872d5a4",
        cloud_account_name: "Dev environment",
        cloud_type: "azure_cnr",
        cost_in_detached_state: 5.807487488000003,
        saving: 79.48649207806451,
        region: "Germany West Central",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1653563904
      },
      {
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/dr-demo-stand/providers/microsoft.compute/disks/mem2_6000c29d-bd8c-a6e6-37ed-604254f41919_aakpkermfjj8z7vexukurw",
        resource_name: "mem2_6000C29d-bd8c-a6e6-37ed-604254f41919_aAKPKErmFJj8Z7vEXuKurW",
        resource_id: "3f2019b3-54e8-4e1b-b660-d98463627603",
        cloud_account_id: "8c4e1b39-399e-4ede-a87a-134ef872d5a4",
        cloud_account_name: "Dev environment",
        cloud_type: "azure_cnr",
        cost_in_detached_state: 5.807943688000001,
        saving: 79.48158615870969,
        region: "Germany West Central",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1653563904
      },
      {
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/dr-demo-stand/providers/microsoft.compute/disks/mem1_6000c29f-97a1-77bc-1ec8-6864ad366896_j2xvdz7zcgnpz3c9zqhf2r",
        resource_name: "mem1_6000C29f-97a1-77bc-1ec8-6864ad366896_J2XVdZ7zCgNPZ3c9zqHF2R",
        resource_id: "9778ffc3-61f6-4083-8b66-db35e82ab8ed",
        cloud_account_id: "8c4e1b39-399e-4ede-a87a-134ef872d5a4",
        cloud_account_name: "Dev environment",
        cloud_type: "azure_cnr",
        cost_in_detached_state: 5.805931288,
        saving: 79.45344572322581,
        region: "Germany West Central",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1653563904
      },
      {
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/dr-demo-stand/providers/microsoft.compute/disks/rhel_7.6_6000c29b-d0d4-cd40-63e1-802208d5e7ac_orxkfe8hl7syqgvh6rxjnf",
        resource_name: "rhel_7.6_6000C29b-d0d4-cd40-63e1-802208d5e7ac_oRXkfe8hL7sYQGVh6rxjNF",
        resource_id: "62d1a931-1ab7-44b1-9356-e6da7ed2860e",
        cloud_account_id: "8c4e1b39-399e-4ede-a87a-134ef872d5a4",
        cloud_account_name: "Dev environment",
        cloud_type: "azure_cnr",
        cost_in_detached_state: 5.282071920000002,
        saving: 79.28783440064515,
        region: "Germany West Central",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1653563904
      },
      {
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/dr-demo-stand/providers/microsoft.compute/disks/ad_6000c292-eaf8-3cf4-a857-992483057fdf_znnvyxuhoqbft92pfjt9hn",
        resource_name: "AD_6000C292-eaf8-3cf4-a857-992483057fdf_ZNNVyXUHoQBFT92pFjT9hN",
        resource_id: "3b58f0f4-4850-463c-b019-376e0db34a69",
        cloud_account_id: "8c4e1b39-399e-4ede-a87a-134ef872d5a4",
        cloud_account_name: "Dev environment",
        cloud_type: "azure_cnr",
        cost_in_detached_state: 5.282689970000002,
        saving: 79.20593657806451,
        region: "Germany West Central",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1653563904
      },
      {
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/aqa-europe/providers/microsoft.compute/disks/sf-stop-test_osdisk_1_72a411202bad45d69ebe1057f7efa0b9",
        resource_name: "SF-stop-test_OsDisk_1_72a411202bad45d69ebe1057f7efa0b9",
        resource_id: "4be22aea-8cb1-4ea6-81c1-fb17ec90ae7e",
        cloud_account_id: "8c4e1b39-399e-4ede-a87a-134ef872d5a4",
        cloud_account_name: "Dev environment",
        cloud_type: "azure_cnr",
        cost_in_detached_state: 5.792882688000003,
        saving: 79.16071902967748,
        region: "West Europe",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1653563904
      },
      {
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/dr-demo-stand/providers/microsoft.compute/disks/azure_cloud_agent_xnppshfjtvncndwsb3eh8k",
        resource_name: "Azure_cloud_agent_XnppSHFjtvNCNDwsB3Eh8k",
        resource_id: "a040ca06-63a2-4c87-a082-38bbcc45cd93",
        cloud_account_id: "8c4e1b39-399e-4ede-a87a-134ef872d5a4",
        cloud_account_name: "Dev environment",
        cloud_type: "azure_cnr",
        cost_in_detached_state: 3.2182041619999966,
        saving: 79.16071902967748,
        region: "Germany West Central",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1653563904
      },
      {
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/dr-demo-stand/providers/microsoft.compute/disks/iis_6000c29c-908d-4a6c-3228-e1122601f072_cy6yfb7k8cymnb5lcqhuwt",
        resource_name: "IIS_6000C29c-908d-4a6c-3228-e1122601f072_CY6yfb7k8CyMnb5LCQhUwT",
        resource_id: "2f7f2d22-0ff3-4c7f-8526-1f7e916dd318",
        cloud_account_id: "8c4e1b39-399e-4ede-a87a-134ef872d5a4",
        cloud_account_name: "Dev environment",
        cloud_type: "azure_cnr",
        cost_in_detached_state: 5.792882688000003,
        saving: 79.16071902967748,
        region: "Germany West Central",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1653563904
      },
      {
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/mgr-demo-stand/providers/microsoft.compute/disks/azure_cloud_agent_unyzotbyytbvcskvmqdysw",
        resource_name: "Azure_cloud_agent_UNyzotbyyTbvcSkVmqdYsW",
        resource_id: "9b2bf329-6b5e-4e5a-bb75-87cc91afcf05",
        cloud_account_id: "8c4e1b39-399e-4ede-a87a-134ef872d5a4",
        cloud_account_name: "Dev environment",
        cloud_type: "azure_cnr",
        cost_in_detached_state: 5.952952068000002,
        saving: 79.16071902967748,
        region: "Germany West Central",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1653563904
      },
      {
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/mgr-demo-stand/providers/microsoft.compute/disks/azure_cloud_agent_wwhhmbdrsyty3cfdtfccos",
        resource_name: "Azure_cloud_agent_wWHhmBDRSytY3cfDTFcCoS",
        resource_id: "6b5f88bf-35ce-444a-ad26-163f6faa13b2",
        cloud_account_id: "8c4e1b39-399e-4ede-a87a-134ef872d5a4",
        cloud_account_name: "Dev environment",
        cloud_type: "azure_cnr",
        cost_in_detached_state: 5.792882688000003,
        saving: 79.16071902967748,
        region: "Germany West Central",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1653563904
      },
      {
        cloud_resource_id:
          "/subscriptions/318bd278-e4ef-4230-9ab4-2ad6a29f578c/resourcegroups/aqa/providers/microsoft.compute/disks/aqa-unattached-volume",
        resource_name: "aqa-unattached-volume",
        resource_id: "04013fd3-ef0e-4766-b3f1-db2d16c50b2d",
        cloud_account_id: "91585588-a4a5-48fb-b40f-f2a5f0cac45a",
        cloud_account_name: "Azure QA",
        cloud_type: "azure_cnr",
        cost_in_detached_state: 29.003820885567528,
        saving: 77.78424105290327,
        region: "Germany West Central",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1603875758
      },
      {
        cloud_resource_id:
          "/subscriptions/318bd278-e4ef-4230-9ab4-2ad6a29f578c/resourcegroups/aqa/providers/microsoft.compute/disks/sfinvalidsg_osdisk_1_6de99a0637194b3597726c15af5b2bb1",
        resource_name: "SFInvalidSG_OsDisk_1_6de99a0637194b3597726c15af5b2bb1",
        resource_id: "9eeff4db-56c8-411d-830c-7b86b67152e4",
        cloud_account_id: "91585588-a4a5-48fb-b40f-f2a5f0cac45a",
        cloud_account_name: "Azure QA",
        cloud_type: "azure_cnr",
        cost_in_detached_state: 14.312184358305618,
        saving: 77.78424105290327,
        region: "Germany West Central",
        is_excluded: false,
        last_seen_in_attached_state: 1628854663,
        detected_at: 1628942434
      },
      {
        cloud_resource_id: "d-gw8860a9n0yr22gowp3c",
        resource_name: "aqa-unattached-volume",
        resource_id: "2c04644b-c66e-49b9-858a-f9b736ae3ab4",
        cloud_account_id: "14d4eb1d-ec9c-4185-af1e-c07ae7598363",
        cloud_account_name: "Ali dev",
        cloud_type: "alibaba_cnr",
        cost_in_detached_state: 17.584413000000005,
        saving: 76.21741935483874,
        region: "Germany (Frankfurt)",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1653434195
      },
      {
        cloud_resource_id:
          "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/sunflower_env/providers/microsoft.compute/disks/orchid-pypi1",
        resource_name: "orchid-pypi1",
        resource_id: "2f636655-7fa1-4c1d-8e1b-400c0728a529",
        cloud_account_id: "8c4e1b39-399e-4ede-a87a-134ef872d5a4",
        cloud_account_name: "Dev environment",
        cloud_type: "azure_cnr",
        cost_in_detached_state: 0.398426612,
        saving: 70.38870145333334,
        region: "West US 2",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1653563904
      },
      {
        cloud_resource_id:
          "/subscriptions/318bd278-e4ef-4230-9ab4-2ad6a29f578c/resourcegroups/aqa/providers/microsoft.compute/disks/sfstoppingtest_osdisk_1_f4cc708c4b6c4542b46c4e586108bd70",
        resource_name: "SFstoppingTest_OsDisk_1_f4cc708c4b6c4542b46c4e586108bd70",
        resource_id: "e5df979c-f982-4640-8ca0-acff49e65229",
        cloud_account_id: "91585588-a4a5-48fb-b40f-f2a5f0cac45a",
        cloud_account_name: "Azure QA",
        cloud_type: "azure_cnr",
        cost_in_detached_state: 0.087625928,
        saving: 69.66261276,
        region: "Germany West Central",
        is_excluded: false,
        last_seen_in_attached_state: 1653401478,
        detected_at: 1653488195
      },
      {
        cloud_resource_id: "vol-09e3290f6f6b2d3c2",
        resource_name: "aqa-unattached-volume",
        resource_id: "27f995b7-cb13-4427-9801-0b2d2c9d2084",
        cloud_account_id: "be7eb0cc-0c0a-4079-ab74-e06620621715",
        cloud_account_name: "AWS HQ",
        cloud_type: "aws_cnr",
        cost_in_detached_state: 1936.8664026110007,
        saving: 42.686600261129044,
        region: "eu-north-1",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1608962524
      },
      {
        cloud_resource_id: "vol-000156560230fe492",
        resource_name: "am_vol",
        resource_id: "95789f41-47bf-410e-8b86-681ad43c318c",
        cloud_account_id: "be7eb0cc-0c0a-4079-ab74-e06620621715",
        cloud_account_name: "AWS HQ",
        cloud_type: "aws_cnr",
        cost_in_detached_state: 1106.5047349409992,
        saving: 30.2962427899355,
        region: "us-west-2",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1615712614
      },
      {
        cloud_resource_id: "vol-03adcef45af33590b",
        resource_name: "volume_from_snapshot_snap-0d09d24f6d07b0356",
        resource_id: "04d01fce-eb67-4e16-b616-bb3184a108bb",
        cloud_account_id: "be7eb0cc-0c0a-4079-ab74-e06620621715",
        cloud_account_name: "AWS HQ",
        cloud_type: "aws_cnr",
        cost_in_detached_state: 1.9687324232000094,
        saving: 24.236992320870975,
        region: "us-west-2",
        is_excluded: false,
        last_seen_in_attached_state: 1642799318,
        detected_at: 1643101853
      },
      {
        cloud_resource_id: "vol-01b510489d2a9cd00",
        resource_name: "ish-ami-deletion-test-volume",
        resource_id: "2a0450fe-e462-4e52-a396-f11ac415d6ca",
        cloud_account_id: "be7eb0cc-0c0a-4079-ab74-e06620621715",
        cloud_account_name: "AWS HQ",
        cloud_type: "aws_cnr",
        cost_in_detached_state: 269.1415691412999,
        saving: 6.059247571161293,
        region: "us-west-2",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1608994924
      },
      {
        cloud_resource_id: "vol-0d49ba10c451274cb",
        resource_name: "SFTESTVOL",
        resource_id: "ce5eb037-c33b-4402-8a44-e57399f26f4a",
        cloud_account_id: "be7eb0cc-0c0a-4079-ab74-e06620621715",
        cloud_account_name: "AWS HQ",
        cloud_type: "aws_cnr",
        cost_in_detached_state: 159.42316315929997,
        saving: 6.059247571161293,
        region: "us-west-2",
        is_excluded: false,
        last_seen_in_attached_state: 0,
        detected_at: 1623142964
      }
    ],
    limit: 100
  }
};

const getTotalSaving = () => Object.values(optimizations).reduce((sum, { saving = 0 }) => sum + saving, 0);

const RelevantRecommendationsMocked = () => {
  const data = mockCategorizedRecommendations({
    next_run: 1,
    id: "8b304f9d-49c4-469c-9663-737f8eb7f600",
    optimizations,
    dismissed_optimizations: optimizations,
    last_completed: datetimeToUnix(subMinutes(new Date(), 60)),
    deleted_at: 0,
    created_at: 1601290532,
    total_saving: getTotalSaving(),
    last_run: 1611542908,
    organization_id: "2a03382a-a036-4881-b6b5-68c08192cc44"
  });

  const [recommendationCategory, setRecommendationCategory] = useState(ALL_CATEGORY);

  const [selectedTab, setSelectedTab] = useState(RECOMMENDATIONS_TABS.ACTIVE);

  const updateCategoryAndSelectedTab = (newCategory) => {
    setRecommendationCategory(newCategory);
    setSelectedTab(selectedTab);
  };

  return (
    <RelevantRecommendations
      data={data}
      isLoadingProps={{
        isGetRecommendationsLoading: false,
        isTabWrapperReady: true,
        isUpdateRecommendationsLoading: false,
        isGetResourceAllowedActionsLoading: false
      }}
      handleAccordionsChange={() => console.log("handleAccordionsChange")}
      downloadRecommendation={() => console.log("download")}
      downloadCleanupScript={() => console.log("downloadCleanupScript")}
      expanded={{
        [RECOMMENDATION_SHORT_LIVING_INSTANCES]: false,
        [RECOMMENDATION_VOLUMES_NOT_ATTACHED_FOR_LONG_TIME]: true,
        [RECOMMENDATION_INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME]: false,
        [RECOMMENDATION_INSTANCE_MIGRATION]: false,
        [RECOMMENDATION_INACTIVE_USERS]: false,
        [RECOMMENDATION_INACTIVE_CONSOLE_USERS]: false,
        [RECOMMENDATION_OBSOLETE_IMAGES]: false,
        [RECOMMENDATION_OBSOLETE_SNAPSHOTS]: false,
        [RECOMMENDATION_OBSOLETE_SNAPSHOT_CHAINS]: false,
        [RECOMMENDATION_INSECURE_SECURITY_GROUPS]: false,
        [RECOMMENDATION_RESERVED_INSTANCES]: false,
        [RECOMMENDATION_OBSOLETE_IPS]: false,
        [RECOMMENDATION_INSTANCE_SUBSCRIPTION]: false,
        [RECOMMENDATION_PUBLIC_S3_BUCKETS]: false,
        [RECOMMENDATION_INSTANCES_GENERATION_UPGRADE]: false
      }}
      selectedTab={selectedTab}
      handleTabChange={() => console.log("handleTabChange")}
      patchResource={() => console.log("patchResource")}
      categorizedRecommendations={data.categorizedRecommendations}
      categoriesSizes={data.categoriesSizes}
      recommendationCategory={recommendationCategory}
      updateCategoryAndSelectedTab={updateCategoryAndSelectedTab}
    />
  );
};

export default RelevantRecommendationsMocked;
