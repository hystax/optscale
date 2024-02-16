import path from "path";
import { RESTDataSource, AugmentedRequest } from "@apollo/datasource-rest";
import type { KeyValueCache } from "@apollo/utils.keyvaluecache";
import { RequestParam } from "../../graphql/__generated__/resolversTypes.js";

class KeeperClient extends RESTDataSource {
  private token: string;

  override baseURL = path.join(process.env.PROXY_URL, "/report/v2/");

  constructor(options: { token: string; cache: KeyValueCache }) {
    super(options);
    this.token = options.token;
  }

  override willSendRequest(_path: string, request: AugmentedRequest) {
    request.headers["authorization"] = `Bearer ${this.token}`;
  }

  async getEvents(organizationId: string, requestParams: RequestParam) {
    const params = new URLSearchParams();

    const paramsMapping = {
      timeStart: "time_start",
      timeEnd: "time_end",
      lastId: "last_id",
      includeRead: "include_read",
      readOnGet: "read_on_get",
    };

    // This is temporary. All URL parameters must be strings.
    // Mapping will be done elsewhere, not clear how at this point.
    Object.entries(requestParams).forEach(([key, value]) => {
      const stringValue = value.toString();

      const mappedParam = paramsMapping[key];

      if (mappedParam) {
        params.append(mappedParam, stringValue);
      } else {
        params.append(key, stringValue);
      }
    });

    const events = await this.get(
      `organizations/${organizationId}/events?${params}`
    );

    // This will go away after https://datatrendstech.atlassian.net/browse/OS-6395
    return JSON.parse(events).events;
  }
}

export default KeeperClient;
