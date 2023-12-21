import RawExpensesTable from "components/RawExpensesTable";

const dataSample1 = [
  {
    start_date: "start_date_3",
    end_date: "end_date_3",
    cost: "cost_3",
    "lineItem/LineItemDescription": "lineItem/LineItemDescription_3",
    meter_details: "meter_details_3",
    usage_quantity: "usage_quantity_3",
    column1: "column1",
    column6: "column6"
  }
];

const dataSample2 = [
  {
    start_date: "start_date_2",
    end_date: "end_date_2",
    cost: "cost_2",
    "lineItem/LineItemDescription": "lineItem/LineItemDescription_2",
    "lineItem/BlendedRate": "lineItem/BlendedRate_2",
    column10: "column10",
    column5: "column5",
    column6: "column6",
    column7: "column7",
    column9: "column9"
  }
];

const dataSample3 = [
  {
    start_date: "start_date_3",
    end_date: "end_date_3",
    cost: "cost_3",
    "lineItem/LineItemDescription": "lineItem/LineItemDescription_3",
    meter_details: "meter_details_3",
    usage_quantity: "usage_quantity_3",
    column1: "column1",
    column6: "column6",
    column7: "column7",
    column9: "column9"
  }
];

export default {
  component: RawExpensesTable,
  argTypes: {
    dataSample: {
      name: "Data",
      control: "select",
      options: [dataSample1, dataSample2, dataSample3],
      defaultValue: dataSample1
    }
  }
};

const expenses = [
  {
    start_date: "2020-10-01T15:00:00",
    end_date: "2020-10-01T16:00:00",
    cost: "4.3e-7",
    "lineItem/LineItemDescription": "$0.0043 per 10,000 GET and all other requests",
    "lineItem/BlendedRate": "0.0000004300",
    "bill/BillType": "Anniversary",
    "bill/BillingEntity": "AWS",
    "bill/BillingPeriodEndDate": "2020-07-01T00:00:00Z",
    "bill/BillingPeriodStartDate": "2020-06-01T00:00:00Z",
    "bill/PayerAccountId": "044478323321",
    cloud_account_id: "6252c4b8-7d8a-4242-9e5c-d815a5d9502d",
    "identity/LineItemId": "fgpclitux456yanvekldytgywyfpy3ddimcq73cfqyy6q5bpylqa",
    "identity/TimeInterval": "2020-06-02T00:00:00Z/2020-06-03T00:00:00Z",
    "lineItem/BlendedCost": "0.0000025800",
    "lineItem/CurrencyCode": "USD",
    "lineItem/LegalEntity": "Amazon Web Services, Inc.",
    "lineItem/LineItemType": "Usage",
    "lineItem/Operation": "ReadBucketPolicyStatus",
    "lineItem/ProductCode": "AmazonS3",
    "lineItem/ResourceId": "al-test-67",
    "lineItem/UnblendedCost": "0.0000025800",
    "lineItem/UnblendedRate": "0.0000004300",
    "lineItem/UsageAccountId": "044478323321",
    "lineItem/UsageAmount": "2.0000000000",
    "lineItem/UsageEndDate": "2020-06-02T16:00:00Z",
    "lineItem/UsageStartDate": "2020-06-02T06:00:00Z",
    "lineItem/UsageType": "EUC1-Requests-Tier2",
    "pricing/RateId": "1686353114",
    "pricing/currency": "USD",
    "pricing/publicOnDemandCost": "0.0000008600",
    "pricing/publicOnDemandRate": "0.0000004300",
    "pricing/term": "OnDemand",
    "pricing/unit": "Requests",
    "product/ProductName": "Amazon Simple Storage Service",
    "product/group": "S3-API-Tier2",
    "product/groupDescription": "GET and all other requests",
    "product/location": "EU (Frankfurt)",
    "product/locationType": "AWS Region",
    "product/productFamily": "API Request",
    "product/region": "eu-central-1",
    "product/servicecode": "AmazonS3",
    "product/servicename": "Amazon Simple Storage Service",
    "product/sku": "TUSXZSTYY6YJH244",
    "product/usagetype": "EUC1-Requests-Tier2",
    "reservation/SubscriptionId": "2496477720",
    "resourceTags/aws:reatedBy": "IAMUser:AIDAQUWY5LJ4YFG4CAYVY:al-full-user",
    _id: "5ed6e8f1aef3a6528fb51e8f"
  },
  {
    start_date: "2020-10-01T08:00:00",
    end_date: "2020-10-01T15:00:00",
    cost: "7.06e-8",
    "lineItem/LineItemDescription": "$0.090 per GB - first 10 TB / month data transfer out beyond the global free tier",
    "lineItem/BlendedRate": "0.0899172129",
    "bill/BillType": "Anniversary",
    "bill/BillingEntity": "AWS",
    "bill/BillingPeriodEndDate": "2020-07-01T00:00:00Z",
    "bill/BillingPeriodStartDate": "2020-06-01T00:00:00Z",
    "bill/PayerAccountId": "044478323321",
    cloud_account_id: "6252c4b8-7d8a-4242-9e5c-d815a5d9502d",
    "identity/LineItemId": "fgpclitux456yanvekldytgywyfpy3ddimcq73cfqyy6q5bpylqa",
    "identity/TimeInterval": "2020-06-02T00:00:00Z/2020-06-03T00:00:00Z",
    "lineItem/BlendedCost": "0.0000025800",
    "lineItem/CurrencyCode": "USD",
    "lineItem/LegalEntity": "Amazon Web Services, Inc.",
    "lineItem/LineItemType": "Usage",
    "lineItem/Operation": "ReadBucketPolicyStatus",
    "lineItem/ProductCode": "AmazonS3",
    "lineItem/ResourceId": "al-test-67",
    "lineItem/UnblendedCost": "0.0000025800",
    "lineItem/UnblendedRate": "0.0000004300",
    "lineItem/UsageAccountId": "044478323321",
    "lineItem/UsageAmount": "2.0000000000",
    "lineItem/UsageEndDate": "2020-06-02T16:00:00Z",
    "lineItem/UsageStartDate": "2020-06-02T06:00:00Z",
    "lineItem/UsageType": "EUC1-Requests-Tier2",
    "pricing/RateId": "1686353114",
    "pricing/currency": "USD",
    "pricing/publicOnDemandCost": "0.0000008600",
    "pricing/publicOnDemandRate": "0.0000004300",
    "pricing/term": "OnDemand",
    "pricing/unit": "Requests",
    "product/ProductName": "Amazon Simple Storage Service",
    "product/group": "S3-API-Tier2",
    "product/groupDescription": "GET and all other requests",
    "product/location": "EU (Frankfurt)",
    "product/locationType": "AWS Region",
    "product/productFamily": "API Request",
    "product/region": "eu-central-1",
    "product/servicecode": "AmazonS3",
    "product/servicename": "Amazon Simple Storage Service",
    "product/sku": "TUSXZSTYY6YJH244",
    "product/usagetype": "EUC1-Requests-Tier2",
    "reservation/SubscriptionId": "2496477720",
    "resourceTags/aws:reatedBy": "IAMUser:AIDAQUWY5LJ4YFG4CAYVY:al-full-user",
    _id: "5ed6e8f1aef3a6528fb51e8f"
  },
  {
    start_date: "2020-10-01T07:00:00",
    end_date: "2020-10-01T16:00:00",
    cost: "5e-8",
    "lineItem/LineItemDescription": "USD 0.02 per GB for EUN1-AWS-Out-Bytes in EU (Stockholm)",
    "lineItem/BlendedRate": "0.0200000000",
    "bill/BillType": "Anniversary",
    "bill/BillingEntity": "AWS",
    "bill/BillingPeriodEndDate": "2020-07-01T00:00:00Z",
    "bill/BillingPeriodStartDate": "2020-06-01T00:00:00Z",
    "bill/PayerAccountId": "044478323321",
    cloud_account_id: "6252c4b8-7d8a-4242-9e5c-d815a5d9502d",
    "identity/LineItemId": "fgpclitux456yanvekldytgywyfpy3ddimcq73cfqyy6q5bpylqa",
    "identity/TimeInterval": "2020-06-02T00:00:00Z/2020-06-03T00:00:00Z",
    "lineItem/BlendedCost": "0.0000025800",
    "lineItem/CurrencyCode": "USD",
    "lineItem/LegalEntity": "Amazon Web Services, Inc.",
    "lineItem/LineItemType": "Usage",
    "lineItem/Operation": "ReadBucketPolicyStatus",
    "lineItem/ProductCode": "AmazonS3",
    "lineItem/ResourceId": "al-test-67",
    "lineItem/UnblendedCost": "0.0000025800",
    "lineItem/UnblendedRate": "0.0000004300",
    "lineItem/UsageAccountId": "044478323321",
    "lineItem/UsageAmount": "2.0000000000",
    "lineItem/UsageEndDate": "2020-06-02T16:00:00Z",
    "lineItem/UsageStartDate": "2020-06-02T06:00:00Z",
    "lineItem/UsageType": "EUC1-Requests-Tier2",
    "pricing/RateId": "1686353114",
    "pricing/currency": "USD",
    "pricing/publicOnDemandCost": "0.0000008600",
    "pricing/publicOnDemandRate": "0.0000004300",
    "pricing/term": "OnDemand",
    "pricing/unit": "Requests",
    "product/ProductName": "Amazon Simple Storage Service",
    "product/group": "S3-API-Tier2",
    "product/groupDescription": "GET and all other requests",
    "product/location": "EU (Frankfurt)",
    "product/locationType": "AWS Region",
    "product/productFamily": "API Request",
    "product/region": "eu-central-1",
    "product/servicecode": "AmazonS3",
    "product/servicename": "Amazon Simple Storage Service",
    "product/sku": "TUSXZSTYY6YJH244",
    "product/usagetype": "EUC1-Requests-Tier2",
    "reservation/SubscriptionId": "2496477720",
    "resourceTags/aws:reatedBy": "IAMUser:AIDAQUWY5LJ4YFG4CAYVY:al-full-user",
    _id: "5ed6e8f1aef3a6528fb51e8f"
  }
];

export const basic = () => <RawExpensesTable expenses={expenses} />;

export const isLoading = () => <RawExpensesTable isLoading expenses={[]} />;

const DifferentDataSamples = () => <RawExpensesTable expenses={args.dataSample} />;

export const differentDataSamples = () => <DifferentDataSamples />;
