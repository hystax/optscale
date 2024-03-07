import { RESTDataSource, AugmentedRequest } from "@apollo/datasource-rest";
import type { KeyValueCache } from "@apollo/utils.keyvaluecache";

class SlackerClient extends RESTDataSource {
  private token: string;

  override baseURL = "http://slacker/slacker/v2/";

  constructor(options: { token: string; cache: KeyValueCache }) {
    super(options);
    this.token = options.token;
  }

  override willSendRequest(_path: string, request: AugmentedRequest) {
    request.headers["authorization"] = `Bearer ${this.token}`;
  }

  async getInstallPath() {
    const installationPath = await this.get("install_path");

    return installationPath.url;
  }

  async connectSlackUser(secret) {
    return this.post("connect_slack_user", {
      body: JSON.stringify({ secret }),
    });
  }
}

export default SlackerClient;
