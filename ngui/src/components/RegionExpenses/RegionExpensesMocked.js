import React from "react";

import { getStartOfTodayInUTCinSeconds, getEndOfTodayInUTCinSeconds } from "utils/datetime";

import RegionExpenses from "./RegionExpenses";

const RegionExpensesMocked = () => (
  <RegionExpenses
    expenses={{
      regions: [
        {
          name: "China (Hong Kong)",
          id: "cn-hongkong",
          total: 2.066392000000001,
          previous_total: 0,
          longitude: 113.987274,
          latitude: 22.3526629,
          type: "alibaba_cnr"
        },
        {
          name: "Singapore",
          id: "ap-southeast-1",
          total: 0.363,
          previous_total: 0,
          longitude: 103.7038234,
          latitude: 1.3139961,
          type: "alibaba_cnr"
        },
        {
          name: "Indonesia (Jakarta)",
          id: "ap-southeast-5",
          total: 0.6046560000000001,
          previous_total: 0,
          longitude: 106.7593066,
          latitude: -6.2297419,
          type: "alibaba_cnr"
        },
        {
          name: "UAE (Dubai)",
          id: "me-east-1",
          total: 0.6498759999999997,
          previous_total: 0,
          longitude: 55.087321,
          latitude: 25.0759564,
          type: "alibaba_cnr"
        },
        {
          name: "Germany (Frankfurt)",
          id: "eu-central-1",
          total: 199.915492,
          previous_total: 0,
          longitude: 8.5663531,
          latitude: 50.1211908,
          type: "alibaba_cnr"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 35.1796,
          id: "koreasouth",
          longitude: 129.0756,
          total: 0,
          name: "Korea South"
        },
        {
          type: "azure_cnr",
          previous_total: 14.292774253599996,
          latitude: 50.110924,
          id: "germanywestcentral",
          longitude: 8.682127,
          total: 14.749990683655554,
          name: "Germany West Central"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 47.233,
          id: "westus2",
          longitude: -119.852,
          total: 0,
          name: "West US 2"
        },
        {
          type: "azure_cnr",
          previous_total: 12.885124923944446,
          latitude: 40.89,
          id: "westcentralus",
          longitude: -110.234,
          total: 0.000374184,
          name: "West Central US"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: -35.3075,
          id: "australiacentral",
          longitude: 149.1244,
          total: 0,
          name: "Australia Central"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 35.68,
          id: "japaneast",
          longitude: 139.77,
          total: 0,
          name: "Japan East"
        },
        {
          type: "aws_cnr",
          previous_total: 0,
          latitude: 39.90388,
          id: "cn-north-1",
          longitude: 116.3857,
          total: 0,
          name: "cn-north-1"
        },
        {
          type: "aws_cnr",
          previous_total: 189.4569227730001,
          latitude: -33.8,
          id: "ap-southeast-2",
          longitude: 151.2,
          total: 195.77215367999995,
          name: "ap-southeast-2"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 52.3667,
          id: "westeurope",
          longitude: 4.9,
          total: 0,
          name: "West Europe"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 46.817,
          id: "canadaeast",
          longitude: -71.217,
          total: 0,
          name: "Canada East"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 46.3772,
          id: "francecentral",
          longitude: 2.373,
          total: 0,
          name: "France Central"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 53.3478,
          id: "northeurope",
          longitude: -6.2597,
          total: 0,
          name: "North Europe"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 22.267,
          id: "eastasia",
          longitude: 114.188,
          total: 0,
          name: "East Asia"
        },
        {
          type: "aws_cnr",
          previous_total: 539.1341466219,
          latitude: 37.57444,
          id: "ap-northeast-2",
          longitude: 126.99272,
          total: 1280.9649869892003,
          name: "ap-northeast-2"
        },
        {
          type: "aws_cnr",
          previous_total: 0,
          latitude: 31.78395,
          id: "us-gov-west-1",
          longitude: -97.09434,
          total: 0,
          name: "us-gov-west-1"
        },
        {
          type: "aws_cnr",
          previous_total: 1455.5376944838004,
          latitude: 39.96,
          id: "us-east-2",
          longitude: -83,
          total: 1504.055617722001,
          name: "us-east-2"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 59.913868,
          id: "norwayeast",
          longitude: 10.752245,
          total: 0,
          name: "Norway East"
        },
        {
          type: "aws_cnr",
          previous_total: 606.7771461458999,
          latitude: 1.29027,
          id: "ap-southeast-1",
          longitude: 103.851959,
          total: 629.0815152312,
          name: "ap-southeast-1"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 39.916,
          id: "chinanorth2",
          longitude: 116.383,
          total: 0,
          name: "China North 2"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 25.266666,
          id: "uaenorth",
          longitude: 55.316666,
          total: 0,
          name: "UAE North"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 1.283,
          id: "southeastasia",
          longitude: 103.833,
          total: 0,
          name: "Southeast Asia"
        },
        {
          type: "aws_cnr",
          previous_total: 0,
          latitude: 22.25424,
          id: "ap-east-1",
          longitude: 114.13624,
          total: 0,
          name: "ap-east-1"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 37.623159,
          id: "usgovvirginia",
          longitude: -78.39411,
          total: 0,
          name: "US Gov Virginia"
        },
        {
          type: "aws_cnr",
          previous_total: 42158.78813639522,
          latitude: 50.12581,
          id: "eu-central-1",
          longitude: 8.65399,
          total: 58858.9825857804,
          name: "eu-central-1"
        },
        {
          type: "aws_cnr",
          previous_total: 0,
          latitude: 48.85717,
          id: "eu-west-3",
          longitude: 2.34293,
          total: 0,
          name: "eu-west-3"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 43.8345,
          id: "francesouth",
          longitude: 2.1972,
          total: 0,
          name: "France South"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: -35.3075,
          id: "australiacentral2",
          longitude: 149.1244,
          total: 0,
          name: "Australia Central 2"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 37.5665,
          id: "koreacentral",
          longitude: 126.978,
          total: 0,
          name: "Korea Central"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 34.42527,
          id: "usgovarizona",
          longitude: -111.7046,
          total: 0,
          name: "US Gov Arizona"
        },
        {
          type: "aws_cnr",
          previous_total: 0,
          latitude: 45.5,
          id: "ca-central-1",
          longitude: -73.6,
          total: 0,
          name: "ca-central-1"
        },
        {
          type: "aws_cnr",
          previous_total: 1859.3765747099999,
          latitude: 53.35014,
          id: "eu-west-1",
          longitude: -6.266155,
          total: 1929.5802080757005,
          name: "eu-west-1"
        },
        {
          type: "aws_cnr",
          previous_total: 0,
          latitude: 25.9304142,
          id: "me-south-1",
          longitude: 50.6377716,
          total: 0,
          name: "me-south-1"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 24.466667,
          id: "uaecentral",
          longitude: 54.366669,
          total: 0,
          name: "UAE Central"
        },
        {
          type: "aws_cnr",
          previous_total: 580.4425980783001,
          latitude: 51.51768,
          id: "eu-west-2",
          longitude: -0.11362,
          total: 599.7906845478003,
          name: "eu-west-2"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 31.228,
          id: "chinaeast",
          longitude: 121.474,
          total: 0,
          name: "China East"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 36.6681,
          id: "eastus2",
          longitude: -78.3889,
          total: 0,
          name: "East US 2"
        },
        {
          type: "aws_cnr",
          previous_total: 0,
          latitude: 35.41,
          id: "ap-northeast-1",
          longitude: 139.42,
          total: 0,
          name: "ap-northeast-1"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: -23.55,
          id: "brazilsouth",
          longitude: -46.633,
          total: 0,
          name: "Brazil South"
        },
        {
          type: "aws_cnr",
          previous_total: 0,
          latitude: 19.07257,
          id: "ap-south-1",
          longitude: 72.8673,
          total: 0,
          name: "ap-south-1"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 31.228,
          id: "chinaeast2",
          longitude: 121.474,
          total: 0,
          name: "China East 2"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 37.3719,
          id: "eastus",
          longitude: -79.8164,
          total: 0,
          name: "East US"
        },
        {
          type: "aws_cnr",
          previous_total: 0,
          latitude: 37.2931,
          id: "cn-northwest-1",
          longitude: 103.73,
          total: 0,
          name: "cn-northwest-1"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 53.427,
          id: "ukwest",
          longitude: -3.084,
          total: 0,
          name: "UK West"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: -22.90278,
          id: "brazilsoutheast",
          longitude: -43.2075,
          total: 0,
          name: "Brazil Southeast"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 37.783,
          id: "westus",
          longitude: -122.417,
          total: 0,
          name: "West US"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 31.56443,
          id: "usgovtexas",
          longitude: -99.208076,
          total: 0,
          name: "US Gov Texas"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 50.1166,
          id: "germanycentral",
          longitude: 8.6833,
          total: 0,
          name: "Germany Central"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 29.4167,
          id: "southcentralus",
          longitude: -98.5,
          total: 0,
          name: "South Central US"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: -37.8136,
          id: "australiasoutheast",
          longitude: 144.9631,
          total: 0,
          name: "Australia Southeast"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 58.969975,
          id: "norwaywest",
          longitude: 5.733107,
          total: 0,
          name: "Norway West"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: -33.86,
          id: "australiaeast",
          longitude: 151.2094,
          total: 0,
          name: "Australia East"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 42.41475,
          id: "usdodcentral",
          longitude: -92.561731,
          total: 0,
          name: "US DoD Central"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 52.133,
          id: "germanynortheast",
          longitude: 11.616,
          total: 0,
          name: "Germany Northeast"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 43.653,
          id: "canadacentral",
          longitude: -79.383,
          total: 0,
          name: "Canada Central"
        },
        {
          type: "aws_cnr",
          previous_total: 24.918135038099997,
          latitude: 46.15,
          id: "us-west-2",
          longitude: -123.88,
          total: 125.1266180184,
          name: "us-west-2"
        },
        {
          type: "aws_cnr",
          previous_total: 170.4876881868,
          latitude: -23.6815,
          id: "sa-east-1",
          longitude: -46.8754,
          total: 241.25487509700002,
          name: "sa-east-1"
        },
        {
          type: "aws_cnr",
          previous_total: 0,
          latitude: 34.69857,
          id: "ap-northeast-3",
          longitude: 135.50674,
          total: 0,
          name: "ap-northeast-3"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 37.70926,
          id: "usdodeast",
          longitude: -77.84588,
          total: 0,
          name: "US DoD East"
        },
        {
          type: "aws_cnr",
          previous_total: 0,
          latitude: -33.928992,
          id: "af-south-1",
          longitude: 18.417396,
          total: 0,
          name: "af-south-1"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 41.8819,
          id: "northcentralus",
          longitude: -87.6278,
          total: 0,
          name: "North Central US"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: -34.075691,
          id: "southafricawest",
          longitude: 18.843266,
          total: 0,
          name: "South Africa West"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 53.073635,
          id: "germanynorth",
          longitude: 8.806422,
          total: 0,
          name: "Germany North"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 46.204391,
          id: "switzerlandwest",
          longitude: 6.143158,
          total: 0,
          name: "Switzerland West"
        },
        {
          type: "aws_cnr",
          previous_total: 1807.4338896492,
          latitude: 37.35,
          id: "us-west-1",
          longitude: -121.96,
          total: 1879.1553467852998,
          name: "us-west-1"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 50.941,
          id: "uksouth",
          longitude: -0.799,
          total: 0,
          name: "UK South"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 41.5908,
          id: "centralus",
          longitude: -93.6208,
          total: 0,
          name: "Central US"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 12.9822,
          id: "southindia",
          longitude: 80.1636,
          total: 0,
          name: "South India"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 19.088,
          id: "westindia",
          longitude: 72.868,
          total: 0,
          name: "West India"
        },
        {
          type: "aws_cnr",
          previous_total: 0,
          latitude: 59.33097,
          id: "eu-north-1",
          longitude: 18.04856,
          total: 0,
          name: "eu-north-1"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 47.451542,
          id: "switzerlandnorth",
          longitude: 8.564572,
          total: 0,
          name: "Switzerland North"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 39.916,
          id: "chinanorth",
          longitude: 116.383,
          total: 0,
          name: "China North"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: -25.73134,
          id: "southafricanorth",
          longitude: 28.21837,
          total: 0,
          name: "South Africa North"
        },
        {
          type: "aws_cnr",
          previous_total: 34137.2356875306,
          latitude: 38.13,
          id: "us-east-1",
          longitude: -78.45,
          total: 36136.0079320788,
          name: "us-east-1"
        },
        {
          type: "aws_cnr",
          previous_total: 2.6212396203,
          latitude: 45.4668,
          id: "eu-south-1",
          longitude: 9.1905,
          total: 41.293080234899996,
          name: "eu-south-1"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 37.274279,
          id: "usseceast",
          longitude: -78.536422,
          total: 0,
          name: "US Sec East"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 38.316024,
          id: "ussecwest",
          longitude: -122.481734,
          total: 0,
          name: "US Sec West"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 18.5822,
          id: "centralindia",
          longitude: 73.9197,
          total: 0,
          name: "Central India"
        },
        {
          type: "aws_cnr",
          previous_total: 0,
          latitude: 39.9653,
          id: "us-gov-east-1",
          longitude: -83.0235,
          total: 0,
          name: "us-gov-east-1"
        },
        {
          type: "azure_cnr",
          previous_total: 0,
          latitude: 34.6939,
          id: "japanwest",
          longitude: 135.5022,
          total: 0,
          name: "Japan West"
        }
      ],
      total: 103639.415385108,
      previous_total: 83559.3877584106,
      previous_range_start: 1596326400
    }}
    applyFilter={() => console.log("apply")}
    startDateTimestamp={getStartOfTodayInUTCinSeconds()}
    endDateTimestamp={getEndOfTodayInUTCinSeconds()}
    isLoading={false}
  />
);

export default RegionExpensesMocked;
