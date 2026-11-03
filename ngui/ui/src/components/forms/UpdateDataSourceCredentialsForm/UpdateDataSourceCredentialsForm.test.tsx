import { MockedProvider } from "@apollo/client/testing";
import { createRoot, Root } from "react-dom/client";
import { act } from "react-dom/test-utils";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import TestProvider from "tests/TestProvider";
import { AWS_CNR, FOCUS } from "utils/constants";
import UpdateDataSourceCredentialsForm from "./UpdateDataSourceCredentialsForm";

// Tell React that act() is supported in this environment
(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <UpdateDataSourceCredentialsForm
        id="id"
        type={AWS_CNR}
        config={{}}
        onSubmit={vi.fn()}
        onCancel={vi.fn()}
        isLoading={false}
      />
    </TestProvider>
  );
  root.unmount();
});

describe("UpdateDataSourceCredentialsForm for a FOCUS data source", () => {
  const bucketConfig = {
    bucket_name: "reports",
    bucket_prefix: "exports/focus/",
    s3_endpoint: "https://minio.example.com",
    region_name: "eu-central-1",
    file_pattern: "\\.parquet$",
    mapping: { resource_id: { columns: ["ResourceId"] } },
  };

  let container: HTMLDivElement;
  let root: Root;

  beforeEach(() => {
    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);
  });

  afterEach(() => {
    act(() => root.unmount());
    container.remove();
  });

  const renderForm = async (config: Record<string, unknown>, onSubmit = vi.fn()) => {
    await act(async () => {
      root.render(
        <MockedProvider>
          <TestProvider>
            <UpdateDataSourceCredentialsForm
              id="focus-id"
              type={FOCUS}
              config={config}
              onSubmit={onSubmit}
              onCancel={vi.fn()}
              isLoading={false}
            />
          </TestProvider>
        </MockedProvider>
      );
    });

    return onSubmit;
  };

  const getInput = (testId: string) => container.querySelector(`[data-test-id="${testId}"]`) as HTMLInputElement | null;

  const clickButton = async (testId: string) => {
    await act(async () => {
      (container.querySelector(`[data-test-id="${testId}"]`) as HTMLButtonElement).click();
    });
  };

  const submit = async () => {
    await act(async () => {
      (container.querySelector('[data-test-id="btn_update_data_source_credentials"]') as HTMLButtonElement).click();
    });
  };

  it("prefills the stored bucket connection with empty keys and shows the anonymous access warning", async () => {
    await renderForm(bucketConfig);

    expect(getInput("input_focus_bucket_name")?.value).toBe("reports");
    expect(getInput("input_focus_bucket_prefix")?.value).toBe("exports/focus/");
    expect(getInput("input_focus_s3_endpoint")?.value).toBe("https://minio.example.com");
    expect(getInput("input_focus_region_name")?.value).toBe("eu-central-1");
    expect(getInput("input_focus_file_pattern")?.value).toBe("\\.parquet$");
    expect(getInput("input_focus_access_key_id")?.value).toBe("");
    expect(getInput("input_focus_secret_access_key")?.value).toBe("");
    expect(container.textContent).toContain("accessed anonymously");
  });

  it("submits the connection config only, without the stored mapping", async () => {
    const onSubmit = await renderForm(bucketConfig);

    await submit();

    expect(onSubmit).toHaveBeenCalledWith("focus-id", {
      config: {
        bucket_name: "reports",
        bucket_prefix: "exports/focus/",
        s3_endpoint: "https://minio.example.com",
        region_name: "eu-central-1",
        file_pattern: "\\.parquet$",
      },
    });
  });

  it("switches a bucket source to manual upload", async () => {
    const onSubmit = await renderForm(bucketConfig);

    await clickButton("btn_focus_manual_upload");

    expect(getInput("input_focus_bucket_name")).toBeNull();
    expect(container.textContent).not.toContain("accessed anonymously");

    await submit();

    const [, params] = onSubmit.mock.calls[0];
    expect(Object.keys(params)).toEqual(["config"]);
    expect(params.config.bucket_name).toBeUndefined();
    expect(params.config.credentials).toBeUndefined();
  });

  it("switches a manual upload source to a bucket", async () => {
    const onSubmit = await renderForm({ mapping: { cost: { columns: ["BilledCost"] } } });

    expect(getInput("input_focus_bucket_name")).toBeNull();

    await clickButton("btn_focus_bucket");

    const bucketNameInput = getInput("input_focus_bucket_name") as HTMLInputElement;
    expect(bucketNameInput.value).toBe("");

    await act(async () => {
      Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set?.call(bucketNameInput, "new-reports");
      bucketNameInput.dispatchEvent(new Event("input", { bubbles: true }));
    });

    await submit();

    expect(onSubmit).toHaveBeenCalledWith("focus-id", { config: { bucket_name: "new-reports" } });
  });
});
