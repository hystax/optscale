import { MockedProvider } from "@apollo/client/testing";
import { createRoot, Root } from "react-dom/client";
import { act } from "react-dom/test-utils";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { ApiMapping } from "components/FocusMappingEditor";
import TestProvider from "tests/TestProvider";
import EditFocusMappingForm from "./EditFocusMappingForm";

// Tell React that act() is supported in this environment
(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

const query = <T extends Element = HTMLElement>(root: Element, selector: string) => {
  const element = root.querySelector<T>(selector);
  if (!element) {
    throw new Error(`Element not found: ${selector}`);
  }
  return element;
};

// A customized field shows its inputs under the header of the card
const isCustom = (field: string) => query(document.body, `[data-test-id="focus_mapping_${field}"]`).children.length > 1;

describe("EditFocusMappingForm", () => {
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

  const renderForm = async ({ mapping, onSubmit = vi.fn() }: { mapping?: ApiMapping | null; onSubmit?: () => void }) => {
    await act(async () => {
      root.render(
        <MockedProvider>
          <TestProvider>
            <EditFocusMappingForm mapping={mapping} onSubmit={onSubmit} onCancel={vi.fn()} />
          </TestProvider>
        </MockedProvider>
      );
    });
  };

  const click = async (selector: string) => {
    await act(async () => {
      query<HTMLButtonElement>(container, selector).click();
    });
  };

  const storedMapping: ApiMapping = {
    cost: { columns: ["x_Cost"], decimal_separator: ",", fallback: { default: true } },
    region: { columns: ["x_SkuRegion"], fallback: { value: "global" } },
  };

  it("shows the stored mapping and the future imports warning", async () => {
    await renderForm({ mapping: storedMapping });

    expect(isCustom("cost")).toBe(true);
    expect(isCustom("region")).toBe(true);
    expect(isCustom("name")).toBe(false);
    expect(container.textContent).toContain("only to future imports");
    expect(container.textContent).toContain("may be counted twice");
  });

  it("does not show the optional field mapping heading of the Connect form", async () => {
    await renderForm({ mapping: storedMapping });

    expect(container.textContent).not.toContain("Field mapping (optional)");
  });

  it("submits the edited mapping only", async () => {
    const onSubmit = vi.fn();
    await renderForm({ mapping: storedMapping, onSubmit });

    await act(async () => {
      query<HTMLButtonElement>(container, '[data-test-id="btn_focus_mapping_region_auto_detect"]').click();
    });
    await click('[data-test-id="btn_save_focus_mapping"]');

    expect(onSubmit).toHaveBeenCalledWith({ cost: storedMapping.cost });
  });

  it("sets every field to default on reset without sending anything", async () => {
    const onSubmit = vi.fn();
    await renderForm({ mapping: storedMapping, onSubmit });

    await click('[data-test-id="btn_reset_focus_mapping"]');

    expect(onSubmit).not.toHaveBeenCalled();
    expect(isCustom("cost")).toBe(false);
    expect(isCustom("region")).toBe(false);
  });

  it("sends a null mapping on save after a reset to defaults", async () => {
    const onSubmit = vi.fn();
    await renderForm({ mapping: storedMapping, onSubmit });

    await click('[data-test-id="btn_reset_focus_mapping"]');
    await click('[data-test-id="btn_save_focus_mapping"]');

    expect(onSubmit).toHaveBeenCalledWith(null);
  });

  it("does not offer a reset when every field is already default", async () => {
    await renderForm({ mapping: storedMapping });

    await click('[data-test-id="btn_reset_focus_mapping"]');

    expect(query<HTMLButtonElement>(container, '[data-test-id="btn_reset_focus_mapping"]').disabled).toBe(true);
  });

  it("does not offer a reset when the mapping is already the default one", async () => {
    await renderForm({ mapping: undefined });

    expect(query<HTMLButtonElement>(container, '[data-test-id="btn_reset_focus_mapping"]').disabled).toBe(true);
  });
});
