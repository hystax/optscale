import React, { useRef, useState } from "react";
import Badge from "@atlaskit/badge";
import Tabs, { Tab, TabList, TabPanel } from "@atlaskit/tabs";
import PropTypes from "prop-types";
import LinkToEnvironmentDetails from "components/LinkToEnvironmentDetails";
import AcquireEnvironmentDropdownButtonContainer from "containers/AcquireEnvironmentDropdownButtonContainer";
import AttachEnvironmentDropdownButtonContainer from "containers/AttachEnvironmentDropdownButtonContainer";
import { isEmpty } from "utils/arrays";
import { differenceInHours } from "utils/datetime";

const Panel = ({ children }) => (
  <div
    style={{
      width: "100%",
      padding: "8px",
      overflow: "auto"
    }}
  >
    {children}
  </div>
);

const ActionsTableHeader = () => (
  <th
    style={{
      minWidth: "120px"
    }}
  >
    Actions
  </th>
);

const EnvironmentNameCell = ({ environment }) => (
  <td>
    <LinkToEnvironmentDetails environment={environment} />
  </td>
);

const MyEnvironmentsTable = ({ environments, onSuccessAttachment, availableIssueStatusesForAutomaticUnlinking }) => {
  const tableRef = useRef();

  const [marginToFitDropdownMenu, setMarginToFitDropdownMenu] = useState(0);

  return (
    <table
      ref={tableRef}
      style={{
        marginBottom: marginToFitDropdownMenu
      }}
    >
      <thead>
        <tr>
          <th>Environment</th>
          <th>Type</th>
          <th>Booking ends</th>
          <th>Issues attached</th>
          <ActionsTableHeader />
        </tr>
      </thead>
      <tbody>
        {environments.map((environment) => {
          const { id: environmentId, details, current_booking: currentBooking } = environment;
          const { details: activeBooking } = currentBooking ?? {};

          return (
            <tr key={environmentId}>
              <EnvironmentNameCell environment={environment} />
              <td>{details.resource_type}</td>
              {activeBooking ? (
                <>
                  <td>
                    {activeBooking.released_at === 0
                      ? "Never"
                      : `In ${differenceInHours(new Date(activeBooking.released_at * 1000), new Date())} hours`}
                  </td>
                  <td>
                    {activeBooking.jira_issue_attachments.length !== 0
                      ? activeBooking.jira_issue_attachments.map((issueAttachment) => (
                          <div key={issueAttachment.id}>{`${issueAttachment.project_key}-${issueAttachment.issue_number}`}</div>
                        ))
                      : "-"}
                  </td>
                </>
              ) : (
                <>
                  <td>-</td>
                  <td>-</td>
                </>
              )}
              <td>
                <AttachEnvironmentDropdownButtonContainer
                  environmentId={environmentId}
                  onSuccess={onSuccessAttachment}
                  availableIssueStatusesForAutomaticUnlinking={availableIssueStatusesForAutomaticUnlinking}
                  tableRef={tableRef}
                  setMarginToFitDropdownMenu={setMarginToFitDropdownMenu}
                />
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};

const AvailableEnvironmentsTable = ({ environments, onSuccessAttachment, availableIssueStatusesForAutomaticUnlinking }) => {
  const tableRef = useRef();

  const [marginToFitDropdownMenu, setMarginToFitDropdownMenu] = useState(0);

  return (
    <table
      ref={tableRef}
      style={{
        marginBottom: marginToFitDropdownMenu
      }}
    >
      <thead>
        <tr>
          <th>Environment</th>
          <th>Type</th>
          <ActionsTableHeader />
        </tr>
      </thead>
      <tbody>
        {environments.map((environment) => {
          const { id: environmentId, details } = environment;

          return (
            <tr key={environmentId}>
              <EnvironmentNameCell environment={environment} />
              <td>{details.resource_type}</td>
              <td>
                <AcquireEnvironmentDropdownButtonContainer
                  environmentId={environmentId}
                  onSuccess={onSuccessAttachment}
                  availableIssueStatusesForAutomaticUnlinking={availableIssueStatusesForAutomaticUnlinking}
                  tableRef={tableRef}
                  setMarginToFitDropdownMenu={setMarginToFitDropdownMenu}
                />
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};

const OtherEnvironmentsTable = ({ environments }) => (
  <table>
    <thead>
      <tr>
        <th>Environment</th>
        <th>Type</th>
        <th>Pool</th>
        <th>Availability</th>
      </tr>
    </thead>
    <tbody>
      {environments.map((environment) => {
        const { id: environmentId, details, current_booking: currentBooking } = environment;
        const { details: activeBooking } = currentBooking ?? {};

        return (
          <tr key={environmentId}>
            <EnvironmentNameCell environment={environment} />
            <td>{details?.resource_type}</td>
            <td>{details?.pool_name}</td>
            {activeBooking ? (
              <>
                <td>
                  {`Acquired by ${activeBooking?.acquired_by?.name}`}
                  {activeBooking.released_at !== 0 && (
                    <>
                      <br />
                      {`Available in ${differenceInHours(new Date(activeBooking.released_at * 1000), new Date())} hours`}
                    </>
                  )}
                </td>
              </>
            ) : (
              <>
                <td>Available</td>
              </>
            )}
          </tr>
        );
      })}
    </tbody>
  </table>
);

const TabTitle = ({ message, count }) => (
  <>
    {message} {<Badge>{count}</Badge>}
  </>
);

const AttachAnotherEnvironment = ({
  myEnvironments = [],
  availableEnvironments = [],
  otherEnvironments = [],
  onSuccessAttachment = () => {},
  availableIssueStatusesForAutomaticUnlinking
}) => {
  const tabs = [
    {
      title: { message: "My", badgeCount: myEnvironments.length },
      panelContent: !isEmpty(myEnvironments) ? (
        <MyEnvironmentsTable
          environments={myEnvironments}
          onSuccessAttachment={onSuccessAttachment}
          availableIssueStatusesForAutomaticUnlinking={availableIssueStatusesForAutomaticUnlinking}
        />
      ) : (
        "No my environments"
      )
    },
    {
      title: { message: "Available", badgeCount: availableEnvironments.length },
      panelContent: !isEmpty(availableEnvironments) ? (
        <AvailableEnvironmentsTable
          environments={availableEnvironments}
          onSuccessAttachment={onSuccessAttachment}
          availableIssueStatusesForAutomaticUnlinking={availableIssueStatusesForAutomaticUnlinking}
        />
      ) : (
        "No available environments"
      )
    },
    {
      title: { message: "Other", badgeCount: otherEnvironments.length },
      panelContent: !isEmpty(otherEnvironments) ? (
        <OtherEnvironmentsTable environments={otherEnvironments} />
      ) : (
        "No other environments"
      )
    }
  ];

  return (
    <div>
      <p>Select environment for this issue</p>
      <Tabs id="default">
        <TabList>
          {tabs.map(({ title }) => (
            <Tab key={title.message}>
              <TabTitle message={title.message} count={title.badgeCount} />
            </Tab>
          ))}
        </TabList>
        {tabs.map(({ title, panelContent }) => (
          <TabPanel key={title.message}>
            <Panel>{panelContent}</Panel>
          </TabPanel>
        ))}
      </Tabs>
    </div>
  );
};

AttachAnotherEnvironment.propTypes = {
  myEnvironments: PropTypes.array.isRequired,
  availableEnvironments: PropTypes.array.isRequired,
  otherEnvironments: PropTypes.array.isRequired,
  onSuccessAttachment: PropTypes.func,
  availableIssueStatusesForAutomaticUnlinking: PropTypes.array.isRequired
};

export default AttachAnotherEnvironment;
