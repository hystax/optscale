import { MockedProvider } from "@apollo/client/testing";
import { createRoot, Root } from "react-dom/client";
import { act } from "react-dom/test-utils";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import TestProvider from "tests/TestProvider";
import { CONNECTION_TYPES, FOCUS } from "utils/constants";
import ConnectCloudAccountForm from "./ConnectCloudAccountForm";

// Tell React that act() is supported in this environment
(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

const setInputValue = (input: HTMLInputElement, value: string) => {
  const valueSetter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
  valueSetter?.call(input, value);
  input.dispatchEvent(new Event("input", { bubbles: true }));
};

const query = <T extends Element = HTMLElement>(root: Element, selector: string) => {
  const element = root.querySelector<T>(selector);
  if (!element) {
    throw new Error(`Element not found: ${selector}`);
  }
  return element;
};

// Types a column name into a columns input and commits it with Enter
const addColumn = async (input: HTMLInputElement, column: string) => {
  await act(async () => {
    input.focus();
    setInputValue(input, column);
  });
  await act(async () => {
    input.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
  });
};

describe("ConnectCloudAccountForm in FOCUS mode", () => {
  let container: HTMLDivElement;
  let root: Root;

  beforeEach(() => {
    window.history.pushState({}, "", `/?type=${CONNECTION_TYPES.FOCUS}`);
    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);
  });

  afterEach(() => {
    act(() => root.unmount());
    container.remove();
    window.history.pushState({}, "", "/");
  });

  it("renders the FOCUS description with the accepted file formats", async () => {
    await act(async () => {
      root.render(
        <MockedProvider>
          <TestProvider>
            <ConnectCloudAccountForm onSubmit={vi.fn()} onCancel={vi.fn()} />
          </TestProvider>
        </MockedProvider>
      );
    });

    expect(container.querySelector('[data-test-id="btn_focus_account"]')).not.toBeNull();
    expect(container.textContent).toContain("Parquet");
    expect(container.textContent).toContain("Field mapping (optional)");
  });

  const renderForm = async (onSubmit = vi.fn()) => {
    await act(async () => {
      root.render(
        <MockedProvider>
          <TestProvider>
            <ConnectCloudAccountForm onSubmit={onSubmit} onCancel={vi.fn()} />
          </TestProvider>
        </MockedProvider>
      );
    });
    await act(async () => {
      setInputValue(query<HTMLInputElement>(container, '[data-test-id="input_cloud_account_name"]'), "My FOCUS exports");
    });
    return onSubmit;
  };

  const submit = async () => {
    await act(async () => {
      query<HTMLButtonElement>(container, '[data-test-id="btn_connect_cloud_account"]').click();
    });
  };

  const overrideField = async (field: string) => {
    await act(async () => {
      query<HTMLButtonElement>(container, `[data-test-id="btn_focus_mapping_${field}_custom"]`).click();
    });
  };

  it("sends an overridden field as the top-level mapping parameter", async () => {
    const onSubmit = await renderForm();

    await overrideField("cost");
    await addColumn(query<HTMLInputElement>(container, '[data-test-id="input_focusMapping.cost.chain.0.columns"]'), "x_Cost");
    await act(async () => {
      query<HTMLInputElement>(container, '[data-test-id="radio_focusMapping.cost.decimalSeparator_comma"]').click();
    });
    await act(async () => {
      query<HTMLInputElement>(container, '[data-test-id="focusMapping.cost.useDefaultAtEnd-checkbox"] input').click();
    });
    await submit();

    expect(onSubmit).toHaveBeenCalledWith({
      name: "My FOCUS exports",
      type: FOCUS,
      config: {},
      mapping: { cost: { columns: ["x_Cost"], decimal_separator: ",", fallback: { default: true } } },
    });
  });

  it("sends fallback steps in the order set by the user", async () => {
    const onSubmit = await renderForm();

    await overrideField("region");
    await addColumn(
      query<HTMLInputElement>(container, '[data-test-id="input_focusMapping.region.chain.0.columns"]'),
      "RegionId"
    );
    await act(async () => {
      query<HTMLButtonElement>(container, '[data-test-id="btn_focusMapping.region_add_fallback"]').click();
    });
    await addColumn(
      query<HTMLInputElement>(container, '[data-test-id="input_focusMapping.region.chain.1.columns"]'),
      "x_SkuRegion"
    );
    await act(async () => {
      query<HTMLButtonElement>(container, '[data-test-id="btn_focusMapping.region.chain.1_move_up"]').click();
    });
    await submit();

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        mapping: { region: { columns: ["x_SkuRegion"], fallback: { columns: ["RegionId"] } } },
      })
    );
  });

  it("does not submit an overridden field without columns", async () => {
    const onSubmit = await renderForm();

    await overrideField("serviceName");
    await submit();

    expect(onSubmit).not.toHaveBeenCalled();
    expect(container.textContent).toContain("Enter at least one column name");
  });

  it("connects an upload-only FOCUS data source with only a name", async () => {
    const onSubmit = vi.fn();

    await act(async () => {
      root.render(
        <MockedProvider>
          <TestProvider>
            <ConnectCloudAccountForm onSubmit={onSubmit} onCancel={vi.fn()} />
          </TestProvider>
        </MockedProvider>
      );
    });

    const nameInput = container.querySelector('[data-test-id="input_cloud_account_name"]') as HTMLInputElement;

    await act(async () => {
      setInputValue(nameInput, "My FOCUS exports");
    });

    await act(async () => {
      (container.querySelector('[data-test-id="btn_connect_cloud_account"]') as HTMLButtonElement).click();
    });

    expect(onSubmit).toHaveBeenCalledWith({
      name: "My FOCUS exports",
      type: FOCUS,
      config: {},
    });
  });

  describe("S3-compatible bucket connection", () => {
    const renderForm = async (onSubmit: () => void) => {
      await act(async () => {
        root.render(
          <MockedProvider>
            <TestProvider>
              <ConnectCloudAccountForm onSubmit={onSubmit} onCancel={vi.fn()} />
            </TestProvider>
          </MockedProvider>
        );
      });
    };

    const getByTestId = <T extends Element>(testId: string) =>
      container.querySelector(`[data-test-id="${testId}"]`) as T | null;

    const fillInput = async (testId: string, value: string) => {
      await act(async () => {
        setInputValue(getByTestId<HTMLInputElement>(testId) as HTMLInputElement, value);
      });
    };

    const selectBucketMode = async () => {
      await act(async () => {
        getByTestId<HTMLButtonElement>("btn_focus_bucket")?.click();
      });
    };

    const submit = async () => {
      await act(async () => {
        getByTestId<HTMLButtonElement>("btn_connect_cloud_account")?.click();
      });
    };

    it("shows bucket fields only in the bucket mode", async () => {
      await renderForm(vi.fn());

      expect(getByTestId("input_focus_bucket_name")).toBeNull();

      await selectBucketMode();

      [
        "input_focus_bucket_name",
        "input_focus_bucket_prefix",
        "input_focus_s3_endpoint",
        "input_focus_region_name",
        "input_focus_access_key_id",
        "input_focus_secret_access_key",
        "input_focus_file_pattern",
      ].forEach((testId) => {
        expect(getByTestId(testId)).not.toBeNull();
      });
    });

    it("connects a bucket with an access key pair", async () => {
      const onSubmit = vi.fn();
      await renderForm(onSubmit);

      await fillInput("input_cloud_account_name", "FOCUS bucket");
      await selectBucketMode();
      await fillInput("input_focus_bucket_name", "reports");
      await fillInput("input_focus_s3_endpoint", "https://minio.example.com");
      await fillInput("input_focus_access_key_id", "AKIAEXAMPLE");
      await fillInput("input_focus_secret_access_key", "secret");
      await submit();

      expect(onSubmit).toHaveBeenCalledWith({
        name: "FOCUS bucket",
        type: FOCUS,
        config: {
          bucket_name: "reports",
          s3_endpoint: "https://minio.example.com",
          credentials: { access_key_id: "AKIAEXAMPLE", secret_access_key: "secret" },
        },
      });
    });

    it("does not submit until the bucket name is set and the inputs are valid", async () => {
      const onSubmit = vi.fn();
      await renderForm(onSubmit);

      await fillInput("input_cloud_account_name", "FOCUS bucket");
      await selectBucketMode();
      await fillInput("input_focus_s3_endpoint", "http://minio.example.com");
      await fillInput("input_focus_access_key_id", "AKIAEXAMPLE");
      await fillInput("input_focus_file_pattern", "focus_(.*");
      await submit();

      expect(onSubmit).not.toHaveBeenCalled();
      expect(container.textContent).toContain("This field is required");
      expect(container.textContent).toContain("The endpoint must start with https://");
      expect(container.textContent).toContain(
        "Enter both the access key ID and the secret access key, or leave both empty for anonymous access"
      );
      expect(container.textContent).toContain("The file name pattern must be a valid regular expression");
    });

    it("connects anonymously after the half-filled key pair is cleared", async () => {
      const onSubmit = vi.fn();
      await renderForm(onSubmit);

      await fillInput("input_cloud_account_name", "Public FOCUS bucket");
      await selectBucketMode();
      await fillInput("input_focus_bucket_name", "public-reports");
      await fillInput("input_focus_secret_access_key", "secret");
      await submit();

      expect(onSubmit).not.toHaveBeenCalled();

      await fillInput("input_focus_secret_access_key", "");

      expect(container.textContent).not.toContain("Enter both the access key ID and the secret access key");

      await submit();

      expect(onSubmit).toHaveBeenCalledWith({
        name: "Public FOCUS bucket",
        type: FOCUS,
        config: { bucket_name: "public-reports" },
      });
    });
  });
});
