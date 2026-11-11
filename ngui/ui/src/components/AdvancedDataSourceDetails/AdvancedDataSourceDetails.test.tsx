import { MockedProvider } from "@apollo/client/testing";
import { createRoot, Root } from "react-dom/client";
import { act } from "react-dom/test-utils";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import TestProvider from "tests/TestProvider";
import AdvancedDataSourceDetails from "./AdvancedDataSourceDetails";

// Tell React that act() is supported in this environment
(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <AdvancedDataSourceDetails
        lastImportAt={0}
        lastImportAttemptAt={0}
        lastImportAttemptError=""
        lastMetricsRetrieval={0}
        lastMetricsRetrievalAttempt={0}
        lastGettingMetricAttemptError={0}
      />
    </TestProvider>
  );
  root.unmount();
});

describe("AdvancedDataSourceDetails monitoring metrics import", () => {
  let container: HTMLDivElement;
  let root: Root;

  beforeEach(() => {
    container = document.createElement("div");
    root = createRoot(container);
  });

  afterEach(() => {
    act(() => root.unmount());
  });

  const render = (props: { withMonitoringMetricsImport?: boolean } = {}) => {
    act(() => {
      root.render(
        <MockedProvider>
          <TestProvider>
            <AdvancedDataSourceDetails
              lastImportAt={0}
              lastImportAttemptAt={0}
              lastImportAttemptError=""
              lastMetricsRetrieval={0}
              lastMetricsRetrievalAttempt={0}
              lastGettingMetricAttemptError=""
              discoveryInfos={[]}
              {...props}
            />
          </TestProvider>
        </MockedProvider>
      );
    });
  };

  it("shows the monitoring metrics import section by default", () => {
    render();

    expect(container.textContent).toContain("Billing import");
    expect(container.textContent).toContain("Monitoring metrics import");
    expect(container.querySelector('[data-test-id="p_last_getting_metrics_at"]')).not.toBeNull();
  });

  it("hides the monitoring metrics import section and keeps the billing import", () => {
    render({ withMonitoringMetricsImport: false });

    expect(container.textContent).toContain("Billing import");
    expect(container.textContent).not.toContain("Monitoring metrics import");
    expect(container.querySelector('[data-test-id="p_last_getting_metrics_at"]')).toBeNull();
    expect(container.querySelector('[data-test-id="p_last_billing_report_processed"]')).not.toBeNull();
  });
});
