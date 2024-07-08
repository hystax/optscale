import BaseClient from "../baseClient.js";
class KeeperClient extends BaseClient {
  override baseURL = `${
    process.env.KEEPER_ENDPOINT || this.endpoint
  }/report/v2/`;

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

    return events.events;
  }
}

export default KeeperClient;
