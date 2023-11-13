import { EXPENSES_FILTERBY_TYPES, COST_EXPLORER } from "utils/constants";
import { getLastWeekRange, addDaysToTimestamp } from "utils/datetime";
import ExpensesBreakdown from "../ExpensesBreakdown";

const ExpensesBreakdownForCloudMocked = () => {
  const { lastWeekStart: firstDateRangePoint, lastWeekEnd: lastDateRangePoint } = getLastWeekRange(true);

  const breakdown = {
    [firstDateRangePoint]: [
      {
        id: "8c63e980-6572-4b36-be82-a2bc59705888",
        type: "aws_cnr",
        name: "AWS HQ",
        expense: 4627.2909333465
      },
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "Azure trial",
        expense: 3541.3401215294
      },
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "AWS Marketing",
        expense: 989.3401215294
      },
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "Azure enterprise agreement",
        expense: 780.3401215294
      },
      {
        id: "528e7e01-cf63-4041-980a-fd92a50da65d",
        type: "kubernetes_cnr",
        name: "K8s cluster",
        expense: 540.3401215294
      },
      {
        id: "71ecf26d-ccae-4b0a-81dd-8f0ab56314c8",
        name: "Ali dev",
        type: "alibaba_cnr",
        expense: 26.627527999999998
      }
    ],
    [addDaysToTimestamp(firstDateRangePoint, 1)]: [
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "Azure trial",
        expense: 1950.3397350166
      },
      {
        id: "8c63e980-6572-4b36-be82-a2bc59705888",
        type: "aws_cnr",
        name: "AWS HQ",
        expense: 4172.6371212522
      },
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "AWS Marketing",
        expense: 1230.3401215294
      },
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "Azure enterprise agreement",
        expense: 1009.3401215294
      },
      {
        id: "528e7e01-cf63-4041-980a-fd92a50da65d",
        type: "kubernetes_cnr",
        name: "K8s cluster",
        expense: 230.3401215294
      },
      {
        id: "71ecf26d-ccae-4b0a-81dd-8f0ab56314c8",
        name: "Ali dev",
        type: "alibaba_cnr",
        expense: 26.829112
      }
    ],
    [addDaysToTimestamp(firstDateRangePoint, 2)]: [
      {
        id: "8c63e980-6572-4b36-be82-a2bc59705888",
        type: "aws_cnr",
        name: "AWS HQ",
        expense: 4720.8836990961
      },
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "Azure trial",
        expense: 2031.3381313975
      },
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "AWS Marketing",
        expense: 510.3401215294
      },
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "Azure enterprise agreement",
        expense: 678.3401215294
      },
      {
        id: "528e7e01-cf63-4041-980a-fd92a50da65d",
        type: "kubernetes_cnr",
        name: "K8s cluster",
        expense: 642.3401215294
      },
      {
        id: "71ecf26d-ccae-4b0a-81dd-8f0ab56314c8",
        name: "Ali dev",
        type: "alibaba_cnr",
        expense: 26.825112
      }
    ],
    [addDaysToTimestamp(firstDateRangePoint, 3)]: [
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "Azure trial",
        expense: 920.3376729567
      },
      {
        id: "8c63e980-6572-4b36-be82-a2bc59705888",
        type: "aws_cnr",
        name: "AWS HQ",
        expense: 3344.6967370416
      },
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "AWS Marketing",
        expense: 1441.3401215294
      },
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "Azure enterprise agreement",
        expense: 550.3401215294
      },
      {
        id: "528e7e01-cf63-4041-980a-fd92a50da65d",
        type: "kubernetes_cnr",
        name: "K8s cluster",
        expense: 123.3401215294
      },
      {
        id: "71ecf26d-ccae-4b0a-81dd-8f0ab56314c8",
        name: "Ali dev",
        type: "alibaba_cnr",
        expense: 26.452244
      }
    ],
    [addDaysToTimestamp(firstDateRangePoint, 4)]: [
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "Azure trial",
        expense: 1088.337899628
      },
      {
        id: "8c63e980-6572-4b36-be82-a2bc59705888",
        type: "aws_cnr",
        name: "AWS HQ",
        expense: 3321.0078451299
      },
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "AWS Marketing",
        expense: 996.3401215294
      },
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "Azure enterprise agreement",
        expense: 503.3401215294
      },
      {
        id: "528e7e01-cf63-4041-980a-fd92a50da65d",
        type: "kubernetes_cnr",
        name: "K8s cluster",
        expense: 242.3401215294
      },
      {
        id: "71ecf26d-ccae-4b0a-81dd-8f0ab56314c8",
        name: "Ali dev",
        type: "alibaba_cnr",
        expense: 2.201825
      }
    ],
    [addDaysToTimestamp(firstDateRangePoint, 5)]: [
      {
        id: "8c63e980-6572-4b36-be82-a2bc59705888",
        type: "aws_cnr",
        name: "AWS HQ",
        expense: 3778.0220649843004
      },
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "Azure trial",
        expense: 2801.3387691288
      },
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "AWS Marketing",
        expense: 647.3401215294
      },
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "Azure enterprise agreement",
        expense: 624.3401215294
      },
      {
        id: "528e7e01-cf63-4041-980a-fd92a50da65d",
        type: "kubernetes_cnr",
        name: "K8s cluster",
        expense: 581.3401215294
      },
      {
        id: "71ecf26d-ccae-4b0a-81dd-8f0ab56314c8",
        name: "Ali dev",
        type: "alibaba_cnr",
        expense: 2.192313
      }
    ],
    [lastDateRangePoint]: [
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "Azure trial",
        expense: 454.3387909872
      },
      {
        id: "8c63e980-6572-4b36-be82-a2bc59705888",
        type: "aws_cnr",
        name: "AWS HQ",
        expense: 3743.3238728661
      },
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "AWS Marketing",
        expense: 289.3401215294
      },
      {
        id: "11fddd0e-3ece-410c-8e68-003abcc44576",
        type: "azure_cnr",
        name: "Azure enterprise agreement",
        expense: 190.3401215294
      },
      {
        id: "528e7e01-cf63-4041-980a-fd92a50da65d",
        type: "kubernetes_cnr",
        name: "K8s cluster",
        expense: 154.3401215294
      },
      {
        id: "71ecf26d-ccae-4b0a-81dd-8f0ab56314c8",
        name: "Ali dev",
        type: "alibaba_cnr",
        expense: 3.367908
      }
    ]
  };

  const filteredBreakdown = [
    {
      id: "8c63e980-6572-4b36-be82-a2bc59705888",
      type: "aws_cnr",
      total: 28385.5937818932,
      name: "AWS HQ",
      previous_total: 28159.6970880297
    },
    {
      id: "11fddd0e-3ece-410c-8e68-003abcc44576",
      type: "azure_cnr",
      total: 12785.473881506799,
      name: "Azure trial",
      previous_total: 4.779527628233333
    },
    {
      id: "11fsa5d0e-3ece-410c-8e68-003abcc44576",
      type: "azure_cnr",
      total: 6102.093881506799,
      name: "AWS Marketing",
      previous_total: 4.779527628233333
    },
    {
      id: "11fdd77e-3ece-410c-8e68-003abcc44576",
      type: "azure_cnr",
      total: 4334.183881506799,
      name: "Azure enterprise agreement",
      previous_total: 4.779527628233333
    },
    {
      id: "528e7e01-cf63-4041-980a-fd92a50da65d",
      type: "kubernetes_cnr",
      total: 2514.38085071,
      name: "K8s cluster",
      previous_total: 612.38085071
    },
    {
      id: "71ecf26d-ccae-4b0a-81dd-8f0ab56314c8",
      name: "Ali dev",
      type: "alibaba_cnr",
      total: 56.07,
      previous_total: 0
    }
  ];

  return (
    <ExpensesBreakdown
      filterBy={EXPENSES_FILTERBY_TYPES.CLOUD}
      type={COST_EXPLORER}
      breakdown={breakdown}
      total={54121.71}
      previousTotal={143621.48}
      filteredBreakdown={filteredBreakdown}
      startDateTimestamp={firstDateRangePoint}
      endDateTimestamp={lastDateRangePoint}
      isLoading={false}
      onApply={() => {}}
      updateFilter={() => {}}
      isInScopeOfPageMockup
    />
  );
};

export default ExpensesBreakdownForCloudMocked;
