import BaseClient from "../baseClient.js";
import { EventsRequestParams } from "../../graphql/__generated__/types/keeper";
import { getParams } from "../../utils/getParams.js";

class KeeperClient extends BaseClient {
  override baseURL = `${process.env.KEEPER_ENDPOINT || this.endpoint}/report/v2/`;

  async getEvents(organizationId: string, requestParams: EventsRequestParams) {
    const path = `organizations/${organizationId}/events`;

    const events = await this.get(path, {
      params: getParams(requestParams),
    });

    return events.events;
  }
}

export default KeeperClient;
