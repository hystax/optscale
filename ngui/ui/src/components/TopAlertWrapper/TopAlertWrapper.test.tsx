import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(<TestProvider>null</TestProvider>);
  root.unmount();
});
// import { IntlProvider } from "react-intl";
// import { Provider } from "react-redux";
// import { act, create } from "react-test-renderer";
// import { createStore } from "redux";
// import { apiEnd, apiStart, apiSuccess } from "api";
// import { GET_CLOUD_ACCOUNTS } from "api/restapi/actionTypes";
// import { onSuccessGetCloudAccounts } from "api/restapi/handlers";
// import { hashParams } from "api/utils";
// import { setScopeId } from "containers/OrganizationSelectorContainer/actionCreators";
// import intlConfig from "translations/react-intl-config";
// import { ENVIRONMENT } from "utils/constants";
// import { addHours } from "utils/datetime";
// import rootReducer from "../../reducers";
// import { updateOrganizationTopAlert } from "./actionCreators";
// import { ALERTS } from "./reducer";
// import TopAlertWrapper, { ALERT_TYPES } from "./TopAlertWrapper";

// const mockMakeRequest = (store, data) => {
//   store.dispatch(apiStart(GET_CLOUD_ACCOUNTS, hashParams("id")));
//   store.dispatch(
//     apiSuccess({
//       label: GET_CLOUD_ACCOUNTS,
//       response: {
//         cloud_accounts: [
//           {
//             type: "any type",
//             last_import_at: 123
//           }
//         ]
//       },
//       ttl: addHours(new Date(), 5)
//     })
//   );
//   store.dispatch(onSuccessGetCloudAccounts(data));
//   store.dispatch(apiEnd(GET_CLOUD_ACCOUNTS));
// };

// const Template = ({ store }) => (
//   <Provider store={store}>
//     <IntlProvider {...intlConfig}>
//       <TopAlertWrapper />
//     </IntlProvider>
//   </Provider>
// );

// it("alert can be closed", () => {
//   const store = createStore(rootReducer, {
//     organizationId: "id",
//     api: {
//       [GET_CLOUD_ACCOUNTS]: {
//         isLoading: false,
//         timestamp: addHours(new Date(), 5),
//         hash: hashParams("id")
//       }
//     },
//     restapi: {
//       [GET_CLOUD_ACCOUNTS]: {
//         cloudAccounts: [
//           {
//             type: ENVIRONMENT
//           }
//         ]
//       }
//     }
//   });

//   let tree;

//   act(() => {
//     tree = create(<Template store={store} />);
//   });
//   expect(tree.toJSON().props["data-test-id"]).toEqual("top_alert_private_deployment");

//   act(() => {
//     store.dispatch(updateOrganizationTopAlert("id", { id: ALERT_TYPES.AVAILABLE_FOR_PRIVATE_DEPLOYMENT, closed: true }));
//     tree.update(<Template store={store} />);
//   });
//   expect(tree.toJSON()).toEqual(null);
// });

// it("should render «private deployment» top alert if there only environment data sources", () => {
//   const store = createStore(rootReducer, {
//     organizationId: "id",
//     api: {
//       [GET_CLOUD_ACCOUNTS]: {
//         isLoading: false,
//         timestamp: addHours(new Date(), 5),
//         hash: hashParams("id")
//       }
//     },
//     restapi: {
//       [GET_CLOUD_ACCOUNTS]: {
//         cloudAccounts: [
//           {
//             type: ENVIRONMENT
//           }
//         ]
//       }
//     }
//   });

//   const tree = create(<Template store={store} />).toJSON();

//   expect(tree.props["data-test-id"]).toEqual("top_alert_private_deployment");
// });

// it("should render «data processing» alert if some data source proceeding its data", () => {
//   const store = createStore(rootReducer, {
//     organizationId: "id",
//     api: {
//       [GET_CLOUD_ACCOUNTS]: {
//         isLoading: false,
//         timestamp: addHours(new Date(), 5),
//         hash: hashParams("id")
//       }
//     },
//     restapi: {
//       [GET_CLOUD_ACCOUNTS]: {
//         cloudAccounts: [
//           {
//             type: "any type",
//             last_import_at: 0
//           }
//         ]
//       }
//     }
//   });

//   const tree = create(<Template store={store} />).toJSON();

//   expect(tree.props["data-test-id"]).toEqual("top_alert_data_processing");
// });

// it("should render «data proceeded alert» if all data sources completed their expenses processing", () => {
//   const store = createStore(rootReducer, {
//     organizationId: "id",
//     api: {
//       [GET_CLOUD_ACCOUNTS]: {
//         isLoading: false,
//         timestamp: addHours(new Date(), 5),
//         hash: hashParams("id")
//       }
//     },
//     restapi: {
//       [GET_CLOUD_ACCOUNTS]: {
//         cloudAccounts: [
//           {
//             type: "any type",
//             last_import_at: 123
//           }
//         ]
//       }
//     },
//     [ALERTS]: {
//       id: [
//         {
//           id: ALERT_TYPES.DATA_SOURCES_ARE_PROCESSING,
//           triggered: true
//         }
//       ]
//     }
//   });

//   const tree = create(<Template store={store} />).toJSON();

//   expect(tree.props["data-test-id"]).toEqual("top_alert_data_proceeded");
// });

// it("should render in order «no banner» --> «data proceeding» --> «data proceeded» --> «data proceeding»", async () => {
//   const store = createStore(rootReducer, {
//     organizationId: "id"
//   });

//   let tree;
//   act(() => {
//     tree = create(<Template store={store} />);
//   });
//   expect(tree.toJSON()).toEqual(null);

//   act(() => {
//     mockMakeRequest(store, {
//       cloud_accounts: [
//         {
//           type: "any type",
//           last_import_at: 0
//         }
//       ]
//     });
//     tree.update(<Template store={store} />);
//   });
//   expect(tree.toJSON().props["data-test-id"]).toEqual("top_alert_data_processing");

//   act(() => {
//     mockMakeRequest(store, {
//       cloud_accounts: [
//         {
//           type: "any type",
//           last_import_at: 123
//         }
//       ]
//     });
//     tree.update(<Template store={store} />);
//   });
//   expect(tree.toJSON().props["data-test-id"]).toEqual("top_alert_data_proceeded");

//   act(() => {
//     mockMakeRequest(store, {
//       cloud_accounts: [
//         {
//           type: "any new type",
//           last_import_at: 0
//         }
//       ]
//     });
//     tree.update(<Template store={store} />);
//   });
//   expect(tree.toJSON().props["data-test-id"]).toEqual("top_alert_data_processing");
// });

// it("should not render closed alert when organization changed", () => {
//   const store = createStore(rootReducer, {
//     organizationId: "id",
//     api: {
//       [GET_CLOUD_ACCOUNTS]: {
//         isLoading: false,
//         timestamp: addHours(new Date(), 5),
//         hash: hashParams("id")
//       }
//     },
//     restapi: {
//       [GET_CLOUD_ACCOUNTS]: {
//         cloudAccounts: [
//           {
//             type: ENVIRONMENT
//           }
//         ]
//       }
//     }
//   });

//   let tree;

//   act(() => {
//     tree = create(<Template store={store} />);
//   });
//   expect(tree.toJSON().props["data-test-id"]).toEqual("top_alert_private_deployment");

//   act(() => {
//     store.dispatch(updateOrganizationTopAlert("id", { id: ALERT_TYPES.AVAILABLE_FOR_PRIVATE_DEPLOYMENT, closed: true }));
//     tree.update(<Template store={store} />);
//   });
//   expect(tree.toJSON()).toEqual(null);

//   act(() => {
//     store.dispatch(setScopeId("id2"));
//     mockMakeRequest(store, {
//       cloud_accounts: [
//         {
//           type: "org 2 cloud type",
//           last_import_at: 123
//         }
//       ]
//     });
//     tree.update(<Template store={store} />);
//   });
//   expect(tree.toJSON()).toEqual(null);

//   act(() => {
//     store.dispatch(setScopeId("id"));
//     mockMakeRequest(store, {
//       cloud_accounts: [
//         {
//           type: ENVIRONMENT
//         }
//       ]
//     });
//     tree.update(<Template store={store} />);
//   });
//   expect(tree.toJSON()).toEqual(null);
// });
