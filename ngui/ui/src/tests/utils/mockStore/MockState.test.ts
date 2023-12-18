import { GET_POOL_ALLOWED_ACTIONS, GET_ORGANIZATION_ALLOWED_ACTIONS } from "api/auth/actionTypes";
import { GET_ORGANIZATIONS } from "api/restapi/actionTypes";
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
            [POOL_ID]: ["manage_something"]
          }
        }
      }
    });
  });
  describe("extracting existed state", () => {
    test("merge states", () => {
      const mockState = MockState({
        someKey: {
          data: {}
        },
        auth: {
          someAuthKey: "randomString",
          [GET_POOL_ALLOWED_ACTIONS]: {
            allowedActions: {
              pool1: ["p1", "p2"],
              pool2: []
            }
          }
        }
      });
      mockState.mockPoolPermissions(POOL_ID, ["manage_something"]);
      expect(mockState.state).toEqual({
        someKey: {
          data: {}
        },
        auth: {
          someAuthKey: "randomString",
          [GET_POOL_ALLOWED_ACTIONS]: {
            allowedActions: {
              pool1: ["p1", "p2"],
              pool2: [],
              [POOL_ID]: ["manage_something"]
            }
          }
        }
      });
    });
    test("extend permissions", () => {
      const mockState = MockState({
        auth: {
          [GET_POOL_ALLOWED_ACTIONS]: {
            allowedActions: {
              [POOL_ID]: ["existed_permission"]
            }
          }
        }
      });
      mockState.mockPoolPermissions(POOL_ID, ["manage_something"]);
      expect(mockState.state).toEqual({
        auth: {
          [GET_POOL_ALLOWED_ACTIONS]: {
            allowedActions: {
              [POOL_ID]: ["existed_permission", "manage_something"]
            }
          }
        }
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
      restapi: {
        [GET_ORGANIZATIONS]: {
          organizations: [
            {
              id: ORGANIZATION_ID
            }
          ]
        }
      },
      auth: {
        [GET_ORGANIZATION_ALLOWED_ACTIONS]: {
          allowedActions: {
            [ORGANIZATION_ID]: ["manage_something"]
          }
        }
      }
    });
  });
  describe("extracting existed state", () => {
    test("merge states", () => {
      const mockState = MockState({
        organizationId: "existedOrganizationId",
        someKey: {
          data: {}
        },
        restapi: {
          someRestApiKey: "randomString",
          [GET_ORGANIZATIONS]: {
            organizations: [{ id: "org1" }, { id: "org2" }]
          }
        },
        auth: {
          someAuthKey: "randomString",
          [GET_ORGANIZATION_ALLOWED_ACTIONS]: {
            allowedActions: {
              org1: ["p1", "p2"],
              org2: []
            }
          }
        }
      });
      mockState.mockOrganizationPermissions(ORGANIZATION_ID, ["manage_something"]);
      expect(mockState.state).toEqual({
        organizationId: "existedOrganizationId",
        someKey: {
          data: {}
        },
        restapi: {
          someRestApiKey: "randomString",
          [GET_ORGANIZATIONS]: {
            organizations: [
              { id: "org1" },
              { id: "org2" },
              {
                id: ORGANIZATION_ID
              }
            ]
          }
        },
        auth: {
          someAuthKey: "randomString",
          [GET_ORGANIZATION_ALLOWED_ACTIONS]: {
            allowedActions: {
              org1: ["p1", "p2"],
              org2: [],
              [ORGANIZATION_ID]: ["manage_something"]
            }
          }
        }
      });
    });
    test("organization is defined already", () => {
      const mockState = MockState({
        organizationId: "existedOrganizationId"
      });
      mockState.mockOrganizationPermissions(ORGANIZATION_ID, ["manage_something"]);
      expect(mockState.state).toEqual({
        organizationId: "existedOrganizationId",
        restapi: {
          [GET_ORGANIZATIONS]: {
            organizations: [
              {
                id: ORGANIZATION_ID
              }
            ]
          }
        },
        auth: {
          [GET_ORGANIZATION_ALLOWED_ACTIONS]: {
            allowedActions: {
              [ORGANIZATION_ID]: ["manage_something"]
            }
          }
        }
      });
    });
    test("extend permissions", () => {
      const mockState = MockState({
        organizationId: "existedOrganizationId",
        auth: {
          [GET_ORGANIZATION_ALLOWED_ACTIONS]: {
            allowedActions: {
              [ORGANIZATION_ID]: ["existed_permission"]
            }
          }
        }
      });
      mockState.mockOrganizationPermissions(ORGANIZATION_ID, ["manage_something"]);
      expect(mockState.state).toEqual({
        organizationId: "existedOrganizationId",
        restapi: {
          [GET_ORGANIZATIONS]: {
            organizations: [
              {
                id: ORGANIZATION_ID
              }
            ]
          }
        },
        auth: {
          [GET_ORGANIZATION_ALLOWED_ACTIONS]: {
            allowedActions: {
              [ORGANIZATION_ID]: ["existed_permission", "manage_something"]
            }
          }
        }
      });
    });
  });
});
