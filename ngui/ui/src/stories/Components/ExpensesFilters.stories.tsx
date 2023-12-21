import ExpensesFilters from "components/ExpensesFilters";
import { getPoolIdWithSubPools } from "urls";
import {
  RESOURCE_TYPE_FILTER,
  POOL_ID_FILTER,
  REGION_FILTER,
  OWNER_ID_FILTER,
  ACTIVE_FILTER,
  AVAILABLE_SAVINGS_FILTER,
  CONSTRAINT_VIOLATED_FILTER,
  SERVICE_NAME_FILTER,
  CLOUD_ACCOUNT_ID_FILTER
} from "utils/constants";

export default {
  component: ExpensesFilters
};

const appliedFilters = {
  [RESOURCE_TYPE_FILTER]: ["Instance"],
  [POOL_ID_FILTER]: [getPoolIdWithSubPools("89dc3640-be3a-46b4-9483-0ef9f1e84bf9")],
  [REGION_FILTER]: ["DE Zone 1"],
  [OWNER_ID_FILTER]: ["c3360014-de43-447c-b105-df4f974baebf"],
  [ACTIVE_FILTER]: [true],
  [AVAILABLE_SAVINGS_FILTER]: [true],
  [CONSTRAINT_VIOLATED_FILTER]: [false],
  [SERVICE_NAME_FILTER]: ["Microsoft.Compute"],
  [CLOUD_ACCOUNT_ID_FILTER]: ["c08d1480-45ca-4237-9dd2-d8ba84b85617"]
};

const filtersFromBE = {
  pool: [
    {
      id: "89dc3640-be3a-46b4-9483-0ef9f1e84bf9",
      name: "Sub",
      purpose: "pool"
    }
  ],
  cloud_account: [
    {
      name: "Azure",
      organization_id: "18696e43-77b0-4167-8500-40947d736cc6",
      type: "azure_cnr",
      id: "c08d1480-45ca-4237-9dd2-d8ba84b85617"
    }
  ],
  owner: [
    {
      name: "EK",
      organization_id: "18696e43-77b0-4167-8500-40947d736cc6",
      id: "c3360014-de43-447c-b105-df4f974baebf"
    }
  ]
};

const expenses = [
  {
    resource_type: "Instance",
    region: "DE Zone 1",
    owner: { name: "EK", id: "c3360014-de43-447c-b105-df4f974baebf" },
    resource_id: "bda4dd0d-b7ab-4c09-b6b7-56ee537cc3cc",
    resource_name: "spottest",
    cloud_account_name: "Azure",
    pool: {
      name: "Sub",
      id: "89dc3640-be3a-46b4-9483-0ef9f1e84bf9",
      purpose: "mlai"
    },
    cloud_account_type: "azure_cnr",
    service_name: "Microsoft.Compute",
    cloud_resource_id:
      "/subscriptions/318bd278-e4ef-4230-9ab4-2ad6a29f578c/resourcegroups/ishtestgroup/providers/microsoft.compute/virtualmachines/spottest",
    cloud_account_id: "c08d1480-45ca-4237-9dd2-d8ba84b85617",
    active: true
  }
];

export const basic = () => (
  <ExpensesFilters
    appliedFilters={appliedFilters}
    filterValues={filtersFromBE}
    expenses={expenses}
    onFilterAdd={() => console.log("onFilterAdd")}
    onFilterDelete={() => console.log("onFilterDelete")}
    onFiltersDelete={() => console.log("onFiltersDelete")}
  />
);
