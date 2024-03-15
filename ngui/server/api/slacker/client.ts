import BaseClient from "../baseClient.js";

class SlackerClient extends BaseClient {
  override baseURL = `${
    process.env.SLACKER_ENDPOINT || this.endpoint
  }/slacker/v2/`;

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
