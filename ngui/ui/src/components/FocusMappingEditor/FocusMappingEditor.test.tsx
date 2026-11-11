import { MockedProvider } from "@apollo/client/testing";
import { createRoot, Root } from "react-dom/client";
import { act } from "react-dom/test-utils";
import { FormProvider, useForm } from "react-hook-form";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import TestProvider from "tests/TestProvider";
import FocusMappingEditor from "./FocusMappingEditor";
import { mappingApiToFormValues, mappingFormValuesToApi } from "./mapping";
import type { ApiMapping, FocusMappingFormValues } from "./types";

// Tell React that act() is supported in this environment
(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

type HarnessFormValues = { mapping: FocusMappingFormValues };

// A parent form that keeps the mapping form values in a sub-tree, as the Edit mapping form does
const Harness = ({ mapping, onSubmit }: { mapping: ApiMapping; onSubmit: (mapping: ApiMapping) => void }) => {
  const methods = useForm<HarnessFormValues>({ defaultValues: { mapping: mappingApiToFormValues(mapping) } });

  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit((formData) => onSubmit(mappingFormValuesToApi(formData.mapping)))} noValidate>
        <FocusMappingEditor name="mapping" />
        <button type="submit" data-test-id="btn_submit" />
      </form>
    </FormProvider>
  );
};

describe("FocusMappingEditor", () => {
  let container: HTMLDivElement;
  let root: Root;

  // A customized field shows its inputs under the header of the card
  const isCustom = (field: string) =>
    (container.querySelector(`[data-test-id="focus_mapping_${field}"]`)?.children.length ?? 0) > 1;

  beforeEach(() => {
    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);
  });

  afterEach(() => {
    act(() => root.unmount());
    container.remove();
  });

  it("shows a stored mapping and submits it unchanged", async () => {
    const mapping: ApiMapping = {
      cost: { columns: ["x_Cost"], decimal_separator: ",", fallback: { default: true } },
      region: { columns: ["x_SkuRegion"], fallback: { template: "{x_Zone}", fallback: { value: "global" } } },
    };
    const onSubmit = vi.fn();

    await act(async () => {
      root.render(
        <MockedProvider>
          <TestProvider>
            <Harness mapping={mapping} onSubmit={onSubmit} />
          </TestProvider>
        </MockedProvider>
      );
    });

    expect(isCustom("cost")).toBe(true);
    expect(isCustom("region")).toBe(true);
    expect(isCustom("startDate")).toBe(false);

    await act(async () => {
      container.querySelector<HTMLButtonElement>('[data-test-id="btn_submit"]')?.click();
    });

    expect(onSubmit).toHaveBeenCalledWith(mapping);
  });

  it("does not submit a template without a {Column} placeholder", async () => {
    const onSubmit = vi.fn();

    await act(async () => {
      root.render(
        <MockedProvider>
          <TestProvider>
            <Harness mapping={{ name: { template: "no placeholder" } }} onSubmit={onSubmit} />
          </TestProvider>
        </MockedProvider>
      );
    });

    await act(async () => {
      container.querySelector<HTMLButtonElement>('[data-test-id="btn_submit"]')?.click();
    });

    expect(onSubmit).not.toHaveBeenCalled();
    expect(container.textContent).toContain("The template must contain at least one {Column} placeholder");
  });

  describe("a field with an error", () => {
    const clickMode = async (mode: "auto_detect" | "custom") => {
      await act(async () => {
        container.querySelector<HTMLButtonElement>(`[data-test-id="btn_focus_mapping_name_${mode}"]`)?.click();
      });
    };

    const submitInvalidTemplate = async (onSubmit: (mapping: ApiMapping) => void) => {
      await act(async () => {
        root.render(
          <MockedProvider>
            <TestProvider>
              <Harness mapping={{ name: { template: "no placeholder" } }} onSubmit={onSubmit} />
            </TestProvider>
          </MockedProvider>
        );
      });
      await act(async () => {
        container.querySelector<HTMLButtonElement>('[data-test-id="btn_submit"]')?.click();
      });
    };

    it("loses its error when switched to Auto-detect and lets the form submit", async () => {
      const onSubmit = vi.fn();
      await submitInvalidTemplate(onSubmit);

      await clickMode("auto_detect");

      expect(isCustom("name")).toBe(false);
      expect(container.textContent).not.toContain("The template must contain at least one {Column} placeholder");

      await act(async () => {
        container.querySelector<HTMLButtonElement>('[data-test-id="btn_submit"]')?.click();
      });

      expect(onSubmit).toHaveBeenCalledWith({});
    });

    it("keeps the entered values when switched back to Custom", async () => {
      await submitInvalidTemplate(vi.fn());

      await clickMode("auto_detect");
      await clickMode("custom");

      expect(isCustom("name")).toBe(true);
      expect(container.querySelector<HTMLInputElement>('[data-test-id="input_mapping.name.chain.0.template"]')?.value).toBe(
        "no placeholder"
      );
    });
  });

  describe("field parameters", () => {
    const renderEditor = async (mapping: ApiMapping, onSubmit: (mapping: ApiMapping) => void) => {
      await act(async () => {
        root.render(
          <MockedProvider>
            <TestProvider>
              <Harness mapping={mapping} onSubmit={onSubmit} />
            </TestProvider>
          </MockedProvider>
        );
      });
    };

    const query = (dataTestId: string) => container.querySelector<HTMLElement>(`[data-test-id="${dataTestId}"]`);

    const click = async (dataTestId: string) => {
      const element = query(dataTestId);
      expect(element, dataTestId).not.toBeNull();
      await act(async () => {
        element?.click();
      });
    };

    const submit = () => click("btn_submit");

    it("shows the resource id, resource type and tags parameters and submits them unchanged", async () => {
      const mapping: ApiMapping = {
        resource_id: { columns: ["ResourceId"], normalize: ["strip", "lower"], fallback: { default: true } },
        resource_type: {
          rules: [
            { column: "x_Operation", match: "^RunInstances", type: "Instance" },
            { column: "ResourceType", match: "(?i)snapshot", type: "Snapshot" },
          ],
          columns: ["ServiceName"],
          fallback: { columns: ["ChargeCategory"] },
        },
        tags: { columns: ["x_Labels"], mode: "list" },
      };
      const onSubmit = vi.fn();

      await renderEditor(mapping, onSubmit);

      expect(isCustom("resourceId")).toBe(true);
      expect(isCustom("resourceType")).toBe(true);
      expect(isCustom("tags")).toBe(true);
      expect(query("input_mapping.resourceType.rules.1.match")).not.toBeNull();

      await submit();

      expect(onSubmit).toHaveBeenCalledWith(mapping);
    });

    describe("normalization of the resource id", () => {
      const isChecked = (dataTestId: string) => (query(dataTestId) as HTMLInputElement | null)?.checked;

      it("shows an unset normalization as the default one and keeps it unset", async () => {
        const mapping: ApiMapping = { resource_id: { columns: ["ResourceId"], fallback: { default: true } } };
        const onSubmit = vi.fn();

        await renderEditor(mapping, onSubmit);

        expect(isChecked("checkbox_mapping.resourceId.normalize_default")).toBe(true);
        expect(query("checkbox_mapping.resourceId.normalize_strip")).toBeNull();

        await submit();

        expect(onSubmit).toHaveBeenCalledWith(mapping);
      });

      it("shows no normalization apart from an unset one and keeps it empty", async () => {
        const mapping: ApiMapping = { resource_id: { columns: ["ResourceId"], normalize: [], fallback: { default: true } } };
        const onSubmit = vi.fn();

        await renderEditor(mapping, onSubmit);

        expect(isChecked("checkbox_mapping.resourceId.normalize_default")).toBe(false);
        expect(isChecked("checkbox_mapping.resourceId.normalize_strip")).toBe(false);
        expect(isChecked("checkbox_mapping.resourceId.normalize_lower")).toBe(false);

        await submit();

        expect(onSubmit).toHaveBeenCalledWith(mapping);
      });

      it("sends the chosen normalization", async () => {
        const onSubmit = vi.fn();

        await renderEditor({ resource_id: { columns: ["ResourceId"] } }, onSubmit);
        await click("checkbox_mapping.resourceId.normalize_default");
        await submit();

        expect(onSubmit).toHaveBeenLastCalledWith({ resource_id: { columns: ["ResourceId"], normalize: [] } });

        await click("checkbox_mapping.resourceId.normalize_lower");
        await submit();

        expect(onSubmit).toHaveBeenLastCalledWith({ resource_id: { columns: ["ResourceId"], normalize: ["lower"] } });
      });

      it("returns a chosen normalization to the default one", async () => {
        const onSubmit = vi.fn();

        await renderEditor({ resource_id: { columns: ["ResourceId"], normalize: ["lower"] } }, onSubmit);
        await click("checkbox_mapping.resourceId.normalize_default");
        await submit();

        expect(onSubmit).toHaveBeenCalledWith({ resource_id: { columns: ["ResourceId"] } });
      });
    });

    it("adds, reorders and removes resource type rules", async () => {
      const rules = [
        { column: "A", match: "^a", type: "Instance" },
        { column: "B", match: "^b", type: "Volume" },
        { column: "C", match: "^c", type: "Bucket" },
      ];
      const onSubmit = vi.fn();

      await renderEditor({ resource_type: { columns: ["ServiceName"], rules } }, onSubmit);
      await click("btn_mapping.resourceType.rules.0_move_down");
      await click("btn_mapping.resourceType.rules.2_delete");
      await submit();

      expect(onSubmit).toHaveBeenLastCalledWith({ resource_type: { columns: ["ServiceName"], rules: [rules[1], rules[0]] } });

      // A new rule needs a column, a match and a type
      await click("btn_mapping.resourceType_add_rule");
      await submit();

      expect(onSubmit).toHaveBeenCalledTimes(1);
      expect(query("input_mapping.resourceType.rules.2.column")).not.toBeNull();
    });

    it("does not submit a rule whose regex does not compile", async () => {
      const onSubmit = vi.fn();

      await renderEditor(
        { resource_type: { columns: ["ServiceName"], rules: [{ column: "x_Kind", match: "(?i)(vm", type: "Instance" }] } },
        onSubmit
      );
      await submit();

      expect(onSubmit).not.toHaveBeenCalled();
      expect(container.textContent).toContain("The rule match must be a valid regular expression");
    });

    it("shows the default mapping toggle of the tags only in json mode", async () => {
      await renderEditor({ tags: { columns: ["Tags"] } }, vi.fn());

      expect(query("mapping.tags.useDefaultAtEnd-checkbox")).not.toBeNull();

      await click("radio_mapping.tags.mode_list");

      expect(query("mapping.tags.useDefaultAtEnd-checkbox")).toBeNull();
      expect(query("btn_mapping.tags_add_fallback")).not.toBeNull();
    });

    it("asks only for a prefix in prefixed columns mode and sends no source", async () => {
      const onSubmit = vi.fn();

      await renderEditor({ tags: { columns: ["Tags"], fallback: { default: true } } }, onSubmit);
      await click("radio_mapping.tags.mode_prefixed_columns");

      expect(query("btn_mapping.tags_add_fallback")).toBeNull();
      expect(query("mapping.tags.useDefaultAtEnd-checkbox")).toBeNull();

      // The prefix is required
      await submit();
      expect(onSubmit).not.toHaveBeenCalled();
      expect(query("input_mapping.tags.prefix")).not.toBeNull();
    });

    describe("values the backend accepts", () => {
      const longText = "x".repeat(300);

      it("submits stored long templates, constants and rule columns and matches unchanged", async () => {
        const mapping: ApiMapping = {
          name: { template: `{${longText}}`, fallback: { value: longText } },
          resource_type: {
            rules: [{ column: longText, match: `^${longText}$`, type: "Instance" }],
            columns: ["ServiceName"],
          },
        };
        const onSubmit = vi.fn();

        await renderEditor(mapping, onSubmit);
        await submit();

        expect(onSubmit).toHaveBeenCalledWith(mapping);
      });

      it("submits a stored long tags prefix unchanged", async () => {
        const mapping: ApiMapping = { tags: { mode: "prefixed_columns", prefix: longText } };
        const onSubmit = vi.fn();

        await renderEditor(mapping, onSubmit);
        await submit();

        expect(onSubmit).toHaveBeenCalledWith(mapping);
      });

      it("submits stored empty and blank constants unchanged", async () => {
        const mapping: ApiMapping = {
          region: { columns: ["x_Region"], fallback: { value: "" } },
          name: { value: "  " },
        };
        const onSubmit = vi.fn();

        await renderEditor(mapping, onSubmit);
        await submit();

        expect(onSubmit).toHaveBeenCalledWith(mapping);
      });

      it("does not submit a resource type longer than 255 characters", async () => {
        const onSubmit = vi.fn();

        await renderEditor(
          { resource_type: { columns: ["ServiceName"], rules: [{ column: "x_Kind", match: "^vm", type: "T".repeat(256) }] } },
          onSubmit
        );
        await submit();

        expect(onSubmit).not.toHaveBeenCalled();
        expect(container.textContent).toContain("255");
      });
    });

    it("submits stored prefixed columns tags unchanged", async () => {
      const mapping: ApiMapping = { tags: { mode: "prefixed_columns", prefix: "tag." } };
      const onSubmit = vi.fn();

      await renderEditor(mapping, onSubmit);
      await submit();

      expect(onSubmit).toHaveBeenCalledWith(mapping);
    });
  });
});
