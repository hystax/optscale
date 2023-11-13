import BaseRoute from "./baseRoute";

class NotFoundRoute extends BaseRoute {
  context = { messageId: "notFound" };

  link = "*";

  page = "Error";
}

export default new NotFoundRoute();
