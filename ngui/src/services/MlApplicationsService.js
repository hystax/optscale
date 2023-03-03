import { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import {
  getMlApplications,
  createGlobalParameter,
  getMlGlobalParameter,
  getMlGlobalParameters,
  updateGlobalParameter,
  deleteGlobalParameter,
  createMlApplication,
  getMlApplication,
  updateMlApplication,
  deleteMlApplication
} from "api";
import { getMlApplicationRuns, getMlRunDetails, getMlRunDetailsBreakdown } from "api/restapi";
import {
  GET_ML_APPLICATIONS,
  CREATE_GLOBAL_PARAMETER,
  GET_ML_GLOBAL_PARAMETER,
  GET_ML_GLOBAL_PARAMETERS,
  UPDATE_GLOBAL_PARAMETER,
  DELETE_GLOBAL_PARAMETER,
  CREATE_ML_APPLICATION,
  GET_ML_APPLICATION,
  UPDATE_ML_APPLICATION,
  DELETE_ML_APPLICATION,
  GET_ML_APPLICATION_RUNS,
  GET_ML_RUN_DETAILS,
  GET_ML_RUN_DETAILS_BREAKDOWN
} from "api/restapi/actionTypes";
import { getEmptyRecommendationsSet } from "components/MlModelRecommendations/Recommendations";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";
import { millisecondsToSeconds } from "utils/datetime";

const useGetAll = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { applications = [] }
  } = useApiData(GET_ML_APPLICATIONS);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_APPLICATIONS, organizationId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlApplications(organizationId));
    }
  }, [shouldInvoke, dispatch, organizationId]);

  return { isLoading, applications };
};

const useCreateApplication = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_ML_APPLICATION);

  const onCreate = (params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(createMlApplication(organizationId, params)).then(() => {
          if (!isError(CREATE_ML_APPLICATION, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onCreate, isLoading };
};

const useUpdateApplication = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(UPDATE_ML_APPLICATION);

  const onUpdate = (applicationId, params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(updateMlApplication(organizationId, applicationId, params)).then(() => {
          if (!isError(UPDATE_ML_APPLICATION, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onUpdate, isLoading };
};

const useDeleteApplication = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(DELETE_ML_APPLICATION);

  const onDelete = (applicationId) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(deleteMlApplication(organizationId, applicationId)).then(() => {
          if (!isError(DELETE_ML_APPLICATION, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onDelete, isLoading };
};

const useGetOne = (applicationId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData } = useApiData(GET_ML_APPLICATION);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_APPLICATION, { organizationId, applicationId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlApplication(organizationId, applicationId));
    }
  }, [applicationId, dispatch, organizationId, shouldInvoke]);

  return { isLoading, application: apiData };
};

const useGetModelRunsList = (applicationId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading, shouldInvoke } = useApiState(GET_ML_APPLICATION_RUNS, { organizationId, applicationId });

  const {
    apiData: { runs = [] }
  } = useApiData(GET_ML_APPLICATION_RUNS);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlApplicationRuns(organizationId, applicationId));
    }
  }, [applicationId, dispatch, organizationId, shouldInvoke]);

  return { isLoading, runs };
};

const useGetModelRecommendation = () => {
  const [apiData, setApiData] = useState(() => getEmptyRecommendationsSet());

  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const data = {
      cross_region_traffic: {
        count: 3,
        saving: (2545 * 0.09 + 1000 * 0.09 + 1997 * 0.09) * 17,
        items: [
          {
            run: "#1_dazzling_lewin",
            name: "compute-1a24cdq251",
            id: "i-03d05ee0324432171",
            cloud_name: "AWS HQ",
            cloud_type: "aws_cnr",
            compute_location: "eu-west-1",
            data_location: "eu-west-2",
            data_transferred: 2545 * 9 * 100000000,
            estimated_expenses: 2545 * 0.09 * 17,
            last_run: millisecondsToSeconds(+new Date() - 15 * 60 * 1000)
          },
          {
            run: "#2_relaxed_antonelli",
            name: "compute-1a24cdq251",
            id: "i-03d05ee0324432171",
            cloud_name: "AWS HQ",
            cloud_type: "aws_cnr",
            compute_location: "eu-west-1",
            data_location: "eu-west-2",
            data_transferred: 1000 * 9 * 100000000,
            estimated_expenses: 1997 * 0.09 * 17,
            last_run: millisecondsToSeconds(+new Date() - 30 * 60 * 1000)
          },
          {
            run: "#3_strange_bassi",
            name: "compute-1a24cdq251",
            id: "i-03d05ee0324432171",
            cloud_name: "AWS HQ",
            cloud_type: "aws_cnr",
            compute_location: "eu-west-1",
            data_location: "eu-west-2",
            data_transferred: 1997 * 9 * 100000000,
            estimated_expenses: 1000 * 0.09 * 17,
            last_run: millisecondsToSeconds(+new Date() - 45 * 60 * 1000)
          }
        ]
      },
      executors_upgrade: {
        count: 11,
        items: [
          {
            name: "compute-6c99ffb459",
            id: "i-03d05ee0324432171",
            region: "eu-west-1",
            size: "t2.small",
            cloud_name: "AWS HQ",
            cloud_type: "aws_cnr",
            last_used: millisecondsToSeconds(+new Date() - 2 * 24 * 3600 * 1000),
            recommended_size: "t3.small"
          },
          {
            name: "compute-1a24cdq251",
            id: "i-03d05ee0324432414",
            region: "eu-west-1",
            size: "t3.2xlarge",
            cloud_name: "AWS HQ",
            cloud_type: "aws_cnr",
            last_used: millisecondsToSeconds(+new Date() - 2 * 24 * 3600 * 1000),
            recommended_size: "t4.2xlarge"
          },
          {
            name: "compute-5849239483",
            id: "i-03df443b1a8cc888",
            region: "eu-west-1",
            size: "t3.2xlarge",
            cloud_name: "AWS HQ",
            cloud_type: "aws_cnr",
            last_used: millisecondsToSeconds(+new Date() - 5 * 24 * 3600 * 1000),
            recommended_size: "t4.2xlarge"
          },
          {
            name: "compute-491094001",
            id: "i-03d05ee0324434444",
            region: "eu-west-1",
            size: "t3.2xlarge",
            cloud_name: "AWS HQ",
            cloud_type: "aws_cnr",
            last_used: millisecondsToSeconds(+new Date() - 15 * 24 * 3600 * 1000),
            recommended_size: "t4.2xlarge"
          },
          {
            name: "compute-194918885",
            id: "i-03d05eebc7abc7cca77",
            region: "eu-west-1",
            size: "t3.2xlarge",
            cloud_name: "AWS HQ",
            cloud_type: "aws_cnr",
            last_used: millisecondsToSeconds(+new Date() - 1 * 24 * 3600 * 1000),
            recommended_size: "t4.2xlarge"
          },
          {
            name: "compute-4910582010",
            id: "i-cab803d05ee0ab8c8ca",
            region: "eu-west-1",
            size: "t3.2xlarge",
            cloud_name: "AWS HQ",
            cloud_type: "aws_cnr",
            last_used: millisecondsToSeconds(+new Date() - 20 * 24 * 3600 * 1000),
            recommended_size: "t4.2xlarge"
          },
          {
            name: "compute-4819481905",
            id: "i-aedc8a87a00ace6ccc8",
            region: "eu-west-1",
            size: "t3.2xlarge",
            cloud_name: "AWS HQ",
            cloud_type: "aws_cnr",
            last_used: millisecondsToSeconds(+new Date() - 1 * 24 * 3600 * 1000),
            recommended_size: "t4.2xlarge"
          },
          {
            name: "compute-103847104",
            id: "i-97cae97caedcb797e9",
            region: "eu-west-1",
            size: "t3.2xlarge",
            cloud_name: "AWS HQ",
            cloud_type: "aws_cnr",
            last_used: millisecondsToSeconds(+new Date() - 3 * 24 * 3600 * 1000),
            recommended_size: "t4.2xlarge"
          },
          {
            name: "compute-491805727",
            id: "i-bce707eabdc707dbeb",
            region: "eu-west-1",
            size: "t3.2xlarge",
            cloud_name: "AWS HQ",
            cloud_type: "aws_cnr",
            last_used: millisecondsToSeconds(+new Date() - 4 * 24 * 3600 * 1000),
            recommended_size: "t4.2xlarge"
          },
          {
            name: "compute-983285982",
            id: "i-a9ed7c9a7adc777cad",
            region: "eu-west-1",
            size: "t3.2xlarge",
            cloud_name: "AWS HQ",
            cloud_type: "aws_cnr",
            last_used: millisecondsToSeconds(+new Date() - 1 * 24 * 3600 * 1000),
            recommended_size: "t4.2xlarge"
          },
          {
            name: "compute-130845917",
            id: "i-eadc979a97dc9a97c7",
            region: "eu-west-1",
            size: "t3.2xlarge",
            cloud_name: "AWS HQ",
            cloud_type: "aws_cnr",
            last_used: millisecondsToSeconds(+new Date() - 18 * 24 * 3600 * 1000),
            recommended_size: "t4.2xlarge"
          }
        ]
      },
      executors_reservation: {
        count: 0,
        saving: 0,
        items: []
      },
      spot_instances_usage: {
        count: 3,
        items: [
          {
            name: "compute-130845917",
            id: "i-eadc979a97dc9a97c7",
            region: "eu-west-1",
            size: "t2.small",
            cloud_name: "AWS HQ",
            cloud_type: "aws_cnr",
            runs_count: 44,
            average_lifetime: 1040
          },
          {
            name: "compute-983285982",
            id: "i-a9ed7c9a7adc777cad",
            region: "West US 2",
            size: "Standard_A2_v2",
            cloud_name: "Azure QA",
            cloud_type: "azure_cnr",
            runs_count: 24,
            average_lifetime: 800
          },
          {
            name: "compute-491805727",
            id: "i-bce707eabdc707dbeb",
            region: "eu-west-1",
            size: "e2-standard-2",
            cloud_name: "GCP dev",
            cloud_type: "gcp_cnr",
            runs_count: 67,
            average_lifetime: 970
          }
        ]
      },

      local_storage_bottleneck: {
        count: 1,
        items: [
          {
            run: "#1_dazzling_lewin",
            last_run: millisecondsToSeconds(+new Date() - 15 * 60 * 1000),
            name: "compute-1a24cdq251",
            id: "i-03d05ee0324432171",
            cloud_name: "AWS HQ",
            cloud_type: "aws_cnr",
            size: "t2.small",
            io: 250,
            rw: 23000000,
            duration: 3 * 60 * 60 + 15 * 60,
            duration_threshold: 4 * 60 * 60
          }
        ]
      },
      gpu_memory: {
        count: 1,
        items: [
          {
            run: "#1_dazzling_lewin",
            last_run: millisecondsToSeconds(+new Date() - 15 * 60 * 1000),
            name: "compute-1a24cdq251",
            id: "i-03d05ee0324432171",
            cloud_name: "AWS HQ",
            cloud_type: "aws_cnr",
            size: "g4ad.4xlarge",
            gpu_memory_usage: 0.98
          }
        ]
      }
    };

    const timeout = setTimeout(() => {
      setIsLoading(false);
      setApiData(data);
    }, 1000);

    return () => clearTimeout(timeout);
  }, []);

  return { isLoading, data: apiData };
};

const useGetModelRun = (runId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading, shouldInvoke } = useApiState(GET_ML_RUN_DETAILS, { organizationId, runId });

  const { apiData } = useApiData(GET_ML_RUN_DETAILS);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlRunDetails(organizationId, runId));
    }
  }, [dispatch, organizationId, runId, shouldInvoke]);

  return { isLoading, run: apiData };
};

const useGetRunBreakdown = (runId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading, isDataReady, shouldInvoke } = useApiState(GET_ML_RUN_DETAILS_BREAKDOWN, { organizationId, runId });

  const {
    apiData: { breakdown = {}, stages = [], milestones = [] }
  } = useApiData(GET_ML_RUN_DETAILS_BREAKDOWN);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlRunDetailsBreakdown(organizationId, runId));
    }
  }, [dispatch, organizationId, runId, shouldInvoke]);

  return { isLoading, isDataReady, breakdown, stages, milestones };
};

const useGetGlobalParameters = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { goals = [] }
  } = useApiData(GET_ML_GLOBAL_PARAMETERS);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_GLOBAL_PARAMETERS, {
    organizationId
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlGlobalParameters(organizationId));
    }
  }, [dispatch, organizationId, shouldInvoke]);

  return { isLoading, parameters: goals };
};

const useAlwaysGetGlobalParameter = (parameterId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const [parameter, setParameter] = useState({});

  const { isLoading } = useApiState(GET_ML_GLOBAL_PARAMETER, {
    organizationId
  });

  useEffect(() => {
    dispatch((_, getState) => {
      dispatch(getMlGlobalParameter(organizationId, parameterId)).then(() => {
        const state = getState();
        if (!isError(GET_ML_GLOBAL_PARAMETER, getState())) {
          setParameter(state.restapi[GET_ML_GLOBAL_PARAMETER]);
        }
      });
    });
  }, [dispatch, organizationId, parameterId]);

  return { isLoading, parameter };
};

const useCreateGlobalParameter = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_GLOBAL_PARAMETER);

  const onCreate = (params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(createGlobalParameter(organizationId, params)).then(() => {
          if (!isError(CREATE_GLOBAL_PARAMETER, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onCreate, isLoading };
};

const useUpdateGlobalParameter = (parameterId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(UPDATE_GLOBAL_PARAMETER);

  const onUpdate = (params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(updateGlobalParameter(organizationId, parameterId, params)).then(() => {
          if (!isError(UPDATE_GLOBAL_PARAMETER, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onUpdate, isLoading };
};

const useDeleteGlobalParameter = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(DELETE_GLOBAL_PARAMETER);

  const onDelete = (parameterId) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(deleteGlobalParameter(organizationId, parameterId)).then(() => {
          if (!isError(DELETE_GLOBAL_PARAMETER, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onDelete, isLoading };
};

function MlApplicationsService() {
  return {
    useGetAll,
    useCreateApplication,
    useUpdateApplication,
    useDeleteApplication,
    useGetGlobalParameters,
    useGetModelRun,
    useGetRunBreakdown,
    useGetOne,
    useGetModelRunsList,
    useGetModelRecommendation,
    useCreateGlobalParameter,
    useUpdateGlobalParameter,
    useAlwaysGetGlobalParameter,
    useDeleteGlobalParameter
  };
}

export default MlApplicationsService;
