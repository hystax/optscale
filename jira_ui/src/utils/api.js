import makeRequest from "utils/makeRequest";

export const getIsUserConnectedToOptscale = async () => {
  const { data, error } = await makeRequest({
    url: "/jira_bus/v2/user_assignment",
    options: {
      method: "GET"
    }
  });

  if (error && error.error_code !== "OJ0008") {
    return Promise.reject(error);
  }

  if (error && error.error_code === "OJ0008") {
    return Promise.resolve({ isConnected: false });
  }

  return Promise.resolve({ isConnected: Boolean(data.auth_user_id) });
};

export const getIsOrganizationAssigned = async () => {
  const { data, error } = await makeRequest({
    url: "/jira_bus/v2/organization_assignment",
    options: {
      method: "GET"
    }
  });

  if (error && error.error_code !== "OJ0019") {
    return Promise.reject(error);
  }
  if (error && error.error_code === "OJ0019") {
    return Promise.resolve({ isOrganizationAssigned: false });
  }

  return Promise.resolve({ isOrganizationAssigned: Boolean(data) });
};

export const getCurrentIssueEnvironments = async () => {
  const { data, error } = await makeRequest({
    url: "/jira_bus/v2/shareable_resource?current_issue=true"
  });

  if (error) {
    return Promise.reject(error);
  }

  return Promise.resolve(data);
};

export const getAllEnvironments = async () => {
  const { data, error } = await makeRequest({
    url: "/jira_bus/v2/shareable_resource"
  });

  if (error) {
    return Promise.reject(error);
  }

  return Promise.resolve(data);
};

export const getCurrentIssueInfo = async () => {
  const { data, error } = await makeRequest({
    url: "/jira_bus/v2/issue_info"
  });

  if (error) {
    return Promise.reject(error);
  }

  return Promise.resolve(data);
};
