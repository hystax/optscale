import BaseClient from "../baseClient.js";
import {
  MutationTokenArgs,
  MutationUpdateUserArgs,
  OrganizationAllowedActionsRequestParams,
} from "../../graphql/__generated__/types/auth";
import { getParams } from "../../utils/getParams.js";

class AuthClient extends BaseClient {
  override baseURL = `${process.env.AUTH_ENDPOINT || this.endpoint}/auth/v2/`;

  async getOrganizationAllowedActions(requestParams: OrganizationAllowedActionsRequestParams) {
    const path = `allowed_actions`;

    const actions = await this.get(path, {
      params: getParams({
        organization: requestParams.organization,
      }),
    });

    return actions.allowed_actions;
  }

  async createToken({ email, password, code }: MutationTokenArgs) {
    const result = await this.post("tokens", {
      body: { email, password, verification_code: code },
    });

    return {
      token: result.token,
      user_email: result.user_email,
      user_id: result.user_id,
    };
  }

  async createUser(email, password, name) {
    const result = await this.post("users", {
      body: { email, password, display_name: name },
    });

    return {
      token: result.token,
      user_email: result.email,
      user_id: result.id,
      verified: result.verified,
    };
  }

  async updateUser(userId: MutationUpdateUserArgs["id"], params: MutationUpdateUserArgs["params"]) {
    const result = await this.patch(`users/${userId}`, {
      body: { display_name: params.name, password: params.password },
    });

    return {
      token: result.token,
      user_email: result.email,
      user_id: result.id,
    };
  }

  async signIn(provider, token, tenantId, redirectUri) {
    const result = await this.post("signin", {
      body: {
        provider,
        token,
        tenant_id: tenantId,
        redirect_uri: redirectUri,
      },
    });

    return {
      token: result.token,
      user_email: result.user_email,
      user_id: result.user_id,
    };
  }
}

export default AuthClient;
