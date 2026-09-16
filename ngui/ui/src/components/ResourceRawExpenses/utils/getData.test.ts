import { getData } from "./getData";

const azureExpense = (overrides = {}) => ({
  cost: 10,
  start_date: "2024-01-01T12:00:00Z",
  kind: "modern",
  usage_quantity: 100,
  meter_details: {
    meter_name: "GPT-4 8K Tokens",
    unit: "1K",
  },
  ...overrides,
});

describe("getData — Azure", () => {
  it("groups Azure expenses by meter_details.meter_name", () => {
    const expenses = [
      azureExpense({ meter_details: { meter_name: "Meter A", unit: "1K" } }),
      azureExpense({ meter_details: { meter_name: "Meter B", unit: "Hours" } }),
    ];

    const { tableData } = getData(expenses);

    expect(tableData.map(({ category }) => category).sort()).toEqual(["Meter A", "Meter B"]);
  });

  it("sums usage_quantity per meter and exposes meter_details.unit prefixed with '* '", () => {
    const expenses = [
      azureExpense({ cost: 5, usage_quantity: 100, meter_details: { meter_name: "GPT-4 Tokens", unit: "1K" } }),
      azureExpense({ cost: 7, usage_quantity: 250, meter_details: { meter_name: "GPT-4 Tokens", unit: "1K" } }),
    ];

    const { tableData } = getData(expenses);

    expect(tableData).toEqual([{ category: "GPT-4 Tokens", expenses: 12, usage: 350, usageUnit: "* 1K" }]);
  });

  it("prefixes any meter_details.unit with '* ', not only magnitude units like '1K'/'1M'", () => {
    const expenses = [azureExpense({ cost: 5, usage_quantity: 20, meter_details: { meter_name: "Meter A", unit: "Hours" } })];

    const { tableData } = getData(expenses);

    expect(tableData).toEqual([{ category: "Meter A", expenses: 5, usage: 20, usageUnit: "* Hours" }]);
  });

  it("aggregates different meters independently", () => {
    const expenses = [
      azureExpense({ cost: 5, usage_quantity: 100, meter_details: { meter_name: "Meter A", unit: "1K" } }),
      azureExpense({ cost: 3, usage_quantity: 20, meter_details: { meter_name: "Meter B", unit: "Hours" } }),
    ];

    const { tableData } = getData(expenses);

    expect(tableData.slice().sort((a, b) => a.category.localeCompare(b.category))).toEqual([
      { category: "Meter A", expenses: 5, usage: 100, usageUnit: "* 1K" },
      { category: "Meter B", expenses: 3, usage: 20, usageUnit: "* Hours" },
    ]);
  });

  it("aggregates usage and expense across multiple dates for the same meter, in both table and chart data", () => {
    const expenses = [
      azureExpense({
        cost: 5,
        usage_quantity: 100,
        start_date: "2024-01-01T12:00:00Z",
        meter_details: { meter_name: "Meter A", unit: "1K" },
      }),
      azureExpense({
        cost: 5,
        usage_quantity: 50,
        start_date: "2024-01-02T12:00:00Z",
        meter_details: { meter_name: "Meter A", unit: "1K" },
      }),
    ];

    const { tableData, chartData } = getData(expenses);

    expect(tableData).toEqual([{ category: "Meter A", expenses: 10, usage: 150, usageUnit: "* 1K" }]);
    expect(chartData).toHaveLength(1);
    expect(chartData[0].id).toBe("Meter A");
    expect(chartData[0].data).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ y: 5, usage: 100, usageUnit: "* 1K" }),
        expect.objectContaining({ y: 5, usage: 50, usageUnit: "* 1K" }),
      ])
    );
  });

  it("still counts expense but skips usage for records missing usage_quantity", () => {
    const expenses = [
      azureExpense({ cost: 5, usage_quantity: 100, meter_details: { meter_name: "Meter A", unit: "1K" } }),
      azureExpense({ cost: 3, usage_quantity: undefined, meter_details: { meter_name: "Meter A", unit: "1K" } }),
    ];

    const { tableData } = getData(expenses);

    expect(tableData).toEqual([{ category: "Meter A", expenses: 8, usage: 100, usageUnit: "* 1K" }]);
  });

  it("still counts expense but skips usage for records missing meter_details.unit", () => {
    const expenses = [
      azureExpense({ cost: 5, usage_quantity: 100, meter_details: { meter_name: "Meter A", unit: "1K" } }),
      azureExpense({ cost: 3, usage_quantity: 20, meter_details: { meter_name: "Meter A", unit: undefined } }),
    ];

    const { tableData } = getData(expenses);

    expect(tableData).toEqual([{ category: "Meter A", expenses: 8, usage: 100, usageUnit: "* 1K" }]);
  });

  it("still counts expense but skips usage for records whose usage_quantity is null", () => {
    const expenses = [
      azureExpense({ cost: 5, usage_quantity: 100, meter_details: { meter_name: "Meter A", unit: "1K" } }),
      azureExpense({ cost: 3, usage_quantity: null, meter_details: { meter_name: "Meter A", unit: "1K" } }),
    ];

    const { tableData } = getData(expenses);

    expect(tableData).toEqual([{ category: "Meter A", expenses: 8, usage: 100, usageUnit: "* 1K" }]);
  });

  it("still counts expense but skips usage for records whose usage_quantity is false", () => {
    const expenses = [
      azureExpense({ cost: 5, usage_quantity: 100, meter_details: { meter_name: "Meter A", unit: "1K" } }),
      azureExpense({ cost: 3, usage_quantity: false, meter_details: { meter_name: "Meter A", unit: "1K" } }),
    ];

    const { tableData } = getData(expenses);

    expect(tableData).toEqual([{ category: "Meter A", expenses: 8, usage: 100, usageUnit: "* 1K" }]);
  });

  it("still counts expense but skips usage for records whose usage_quantity is an empty or blank string", () => {
    const expenses = [
      azureExpense({ cost: 5, usage_quantity: 100, meter_details: { meter_name: "Meter A", unit: "1K" } }),
      azureExpense({ cost: 3, usage_quantity: "", meter_details: { meter_name: "Meter A", unit: "1K" } }),
      azureExpense({ cost: 2, usage_quantity: "   ", meter_details: { meter_name: "Meter A", unit: "1K" } }),
    ];

    const { tableData } = getData(expenses);

    expect(tableData).toEqual([{ category: "Meter A", expenses: 10, usage: 100, usageUnit: "* 1K" }]);
  });

  it("excludes usage for records whose kind is not 'modern', but keeps the expense", () => {
    const expenses = [
      azureExpense({ cost: 5, usage_quantity: 100, kind: "modern", meter_details: { meter_name: "Meter A", unit: "1K" } }),
      azureExpense({ cost: 4, usage_quantity: 40, kind: "legacy", meter_details: { meter_name: "Meter A", unit: "1K" } }),
    ];

    const { tableData } = getData(expenses);

    expect(tableData).toEqual([{ category: "Meter A", expenses: 9, usage: 100, usageUnit: "* 1K" }]);
  });

  it("excludes usage for records with no kind field at all", () => {
    const expenses = [
      azureExpense({ cost: 5, usage_quantity: 100, meter_details: { meter_name: "Meter A", unit: "1K" } }),
      azureExpense({ cost: 4, usage_quantity: 40, kind: undefined, meter_details: { meter_name: "Meter A", unit: "1K" } }),
    ];

    const { tableData } = getData(expenses);

    expect(tableData).toEqual([{ category: "Meter A", expenses: 9, usage: 100, usageUnit: "* 1K" }]);
  });

  it("omits usage fields entirely when no record in the meter has valid usage data", () => {
    const expenses = [
      azureExpense({ cost: 5, usage_quantity: undefined, meter_details: { meter_name: "Meter A", unit: "1K" } }),
    ];

    const { tableData } = getData(expenses);

    expect(tableData).toEqual([{ category: "Meter A", expenses: 5 }]);
  });
});

describe("getData — other cloud types and fallback (regression)", () => {
  it("keeps AWS grouping/expense totals and now also includes usage in chart points (bug fix)", () => {
    const expenses = [
      {
        "lineItem/LineItemDescription": "EC2 Instance",
        "lineItem/BlendedRate": "0.5",
        "pricing/unit": "Hrs",
        cost: 5,
        start_date: "2024-01-01T12:00:00Z",
      },
    ];

    const { tableData, chartData } = getData(expenses);

    expect(tableData).toEqual([{ category: "EC2 Instance", expenses: 5, usage: 10, usageUnit: "Hrs" }]);
    expect(chartData[0].data[0]).toEqual(expect.objectContaining({ usage: 10, usageUnit: "Hrs" }));
  });

  it("keeps Nebius grouping/expense/usage totals", () => {
    const expenses = [
      { sku_name: "Compute", cost: 5, pricing_quantity: "10", pricing_unit: "Hrs", start_date: "2024-01-01T12:00:00Z" },
    ];

    const { tableData } = getData(expenses);

    expect(tableData).toEqual([{ category: "Compute", expenses: 5, usage: 10, usageUnit: "Hrs" }]);
  });

  it("keeps Alibaba grouping by BillingItem, with no usage column", () => {
    const expenses = [
      { BillingItem: "ECS", cost: 5, start_date: "2024-01-01T12:00:00Z" },
      { BillingItem: "ECS", cost: 3, start_date: "2024-01-02T12:00:00Z" },
    ];

    const { tableData } = getData(expenses);

    expect(tableData).toEqual([{ category: "ECS", expenses: 8 }]);
  });

  it("falls back to a single 'Total expenses' category when cloud type cannot be determined", () => {
    const expenses = [
      { cost: 5, start_date: "2024-01-01T12:00:00Z" },
      { cost: 3, start_date: "2024-01-02T12:00:00Z" },
    ];

    const { tableData } = getData(expenses);

    expect(tableData).toEqual([{ category: "Total expenses", expenses: 8 }]);
  });
});
