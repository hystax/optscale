import { useCallback, useEffect } from "react";
import { useDispatch } from "react-redux";
import { RESTAPI, getCleanExpenses } from "api";
import { GET_CLEAN_EXPENSES } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useInScopeOfPageMockup } from "hooks/useInScopeOfPageMockup";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { MOCKED_ORGANIZATION_POOL_ID } from "stories";
import { isError } from "utils/api";
import { START_DATE_FILTER, END_DATE_FILTER } from "utils/constants";
import { mapAvailableFilterKeys } from "./AvailableFiltersService";

const mockedData = {
  clean_expenses: [
    {
      resource_id: "672211a0-d08e-452d-880f-7d815b3c4d48",
      _id: {
        resource_id: "672211a0-d08e-452d-880f-7d815b3c4d48"
      },
      resource_type: "Instance",
      active: false,
      pool: {
        purpose: "business_unit",
        id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
        name: "Engineering"
      },
      region: "eu-central-1",
      owner: {
        id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
        name: "Amy Smith"
      },
      cloud_account_type: "aws_cnr",
      service_name: "AmazonEC2",
      cloud_resource_id: "i-0307c865e6f4f379f",
      cloud_account_id: "8c63e980-6572-4b36-be82-a2bc59705888",
      cloud_account_name: "AWS HQ",
      raw_data_links: 5,
      resource_name: "sunflower-us-east-2",
      cost: 22.5719317827,
      recommendations: {}
    },
    {
      resource_id: "3dd84f76-b16b-48e1-a22b-a6078a1c4ba4",
      _id: {
        resource_id: "3dd84f76-b16b-48e1-a22b-a6078a1c4ba4"
      },
      resource_type: "Instance",
      active: true,
      pool: {
        purpose: "business_unit",
        id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
        name: "Engineering"
      },
      region: "DE Zone 1",
      owner: {
        id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
        name: "Marie Briggs"
      },
      cloud_account_type: "azure_cnr",
      service_name: "Microsoft.Compute",
      cloud_resource_id:
        "/subscriptions/318bd278-e4ef-4230-9ab4-2ad6a29f578c/resourcegroups/ishtestgroup/providers/microsoft.compute/virtualmachines/spottest",
      cloud_account_id: "11fddd0e-3ece-410c-8e68-003abcc44576",
      cloud_account_name: "Azure trial",
      raw_data_links: 3,
      resource_name: "spottest",
      cost: 14.5,
      recommendations: {}
    },
    {
      resource_id: "258804b8-e684-42b9-a148-21795e749168",
      _id: {
        resource_id: "258804b8-e684-42b9-a148-21795e749168"
      },
      resource_type: "Instance",
      active: true,
      pool: {
        purpose: "team",
        id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
        name: "QA"
      },
      region: "eu-central-1",
      owner: {
        id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
        name: "Katy Ali"
      },
      cloud_account_type: "aws_cnr",
      service_name: "AmazonEC2",
      cloud_resource_id: "i-0701429a26d0d574c",
      cloud_account_id: "8c63e980-6572-4b36-be82-a2bc59705888",
      cloud_account_name: "AWS HQ",
      raw_data_links: 15,
      resource_name: "sunflower-us-east-1",
      cost: 28.7082291744,
      recommendations: {}
    },
    {
      resource_id: "c955ea30-349e-4fd1-8764-c766e676fd7a",
      _id: {
        resource_id: "c955ea30-349e-4fd1-8764-c766e676fd7a"
      },
      resource_type: "Instance",
      active: true,
      pool: {
        purpose: "business_unit",
        id: "8ce779dc-cc2a-4210-9770-00a2ce7ccf39",
        name: "Marketing"
      },
      region: "eu-central-1",
      owner: {
        id: "015c36f9-5c05-4da8-b445-932560a00191",
        name: "Sally Wong"
      },
      cloud_account_type: "aws_cnr",
      service_name: "AmazonEC2",
      cloud_resource_id: "i-095a8e515029f5153",
      cloud_account_id: "8c63e980-6572-4b36-be82-a2bc59705888",
      cloud_account_name: "AWS HQ",
      raw_data_links: 5,
      resource_name: "mail-server",
      cost: 24.639862891499998,
      recommendations: {}
    },
    {
      resource_id: "eb9c3b77-d5e6-48f8-b1f5-0a9c7a92e44a",
      _id: {
        resource_id: "eb9c3b77-d5e6-48f8-b1f5-0a9c7a92e44a"
      },
      resource_type: "Instance",
      active: false,
      pool: {
        purpose: "team",
        id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
        name: "Dev"
      },
      region: "eu-central-1",
      owner: {
        id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
        name: "Ella Price"
      },
      cloud_account_type: "aws_cnr",
      service_name: "AmazonEC2",
      cloud_resource_id: "i-041a8aaca5347338a",
      cloud_account_id: "8c63e980-6572-4b36-be82-a2bc59705888",
      cloud_account_name: "AWS HQ",
      raw_data_links: 7,
      resource_name: "jenkins-worker-1",
      cost: 24.6400322778,
      recommendations: {}
    },
    {
      resource_id: "9ec88641-e22a-4720-814c-432d39913ea0",
      _id: {
        resource_id: "9ec88641-e22a-4720-814c-432d39913ea0"
      },
      resource_type: "Instance",
      active: false,
      pool: {
        purpose: "business_unit",
        id: MOCKED_ORGANIZATION_POOL_ID,
        name: "Sunflower corporation"
      },
      region: "eu-central-1",
      owner: {
        id: "87812acf-48f3-47ce-ac7d-0623ae3405ed",
        name: "Taylor Everett"
      },
      cloud_account_type: "aws_cnr",
      service_name: "AmazonEC2",
      cloud_resource_id: "i-0a9ea018c1c3b0c6f",
      cloud_account_id: "8c63e980-6572-4b36-be82-a2bc59705888",
      cloud_account_name: "AWS HQ",
      raw_data_links: 9,
      resource_name: "jenkins-worker-2",
      cost: 24.633812491199997,
      recommendations: {}
    },
    {
      resource_id: "9a7af063-af81-43f8-a98f-27ef86da626a",
      _id: {
        resource_id: "9a7af063-af81-43f8-a98f-27ef86da626a"
      },
      resource_type: "Instance",
      active: false,
      region: "eu-central-1",
      owner: {
        id: "015c36f9-5c05-4da8-b445-932560a00191",
        name: "Sally Wong"
      },
      cloud_account_type: "aws_cnr",
      service_name: "AmazonEC2",
      cloud_resource_id: "i-0ace248dd3fa90d96",
      cloud_account_id: "8c63e980-6572-4b36-be82-a2bc59705888",
      cloud_account_name: "AWS HQ",
      raw_data_links: 1,
      pool: {
        purpose: "team",
        id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
        name: "Dev"
      },
      resource_name: "mail-server-2",
      cost: 0.0341706834,
      recommendations: {}
    }
  ]
};

export const mapCleanExpensesFilterParamsToApiParams = (params) => ({
  start_date: params[START_DATE_FILTER],
  end_date: params[END_DATE_FILTER],
  ...mapAvailableFilterKeys(params)
});

// TODO: could be added to filters definitions
// (but take a note, filter backendKey does not equal to those keys),
// for example cloud_account from available_filters here will become cloud_account_id
// due to different types of data
export const mapCleanExpensesRequestParamsToApiParams = (params) => ({
  ...mapCleanExpensesFilterParamsToApiParams(params),
  limit: params.limit,
  format: params.format
});

export const useGet = ({ params = {} } = {}) => {
  const inScopeOfPageMockup = useInScopeOfPageMockup();

  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();
  const { apiData: data } = useApiData(GET_CLEAN_EXPENSES);

  const { isLoading, shouldInvoke } = useApiState(GET_CLEAN_EXPENSES, {
    organizationId,
    ...mapCleanExpensesRequestParamsToApiParams(params)
  });

  useEffect(() => {
    if (shouldInvoke && !inScopeOfPageMockup) {
      dispatch(getCleanExpenses(organizationId, mapCleanExpensesRequestParamsToApiParams(params)));
    }
  }, [dispatch, organizationId, params, shouldInvoke, inScopeOfPageMockup]);

  return { isLoading, data: inScopeOfPageMockup ? mockedData : data };
};

const useGetOnDemand = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();
  const { apiData: data } = useApiData(GET_CLEAN_EXPENSES);

  const { isLoading } = useApiState(GET_CLEAN_EXPENSES);

  const getData = useCallback(
    (params) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(getCleanExpenses(organizationId, mapCleanExpensesRequestParamsToApiParams(params))).then(() => {
            if (!isError(GET_CLEAN_EXPENSES, getState())) {
              const apiData = getState()?.[RESTAPI]?.[GET_CLEAN_EXPENSES];
              return resolve(apiData);
            }
            return reject();
          });
        });
      }),
    [dispatch, organizationId]
  );

  return { isLoading, data, getData };
};

function CleanExpensesService() {
  return { useGet, useGetOnDemand };
}

export default CleanExpensesService;
