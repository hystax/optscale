import ShareOutlinedIcon from "@mui/icons-material/ShareOutlined";
import { FormattedMessage } from "react-intl";
import Selector, { Item, ItemContent, Title } from "components/Selector";
import { DEFAULT_DASHBOARD } from "hooks/useModelRunChartState";

export const DEFAULT_ID = "default";

const NameSelector = ({ dashboards, currentEmployeeId, selected, onChange, saved = false, isLoading = false }) => {
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

  return (
    <Selector
      id="run-dashboard-selector"
      value={selected}
      onChange={onChange}
      labelMessageId="dashboard"
      isLoading={isLoading}
      sx={{ minWidth: { sm: "300px", xs: "200px" } }}
    >
      <Item value={defaultDashboard.id}>
        <ItemContent>{formatDashboardName(defaultDashboard.id, defaultDashboard.name)}</ItemContent>
      </Item>
      <Title>
        <FormattedMessage id="mine" />
      </Title>
      {myDashboards.map(({ id, name, shared }) => {
        const icon = shared
          ? {
              placement: "end",
              IconComponent: ShareOutlinedIcon,
              tooltipTitle: <FormattedMessage id="shared" />
            }
          : undefined;

        return (
          <Item key={id} value={id}>
            <ItemContent icon={icon}>{formatDashboardName(id, name)}</ItemContent>
          </Item>
        );
      })}
      <Title>
        <FormattedMessage id="shared" />
      </Title>
      {sharedDashboards.map(({ id, name, shared }) => {
        const icon = shared
          ? {
              placement: "end",
              IconComponent: ShareOutlinedIcon,
              tooltipTitle: <FormattedMessage id="shared" />
            }
          : undefined;

        return (
          <Item key={id} value={id}>
            <ItemContent icon={icon}>{formatDashboardName(id, name)}</ItemContent>
          </Item>
        );
      })}
    </Selector>
  );
};

export default NameSelector;
