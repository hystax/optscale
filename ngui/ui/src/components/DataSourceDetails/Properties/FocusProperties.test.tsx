import { MockedProvider } from "@apollo/client/testing";
import { createRoot, Root } from "react-dom/client";
import { act } from "react-dom/test-utils";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import TestProvider from "tests/TestProvider";
import FocusProperties from "./FocusProperties";

// Tell React that act() is supported in this environment
(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

describe("FocusProperties", () => {
  let container: HTMLDivElement;
  let root: Root;

  beforeEach(() => {
    container = document.createElement("div");
    root = createRoot(container);
  });

  afterEach(() => {
    act(() => root.unmount());
  });

  it("shows that an upload-only data source has no bucket", () => {
    act(() => {
      root.render(
        <MockedProvider>
          <TestProvider>
            <FocusProperties accountId="account-id" createdAt="10/28/2026 10:00 AM UTC" config={{}} />
          </TestProvider>
        </MockedProvider>
      );
    });

    expect(container.textContent).toContain("10/28/2026 10:00 AM UTC");
    expect(container.textContent).toContain("No bucket, reports are uploaded manually");
    expect(container.querySelector('[data-test-id="p_value_bucket_name"]')).toBeNull();
    expect(container.querySelector('[data-test-id="p_value_access"]')).toBeNull();
  });

  it("shows the bucket connection properties", () => {
    act(() => {
      root.render(
        <MockedProvider>
          <TestProvider>
            <FocusProperties
              accountId="account-id"
              createdAt="10/28/2026 10:00 AM UTC"
              config={{
                bucket_name: "focus-exports",
                bucket_prefix: "exports/",
                s3_endpoint: "https://minio.example.com",
                region_name: "eu-west-1",
                file_pattern: ".*\\.parquet$",
              }}
            />
          </TestProvider>
        </MockedProvider>
      );
    });

    expect(container.querySelector('[data-test-id="p_value_bucket_name"]')?.textContent).toBe("focus-exports");
    expect(container.textContent).toContain("https://minio.example.com");
    expect(container.textContent).not.toContain("No bucket, reports are uploaded manually");
    expect(container.querySelector('[data-test-id="p_value_access"]')?.textContent).toBe("Anonymous");
  });

  it("shows the stored access key ID of a bucket accessed with keys", () => {
    act(() => {
      root.render(
        <MockedProvider>
          <TestProvider>
            <FocusProperties
              accountId="account-id"
              createdAt="10/28/2026 10:00 AM UTC"
              config={{ bucket_name: "focus-exports", credentials: { access_key_id: "AKIAEXAMPLE" } }}
            />
          </TestProvider>
        </MockedProvider>
      );
    });

    expect(container.querySelector('[data-test-id="p_value_access"]')?.textContent).toBe("Access keys (AKIAEXAMPLE)");
  });

  it("lists the overridden mapping fields in the order of the editor", () => {
    act(() => {
      root.render(
        <MockedProvider>
          <TestProvider>
            <FocusProperties
              accountId="account-id"
              createdAt="10/28/2026 10:00 AM UTC"
              config={{
                mapping: {
                  service_name: { value: "Azure" },
                  cost: { columns: ["x_Cost"], decimal_separator: "," },
                  resource_id: { columns: ["Id"] },
                },
              }}
            />
          </TestProvider>
        </MockedProvider>
      );
    });

    expect(container.querySelector('[data-test-id="p_value_mapped_fields"]')?.textContent).toBe("Cost, Resource ID, Service");
  });
});
