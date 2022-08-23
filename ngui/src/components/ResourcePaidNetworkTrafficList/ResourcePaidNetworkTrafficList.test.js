import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ResourcePaidNetworkTrafficList, { getTrafficExpensesDataChunks } from "./ResourcePaidNetworkTrafficList";

const formatData = (numbers) => numbers.map((el) => ({ cost: el }));

describe("Should correctly split expenses into chunks", () => {
  it("Both chunks should be empty if there are no expenses", () => {
    const expenses = [];

    const result = getTrafficExpensesDataChunks(expenses);

    expect(result).toEqual({
      expensesChunk1: [],
      expensesChunk2: []
    });
  });
  describe("The top expense is more or equal to the threshold", () => {
    describe("All the costs are more than the threshold", () => {
      it("Should populate the 1st chunk is there is only 1 expense", () => {
        const expenses = formatData([1]);

        const result = getTrafficExpensesDataChunks(expenses);

        expect(result).toEqual({
          expensesChunk1: formatData([1]),
          expensesChunk2: []
        });
      });
      it("Should return top 5 elements in the first chunk and the rest in the second one", () => {
        const expenses = formatData([10, 9, 8, 7, 6, 5, 4, 3, 2, 1]);

        const result = getTrafficExpensesDataChunks(expenses);

        expect(result).toEqual({
          expensesChunk1: formatData([10, 9, 8, 7, 6]),
          expensesChunk2: formatData([5, 4, 3, 2, 1])
        });
      });
      it("The second chunk should be empty", () => {
        const expenses = formatData([10, 9, 8, 7, 5]);

        const result = getTrafficExpensesDataChunks(expenses);

        expect(result).toEqual({
          expensesChunk1: formatData([10, 9, 8, 7, 5]),
          expensesChunk2: formatData([])
        });
      });
    });
    describe("There are elements less than the threshold", () => {
      describe("The costs less than the threshold should be always pushed to the 2nd chunk ", () => {
        it("Case 1", () => {
          const expenses = formatData([10, 9, 8, 3, 2, 1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3]);

          const result = getTrafficExpensesDataChunks(expenses);

          expect(result).toEqual({
            expensesChunk1: formatData([10, 9, 8, 3, 2]),
            expensesChunk2: formatData([1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3])
          });
        });
        it("Case 2", () => {
          const expenses = formatData([1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3]);

          const result = getTrafficExpensesDataChunks(expenses);

          expect(result).toEqual({
            expensesChunk1: formatData([1]),
            expensesChunk2: formatData([0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3])
          });
        });
      });
    });
  });
  describe("The top expense is less than the threshold", () => {
    it("Should populate the 1st chunk is there is only 1 expense", () => {
      const expenses = formatData([0.1]);

      const result = getTrafficExpensesDataChunks(expenses);

      expect(result).toEqual({
        expensesChunk1: formatData([0.1]),
        expensesChunk2: []
      });
    });
    it("The first chunk should only contain the item with top expense", () => {
      const expenses = formatData([0.9, 0.8, 0.7, 0.6, 0.5]);

      const result = getTrafficExpensesDataChunks(expenses);

      expect(result).toEqual({
        expensesChunk1: formatData([0.9]),
        expensesChunk2: formatData([0.8, 0.7, 0.6, 0.5])
      });
    });
  });
});

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ResourcePaidNetworkTrafficList trafficExpenses={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
