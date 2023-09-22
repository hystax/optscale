import React from "react";
import { PageMockupContextProvider } from "contexts/PageMockupContext";
import S3DuplicateFinderCheck from "./S3DuplicateFinderCheck";

const S3DuplicateFinderCheckMocked = () => (
  <PageMockupContextProvider>
    <S3DuplicateFinderCheck
      gemini={{
        deleted_at: 0,
        id: "bc319ede-ee9c-4241-8a1e-60a93e82fae7",
        created_at: 1693814824,
        organization_id: "6e1d27d6-6c4d-42ab-8811-ef767f2fca34",
        last_run: 1693814836,
        last_completed: 1693814839,
        last_error: null,
        status: "SUCCESS",
        filters: {
          cloud_account_id: "04ceaf5d-add6-4945-a72d-1ae425021b40",
          min_size: 0,
          buckets: ["bucket-copy", "bucket-main", "bucket-main-new"]
        },
        stats: {
          total_objects: 703164,
          filtered_objects: 703164,
          total_size: 5373046482003,
          duplicates_size: 296857044997,
          duplicated_objects: 201,
          monthly_savings: 756.276996,
          buckets: {
            "bucket-copy": {
              total_objects: 474,
              filtered_objects: 474,
              size: 9599723245,
              monthly_cost: 0.21185923199999998,
              objects_with_duplicates: 2,
              objects_with_duplicates_size: 4,
              monthly_savings: 23.32
            },
            "bucket-main": {
              total_objects: 79,
              filtered_objects: 79,
              size: 1262938021888,
              monthly_cost: 26.127478212,
              objects_with_duplicates: 0,
              objects_with_duplicates_size: 0,
              monthly_savings: 5.1
            },
            "bucket-main-new": {
              total_objects: 9,
              filtered_objects: 9,
              size: 26476835,
              monthly_cost: 0.013725659999999999,
              objects_with_duplicates: 3,
              objects_with_duplicates_size: 5406007,
              monthly_savings: 31.2
            }
          },
          matrix: {
            "bucket-copy": {
              "bucket-copy": {
                duplicated_objects: 33,
                duplicates_size: 10000381,
                monthly_savings: 32.42
              },
              "bucket-main": {
                duplicated_objects: 12,
                duplicates_size: 52432534827,
                monthly_savings: 12.42
              },
              "bucket-main-new": {
                duplicated_objects: 8,
                duplicates_size: 3734827,
                monthly_savings: 52.22
              }
            },
            "bucket-main": {
              "bucket-main": {
                duplicated_objects: 4,
                duplicates_size: 104857600000,
                monthly_savings: 42.1
              },
              "bucket-copy": {
                duplicated_objects: 12,
                duplicates_size: 52432534827,
                monthly_savings: 12.62
              },
              "bucket-main-new": {
                duplicated_objects: 4,
                duplicates_size: 52428800000,
                monthly_savings: 85.2
              }
            },
            "bucket-main-new": {
              "bucket-main-new": {
                duplicated_objects: 7,
                duplicates_size: 21019006,
                monthly_savings: 42.2
              },
              "bucket-copy": {
                duplicated_objects: 8,
                duplicates_size: 3734827,
                monthly_savings: 64.6
              },
              "bucket-main": {
                duplicated_objects: 4,
                duplicates_size: 52428800000,
                monthly_savings: 72.8
              }
            }
          }
        }
      }}
      isLoading={false}
      thresholds={{
        requiringAttention: 50,
        critical: 200
      }}
    />
  </PageMockupContextProvider>
);

export default S3DuplicateFinderCheckMocked;
