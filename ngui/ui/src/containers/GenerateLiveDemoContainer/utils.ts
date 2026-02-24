import { RESTAPI } from "api";
import { GET_LIVE_DEMO } from "api/restapi/actionTypes";

type LiveDemoSelectors = {
  getIsAlive: () => boolean;
  getOrganizationId: () => string;
  getEmail: () => string;
  getPassword: () => string;
};

type getStateFn = () => LiveDemoState;

type LiveDemoState = {
  restapi?: {
    [GET_LIVE_DEMO]?: LiveDemoFields;
  };
};

type LiveDemoFields = {
  is_alive?: boolean;
  organization_id?: string;
  email?: string;
  password?: string;
};

type LiveDemoField = keyof LiveDemoFields;

const getStateField = <T extends LiveDemoField>(
  getState: getStateFn,
  field: T,
  defaultValue: NonNullable<LiveDemoFields[T]>
): NonNullable<LiveDemoFields[T]> => getState()?.[RESTAPI]?.[GET_LIVE_DEMO]?.[field] ?? defaultValue;

export const createLiveDemoSelectors = (getState: getStateFn): LiveDemoSelectors => ({
  getIsAlive: (): boolean => getStateField(getState, "is_alive", false),
  getOrganizationId: (): string => getStateField(getState, "organization_id", ""),
  getEmail: (): string => getStateField(getState, "email", ""),
  getPassword: (): string => getStateField(getState, "password", ""),
});
