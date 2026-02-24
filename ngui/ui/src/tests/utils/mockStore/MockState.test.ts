import { GET_POOL_ALLOWED_ACTIONS } from "api/auth/actionTypes";
import { MockState } from "utils/MockState";

const POOL_ID = "pool_uuid";
const ORGANIZATION_ID = "organization_uuid";

describe("mockPoolPermissions method testing", () => {
  test("with default/empty state", () => {
    const mockState = MockState();
    mockState.mockPoolPermissions(POOL_ID, ["manage_something"]);
    expect(mockState.state).toEqual({
      auth: {
        [GET_POOL_ALLOWED_ACTIONS]: {
          allowedActions: {
            [POOL_ID]: ["manage_something"],
          },
        },
      },
    });
  });
  describe("extracting existed state", () => {
    test("merge states", () => {
      const mockState = MockState({
        someKey: {
          data: {},
        },
        auth: {
          someAuthKey: "randomString",
          [GET_POOL_ALLOWED_ACTIONS]: {
            allowedActions: {
              pool1: ["p1", "p2"],
              pool2: [],
            },
          },
        },
      });
      mockState.mockPoolPermissions(POOL_ID, ["manage_something"]);
      expect(mockState.state).toEqual({
        someKey: {
          data: {},
        },
        auth: {
          someAuthKey: "randomString",
          [GET_POOL_ALLOWED_ACTIONS]: {
            allowedActions: {
              pool1: ["p1", "p2"],
              pool2: [],
              [POOL_ID]: ["manage_something"],
            },
          },
        },
      });
    });
    test("extend permissions", () => {
      const mockState = MockState({
        auth: {
          [GET_POOL_ALLOWED_ACTIONS]: {
            allowedActions: {
              [POOL_ID]: ["existed_permission"],
            },
          },
        },
      });
      mockState.mockPoolPermissions(POOL_ID, ["manage_something"]);
      expect(mockState.state).toEqual({
        auth: {
          [GET_POOL_ALLOWED_ACTIONS]: {
            allowedActions: {
              [POOL_ID]: ["existed_permission", "manage_something"],
            },
          },
        },
      });
    });
  });
});

describe("mockOrganizationPermissions method testing", () => {
  test("with default/empty state", () => {
    const mockState = MockState();
    mockState.mockOrganizationPermissions(ORGANIZATION_ID, ["manage_something"]);
    expect(mockState.state).toEqual({
      organizationId: ORGANIZATION_ID,
    });
  });
  describe("extracting existed state", () => {
    test("merge states", () => {
      const mockState = MockState({
        organizationId: "existedOrganizationId",
        someKey: {
          data: {},
        },
        restapi: {
          someRestApiKey: "randomString",
        },
      });
      mockState.mockOrganizationPermissions(ORGANIZATION_ID, ["manage_something"]);
      expect(mockState.state).toEqual({
        organizationId: "existedOrganizationId",
        someKey: {
          data: {},
        },
        restapi: {
          someRestApiKey: "randomString",
        },
      });
    });
    test("organization is defined already", () => {
      const mockState = MockState({
        organizationId: "existedOrganizationId",
      });
      mockState.mockOrganizationPermissions(ORGANIZATION_ID, ["manage_something"]);
      expect(mockState.state).toEqual({
        organizationId: "existedOrganizationId",
      });
    });
    test("extend permissions", () => {
      const mockState = MockState({
        organizationId: "existedOrganizationId",
      });
      mockState.mockOrganizationPermissions(ORGANIZATION_ID, ["manage_something"]);
      expect(mockState.state).toEqual({
        organizationId: "existedOrganizationId",
      });
    });
  });
});
