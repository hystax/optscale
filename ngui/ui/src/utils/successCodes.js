import {
  MARK_RESOURCES_AS_ENVIRONMENTS,
  UPLOAD_CLOUD_REPORT,
  CREATE_INVITATIONS,
  CREATE_ASSIGNMENT_RULE,
  DELETE_EMPLOYEE,
  UPLOAD_CODE_REPORT,
  UPDATE_ORGANIZATION_OPTION,
  UPDATE_OPTIMIZATION_OPTIONS,
  STOP_ML_RUNSET
} from "api/restapi/actionTypes";
import { ALERT_SEVERITY } from "./constants";

const defaultSettings = Object.freeze({
  code: "FE0000"
});

const labelToSuccessSettingsMap = Object.freeze({
  [UPLOAD_CLOUD_REPORT]: {
    code: "FE0001"
  },
  [UPLOAD_CODE_REPORT]: {
    code: "FE0001"
  },
  [CREATE_INVITATIONS]: {
    code: "FE0003",
    getMessageParams: (params) => [Object.keys(params.invites).length]
  },
  [MARK_RESOURCES_AS_ENVIRONMENTS]: {
    code: "FE0006",
    getSeverity: (_, response) => (response.data?.succeeded?.length === 0 ? ALERT_SEVERITY.ERROR : ALERT_SEVERITY.SUCCESS),
    getMessageParams: (_, response) => {
      const successfullyMarkedResourcedCount = response.data?.succeeded?.length ?? 0;
      const unsuccessfullyMarkedResourcedCount = response.data?.failed?.length ?? 0;
      return [successfullyMarkedResourcedCount, successfullyMarkedResourcedCount + unsuccessfullyMarkedResourcedCount];
    }
  },
  [CREATE_ASSIGNMENT_RULE]: {
    code: "FE0007",
    getMessageParams: ({ name }) => [name]
  },
  [DELETE_EMPLOYEE]: {
    code: "FE0008"
  },
  [UPDATE_ORGANIZATION_OPTION]: {
    code: "FE0009"
  },
  [UPDATE_OPTIMIZATION_OPTIONS]: {
    code: "FE0010",
    getMessageParams: (_, __, payload) => [payload.settingType]
  },
  [STOP_ML_RUNSET]: {
    code: "FE0011"
  }
});

export const getSuccessAlertSettingsByLabel = (label) => labelToSuccessSettingsMap[label] || defaultSettings;
