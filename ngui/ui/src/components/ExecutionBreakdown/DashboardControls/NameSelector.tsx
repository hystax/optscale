import ShareOutlinedIcon from "@mui/icons-material/ShareOutlined";
import { FormattedMessage } from "react-intl";
import Icon from "components/Icon";
import Selector from "components/Selector";
import SelectorLoader from "components/SelectorLoader";
import { DEFAULT_DASHBOARD } from "hooks/useModelRunChartState";

export const DEFAULT_ID = "default";

const NameSelector = ({ dashboards, currentEmployeeId, selected, onChange, saved, isLoading }) => {
  const defaultDashboard = dashboards.find(({ id }) => id === DEFAULT_DASHBOARD.id);

  const myDashboards = dashboards.filter(({ owner_id: ownerId }) => ownerId === currentEmployeeId);

  const sharedDashboards = dashboards.filter(({ owner_id: ownerId, shared }) => ownerId !== currentEmployeeId && shared);

  const formatDashboardName = (id, name) => {
    const markAsNotSaved = id === selected && !saved;

    if (markAsNotSaved) {
      return `${name} *`;
    }

    return name;
  };

  const selectorData = {
    items: [
      {
        value: defaultDashboard.id,
        name: formatDashboardName(defaultDashboard.id, defaultDashboard.name),
        shared: false
      },
      {
        render: ({ title }) =>
          title({
            children: <FormattedMessage id="mine" />
          })
      },
      ...myDashboards.map(({ id, name, shared }) => ({
        value: id,
        name: formatDashboardName(id, name),
        shared,
        owned: true
      })),
      {
        render: ({ title }) =>
          title({
            children: <FormattedMessage id="shared" />
          })
      },
      ...sharedDashboards.map(({ id, name, shared }) => ({
        value: id,
        name: formatDashboardName(id, name),
        shared,
        owned: false
      }))
    ],
    selected
  };

  return isLoading ? (
    <SelectorLoader labelId="dashboard" />
  ) : (
    <Selector
      sx={{ minWidth: { sm: "300px", xs: "200px" } }}
      onChange={onChange}
      data={selectorData}
      labelId="dashboard"
      menuItemIcon={{
        placement: "end",
        component: ({ shared }) => {
          if (shared) {
            return (
              <Icon
                icon={ShareOutlinedIcon}
                hasLeftMargin
                color="inherit"
                fontSize="inherit"
                tooltip={{
                  show: true,
                  messageId: "shared"
                }}
              />
            );
          }

          return null;
        },
        getComponentProps: (item) => item
      }}
    />
  );
};

export default NameSelector;
