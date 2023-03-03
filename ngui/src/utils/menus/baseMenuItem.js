import { v4 as uuidv4 } from "uuid";
import BaseRoute from "utils/routes";

class BaseMenuItem {
  key = uuidv4();

  route = new BaseRoute();

  messageId = "";

  dataTestId = "";
}

export default BaseMenuItem;
