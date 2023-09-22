import React from "react";
import { PageMockupContextProvider } from "contexts/PageMockupContext";
import S3DuplicateFinder from "./S3DuplicateFinder";

const S3DuplicateFinderMocked = () => (
  <PageMockupContextProvider>
    <S3DuplicateFinder
      geminis={[
        {
          deleted_at: 0,
          id: "6544c42a-af06-461e-8930-cda0e569df10",
          created_at: 1691411466,
          organization_id: "c91c04f6-9a1e-4cfa-be47-50efa6c75ab6",
          last_run: 1691411714,
          last_completed: 1691412040,
          status: "SUCCESS",
          last_error: null,
          filters: {
            cloud_account_id: "1544c42a-af06-461e-8930-cda0e569df10",
            buckets: ["report-bucket", "dev-bucket"],
            min_size: 123
          },
          stats: {
            monthly_savings: 212,
            total_objects: 340,
            duplicated_objects: 210,
            total_size: 212345512,
            duplicates_size: 5422231
          }
        },
        {
          deleted_at: 0,
          id: "6544c42a-af06-461e-8930-cda0e569df10",
          created_at: 1691412700,
          organization_id: "c91c04f6-9a1e-4cfa-be47-50efa6c75ab6",
          last_run: 1691412948,
          last_completed: 1691412274,
          status: "RUNNING",
          last_error: null,
          filters: {
            cloud_account_id: "1544c42a-af06-461e-8930-cda0e569df10",
            buckets: ["report-bucket", "dev-bucket"],
            min_size: 123
          },
          stats: {
            total_objects: 52,
            duplicated_objects: 25,
            total_size: 64265512,
            duplicates_size: 522231
          }
        },
        {
          deleted_at: 0,
          id: "6544c42a-af06-461e-8930-cda0e569df10",
          created_at: 1691414466,
          organization_id: "c91c04f6-9a1e-4cfa-be47-50efa6c75ab6",
          last_run: 1691411714,
          last_completed: 1691412140,
          status: "SUCCESS",
          last_error: null,
          filters: {
            cloud_account_id: "1544c42a-af06-461e-8930-cda0e569df10",
            buckets: ["report-bucket", "dev-bucket"],
            min_size: 123
          },
          stats: {
            monthly_savings: 651,
            total_objects: 522,
            duplicated_objects: 325,
            total_size: 515265512,
            duplicates_size: 62231
          }
        }
      ]}
      isLoading={false}
    />
  </PageMockupContextProvider>
);

export default S3DuplicateFinderMocked;
