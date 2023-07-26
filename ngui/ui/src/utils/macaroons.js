import { deserialize } from "node-macaroons";
import { booleanStringToBoolean } from "utils/strings";

export default {
  deserialize: (token) => deserialize(token),
  processCaveats: (caveats) =>
    (caveats ?? []).reduce((result, { _identifier = ":" }) => {
      const [key, value] = _identifier.split(":");
      return { ...result, ...{ [key]: booleanStringToBoolean(value) } };
    }, {})
};
