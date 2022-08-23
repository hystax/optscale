import React from "react";
import { getStartOfTodayInUTCinSeconds, getEndOfTodayInUTCinSeconds } from "utils/datetime";
import TrafficExpenses from "./TrafficExpenses";

const TrafficExpensesMocked = () => (
  <TrafficExpenses
    expenses={{
      traffic_expenses: [
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-north-1",
            latitude: 59.33097,
            longitude: 18.04856
          },
          to: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          usage: 1.1294000000000002,
          cost: 112.497
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          to: {
            name: "eu-west-3",
            latitude: 48.85717,
            longitude: 2.34293
          },
          usage: 2.0061,
          cost: 33.01
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          to: {
            name: "ap-northeast-1",
            latitude: 35.41,
            longitude: 139.42
          },
          usage: 3.0392,
          cost: 116.05
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-north-1",
            latitude: 59.33097,
            longitude: 18.04856
          },
          to: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          usage: 1.1190000000000002,

          cost: 22.0998
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          to: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          usage: 8.222699999999998,
          cost: 131.648
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          to: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          usage: 1.20027,
          cost: 2.696
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          to: {
            name: "me-south-1",
            latitude: 25.9304142,
            longitude: 50.6377716
          },
          usage: 1.9679,
          cost: 3.94
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          to: {
            name: "us-east-2",
            latitude: 39.96,
            longitude: -83
          },
          usage: 0.0013270139000000002,
          cost: 31.39928
        },
        {
          cloud_account_id: "45d15534-d3b6-4505-986a-b0649d056a88",
          cloud_type: "azure_cnr",
          from: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          to: {
            name: "Inter-Region"
          },
          usage: 2.0535662757999993,
          cost: 42.206
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          to: {
            name: "ap-northeast-3",
            latitude: 34.69857,
            longitude: 135.50674
          },
          usage: 3.73,
          cost: 77
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          to: {
            name: "ap-east-1",
            latitude: 22.25424,
            longitude: 114.13624
          },
          usage: 4.01624,
          cost: 88.032
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          to: {
            name: "us-west-2",
            latitude: 46.15,
            longitude: -123.88
          },
          usage: 0.0003650936,
          cost: 8.1584
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          to: {
            name: "ap-east-1",
            latitude: 22.25424,
            longitude: 114.13624
          },
          usage: 1.1190000000000002,
          cost: 21.098
        },
        {
          cloud_account_id: "45d15534-d3b6-4505-986a-b0649d056a88",
          cloud_type: "azure_cnr",
          from: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          to: {
            name: "Inter-Region"
          },
          usage: 0.139540635049342,
          cost: 120.002
        },
        {
          cloud_account_id: "45d15534-d3b6-4505-986a-b0649d056a88",
          cloud_type: "azure_cnr",
          from: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          to: {
            name: "external"
          },
          usage: 1.8,
          cost: 51.002
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          to: {
            name: "sa-east-1",
            latitude: -23.6815,
            longitude: -46.8754
          },
          usage: 6.02714,
          cost: 111.2054
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          to: {
            name: "ap-southeast-2",
            latitude: -33.8,
            longitude: 151.2
          },
          usage: 2.981,
          cost: 25.9
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          to: {
            name: "me-south-1",
            latitude: 25.9304142,
            longitude: 50.6377716
          },
          usage: 3.73,
          cost: 7
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          to: {
            name: "ap-southeast-2",
            latitude: -33.8,
            longitude: 151.2
          },
          usage: 1.9679,
          cost: 3.94
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-north-1",
            latitude: 59.33097,
            longitude: 18.04856
          },
          to: {
            name: "af-south-1",
            latitude: -33.928992,
            longitude: 18.417396
          },
          usage: 21.118,
          cost: 222.2
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          to: {
            name: "ap-south-1",
            latitude: 19.07257,
            longitude: 72.8673
          },
          usage: 0.0001530883,
          cost: 3.0623
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          to: {
            name: "eu-west-3",
            latitude: 48.85717,
            longitude: 2.34293
          },
          usage: 5.221,
          cost: 9.899
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          to: {
            name: "eu-west-2",
            latitude: 51.51768,
            longitude: -0.11362
          },
          usage: 1.4906799999999998,
          cost: 2.982
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-north-1",
            latitude: 59.33097,
            longitude: 18.04856
          },
          to: {
            name: "eu-west-1",
            latitude: 53.35014,
            longitude: -6.266155
          },
          usage: 0.0063017779000000005,
          cost: 0.00013895729999999998
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          to: {
            name: "eu-west-2",
            latitude: 51.51768,
            longitude: -0.11362
          },
          usage: 1.1190000000000002,
          cost: 2.099
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          to: {
            name: "us-west-2",
            latitude: 46.15,
            longitude: -123.88
          },
          usage: 8.348,
          cost: 2.972000000000001
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-north-1",
            latitude: 59.33097,
            longitude: 18.04856
          },
          to: {
            name: "ap-southeast-2",
            latitude: -33.8,
            longitude: 151.2
          },
          usage: 3.726,
          cost: 8.9
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          to: {
            name: "ap-southeast-1",
            latitude: 1.29027,
            longitude: 103.851959
          },
          usage: 0.0005363322,
          cost: 1.0727
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          to: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          usage: 5.693,
          cost: 1.1813999999999998
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-north-1",
            latitude: 59.33097,
            longitude: 18.04856
          },
          to: {
            name: "External"
          },
          usage: 0.01572249689999999,
          cost: 10000
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-north-1",
            latitude: 59.33097,
            longitude: 18.04856
          },
          to: {
            name: "ap-east-1",
            latitude: 22.25424,
            longitude: 114.13624
          },
          usage: 3.73,
          cost: 7
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          to: {
            name: "eu-south-1",
            latitude: 45.4668,
            longitude: 9.1905
          },
          usage: 6.01821,
          cost: 1.2036
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          to: {
            name: "ca-central-1",
            latitude: 45.5,
            longitude: -73.6
          },
          usage: 5.903699999999999,
          cost: 1.182
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          to: {
            name: "ap-northeast-2",
            latitude: 37.57444,
            longitude: 126.99272
          },
          usage: 0.0003330689,
          cost: 8.1388
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          to: {
            name: "eu-west-1",
            latitude: 53.35014,
            longitude: -6.266155
          },
          usage: 0.00040749069999999996,
          cost: 9.586899999999998
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          to: {
            name: "ap-northeast-1",
            latitude: 35.41,
            longitude: 139.42
          },
          usage: 8.198,
          cost: 1.62
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          to: {
            name: "eu-west-1",
            latitude: 53.35014,
            longitude: -6.266155
          },
          usage: 0.0002535975,
          cost: 5.071
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-north-1",
            latitude: 59.33097,
            longitude: 18.04856
          },
          to: {
            name: "us-west-2",
            latitude: 46.15,
            longitude: -123.88
          },
          usage: 7.863300000000001,
          cost: 2.9050000000000007
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          to: {
            name: "ap-southeast-1",
            latitude: 1.29027,
            longitude: 103.851959
          },
          usage: 1.0808,
          cost: 2.119
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          to: {
            name: "us-east-2",
            latitude: 39.96,
            longitude: -83
          },
          usage: 3.206,
          cost: 6.559999999999999
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-north-1",
            latitude: 59.33097,
            longitude: 18.04856
          },
          to: {
            name: "ca-central-1",
            latitude: 45.5,
            longitude: -73.6
          },
          usage: 5.59,
          cost: 1.1
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          to: {
            name: "eu-north-1",
            latitude: 59.33097,
            longitude: 18.04856
          },
          usage: 3.9358,
          cost: 7.88
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-north-1",
            latitude: 59.33097,
            longitude: 18.04856
          },
          to: {
            name: "us-east-2",
            latitude: 39.96,
            longitude: -83
          },
          usage: 2.8326,
          cost: 5.679999999999999
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          to: {
            name: "ca-central-1",
            latitude: 45.5,
            longitude: -73.6
          },
          usage: 1.59554,
          cost: 3.191
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          to: {
            name: "ap-northeast-2",
            latitude: 37.57444,
            longitude: 126.99272
          },
          usage: 4.27319,
          cost: 8.547
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          to: {
            name: "eu-north-1",
            latitude: 59.33097,
            longitude: 18.04856
          },
          usage: 3.73,
          cost: 7
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          to: {
            name: "ap-south-1",
            latitude: 19.07257,
            longitude: 72.8673
          },
          usage: 5.965,
          cost: 1.1499999999999997
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          to: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          usage: 0.0001981443,
          cost: 4.563
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-north-1",
            latitude: 59.33097,
            longitude: 18.04856
          },
          to: {
            name: "eu-west-3",
            latitude: 48.85717,
            longitude: 2.34293
          },
          usage: 2.984,
          cost: 5.6
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          to: {
            name: "af-south-1",
            latitude: -33.928992,
            longitude: 18.417396
          },
          usage: 1.118,
          cost: 2.2
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-north-1",
            latitude: 59.33097,
            longitude: 18.04856
          },
          to: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          usage: 4.099,
          cost: 8.1
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          to: {
            name: "ap-southeast-1",
            latitude: 1.29027,
            longitude: 103.851959
          },
          usage: 1.0839799999999999,
          cost: 2.169
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          to: {
            name: "ap-south-1",
            latitude: 19.07257,
            longitude: 72.8673
          },
          usage: 0.0025480691,
          cost: 5.09621
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          to: {
            name: "External"
          },
          usage: 0.006827894199999999,
          cost: 9000
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          to: {
            name: "eu-west-2",
            latitude: 51.51768,
            longitude: -0.11362
          },
          usage: 1.41096,
          cost: 2.823
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          to: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          usage: 1.492,
          cost: 2.8
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-north-1",
            latitude: 59.33097,
            longitude: 18.04856
          },
          to: {
            name: "sa-east-1",
            latitude: -23.6815,
            longitude: -46.8754
          },
          usage: 2.236,
          cost: 4.4
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          to: {
            name: "sa-east-1",
            latitude: -23.6815,
            longitude: -46.8754
          },
          usage: 1.9679,
          cost: 3.94
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-north-1",
            latitude: 59.33097,
            longitude: 18.04856
          },
          to: {
            name: "ap-southeast-1",
            latitude: 1.29027,
            longitude: 103.851959
          },
          usage: 1.4163000000000003,
          cost: 2.7699
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          to: {
            name: "ap-southeast-2",
            latitude: -33.8,
            longitude: 151.2
          },
          usage: 9.95435,
          cost: 1.9908
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-north-1",
            latitude: 59.33097,
            longitude: 18.04856
          },
          to: {
            name: "eu-west-2",
            latitude: 51.51768,
            longitude: -0.11362
          },
          usage: 2.983,
          cost: 5.7
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          to: {
            name: "eu-west-1",
            latitude: 53.35014,
            longitude: -6.266155
          },
          usage: 0.00036877420000000033,
          cost: 8.5196
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          to: {
            name: "sa-east-1",
            latitude: -23.6815,
            longitude: -46.8754
          },
          usage: 2.609,
          cost: 5.099999999999999
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          to: {
            name: "us-east-2",
            latitude: 39.96,
            longitude: -83
          },
          usage: 2.502,
          cost: 5.008
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          to: {
            name: "ca-central-1",
            latitude: 45.5,
            longitude: -73.6
          },
          usage: 6.336,
          cost: 1.23
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          to: {
            name: "ap-east-1",
            latitude: 22.25424,
            longitude: 114.13624
          },
          usage: 4.1,
          cost: 8
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-north-1",
            latitude: 59.33097,
            longitude: 18.04856
          },
          to: {
            name: "ap-northeast-1",
            latitude: 35.41,
            longitude: 139.42
          },
          usage: 7.825,
          cost: 1.55
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          to: {
            name: "us-west-2",
            latitude: 46.15,
            longitude: -123.88
          },
          usage: 5.328289999999999,
          cost: 1.1611
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "eu-north-1",
            latitude: 59.33097,
            longitude: 18.04856
          },
          to: {
            name: "ap-south-1",
            latitude: 19.07257,
            longitude: 72.8673
          },
          usage: 8.576000000000001,
          cost: 1.63
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          to: {
            name: "eu-west-3",
            latitude: 48.85717,
            longitude: 2.34293
          },
          usage: 1.9679,
          cost: 3.94
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-west-1",
            latitude: 37.35,
            longitude: -121.96
          },
          to: {
            name: "External"
          },
          usage: 0.3401115375,
          cost: 8000
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          to: {
            name: "ap-northeast-1",
            latitude: 35.41,
            longitude: 139.42
          },
          usage: 0.00041692149999999996,
          cost: 8.338
        },
        {
          cloud_account_id: "b757aea5-d5a7-45a3-a88d-576ea9590ad2",
          cloud_type: "aws_cnr",
          from: {
            name: "us-east-1",
            latitude: 38.13,
            longitude: -78.45
          },
          to: {
            name: "eu-central-1",
            latitude: 50.12581,
            longitude: 8.65399
          },
          usage: 0.00012188789999999999,
          cost: 2.4375999999999998
        }
      ],
      start_date: 1640984400,
      end_date: 1652130000,
      total_cost: 285,
      total_usage: 110
    }}
    applyFilter={() => console.log("apply")}
    startDateTimestamp={getStartOfTodayInUTCinSeconds()}
    endDateTimestamp={getEndOfTodayInUTCinSeconds()}
    isLoading={false}
  />
);

export default TrafficExpensesMocked;
