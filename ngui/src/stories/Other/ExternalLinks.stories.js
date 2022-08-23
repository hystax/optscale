import React from "react";
import TableUseMemoWrapper from "stories/Other/TableUseMemoWrapper";
import WrapperCard from "components/WrapperCard";
import Link from "@mui/material/Link";
import { isEmpty } from "utils/arrays";
import {
  PRODUCTION,
  HYSTAX,
  HYSTAX_CLOUD_MIGRATION,
  HYSTAX_DISASTER_RECOVERY,
  HYSTAX_CLOUD_MIGRATION_AWS,
  HYSTAX_CLOUD_MIGRATION_AZURE,
  HYSTAX_CLOUD_MIGRATION_GCP,
  HYSTAX_CLOUD_MIGRATION_VMWARE,
  HYSTAX_CLOUD_MIGRATION_ALIBABA,
  HYSTAX_CLOUD_MIGRATION_OPENSTACK,
  HYSTAX_DISASTER_RECOVERY_AWS,
  HYSTAX_DISASTER_RECOVERY_AZURE,
  HYSTAX_DISASTER_RECOVERY_GCP,
  HYSTAX_DISASTER_RECOVERY_VMWARE,
  HYSTAX_DISASTER_RECOVERY_ALIBABA,
  HYSTAX_DISASTER_RECOVERY_OPENSTACK,
  AWS_MARKETPLACE,
  AZURE_MARKETPLACE,
  ALIBABA_MARKETPLACE,
  // Hystax documentation urls
  DOCS_HYSTAX_OPTSCALE,
  DOCS_HYSTAX_AUTO_BILLING_AWS,
  DOCS_HYSTAX_DISCOVER_RESOURCES,
  DOCS_HYSTAX_CONNECT_AZURE_ACCOUNT,
  DOCS_HYSTAX_RESOURCE_CONSTRAINTS,
  GITHUB_HYSTAX_K8S_COST_METRICS_COLLECTOR,
  GITHUB_HYSTAX_EXTRACT_LINKED_REPORTS,
  DOCS_HYSTAX_CLUSTERS,
  DOCS_HYSTAX_CLEANUP_SCRIPTS,
  HYSTAX_MARKETPLACES_ANCHOR
} from "urls";
import { KINDS } from "stories";

export default {
  title: `${KINDS.OTHER}/ExternalLinks`
};

const cloudMigrationToLinksUsages = [
  '"Cloud Migrations" page',
  "Redirect to a corresponding cloud-migration page",
  "Wraps a corresponding cloud logo"
];
const disasterRecoveryToLinksUsages = [
  '"Disaster Recovery" page',
  "Redirect to a corresponding cloud-migration page",
  "Wraps a corresponding cloud logo"
];

const linksDefinition = {
  Other: [
    {
      link: PRODUCTION,
      usages: [
        "To check if we are (user/users/etc) in the production environment (used to enable GA and Hotjar)",
        "Add link to a PDF file"
      ]
    },
    {
      link: HYSTAX,
      usages: ["On the authorization, registration and reset password pages (top-right corner)"]
    },
    {
      link: HYSTAX_CLOUD_MIGRATION,
      usages: ['In a description on the "Cloud Migrations" page']
    },
    {
      link: HYSTAX_DISASTER_RECOVERY,
      usages: ['In a description on the "Disaster Recovery" page']
    },
    {
      link: AWS_MARKETPLACE,
      usages: ["cloud-account/connect"]
    },
    {
      link: AZURE_MARKETPLACE,
      usages: ["cloud-account/connect"]
    },
    {
      link: ALIBABA_MARKETPLACE,
      usages: ["cloud-account/connect"]
    },
    {
      link: HYSTAX_MARKETPLACES_ANCHOR,
      usages: ["Top Alert"]
    }
  ],
  "Live cloud migration to": [
    {
      link: HYSTAX_CLOUD_MIGRATION_AWS,
      usages: cloudMigrationToLinksUsages
    },
    {
      link: HYSTAX_CLOUD_MIGRATION_AZURE,
      usages: cloudMigrationToLinksUsages
    },
    {
      link: HYSTAX_CLOUD_MIGRATION_GCP,
      usages: cloudMigrationToLinksUsages
    },
    {
      link: HYSTAX_CLOUD_MIGRATION_VMWARE,
      usages: cloudMigrationToLinksUsages
    },
    {
      link: HYSTAX_CLOUD_MIGRATION_ALIBABA,
      usages: cloudMigrationToLinksUsages
    },
    {
      link: HYSTAX_CLOUD_MIGRATION_OPENSTACK,
      usages: cloudMigrationToLinksUsages
    }
  ],
  "Disaster recovery to": [
    {
      link: HYSTAX_DISASTER_RECOVERY_AWS,
      usages: disasterRecoveryToLinksUsages
    },
    {
      link: HYSTAX_DISASTER_RECOVERY_AZURE,
      usages: disasterRecoveryToLinksUsages
    },
    {
      link: HYSTAX_DISASTER_RECOVERY_GCP,
      usages: disasterRecoveryToLinksUsages
    },
    {
      link: HYSTAX_DISASTER_RECOVERY_VMWARE,
      usages: disasterRecoveryToLinksUsages
    },
    {
      link: HYSTAX_DISASTER_RECOVERY_ALIBABA,
      usages: disasterRecoveryToLinksUsages
    },
    {
      link: HYSTAX_DISASTER_RECOVERY_OPENSTACK,
      usages: disasterRecoveryToLinksUsages
    }
  ],
  "Hystax documentation urls": [
    {
      link: DOCS_HYSTAX_OPTSCALE,
      usages: ['Page title -> "DOCUMENTATION" button', '"OptScale Privacy Policy" alert dialog']
    },
    {
      link: DOCS_HYSTAX_AUTO_BILLING_AWS,
      usages: ["Connect cloud account form description (AWS Root and AWS Linked)"]
    },
    {
      link: DOCS_HYSTAX_DISCOVER_RESOURCES,
      usages: ["Connect cloud account form description (AWS Linked - 'read-only policy for resource discovery' label)"]
    },
    {
      link: DOCS_HYSTAX_CONNECT_AZURE_ACCOUNT,
      usages: ["Connect cloud account form description (Azure)"]
    },
    {
      link: DOCS_HYSTAX_RESOURCE_CONSTRAINTS,
      usages: [
        'Pools page -> Constraints tab -> "Get more help" label',
        'Resource details page -> Constraints tab -> "Get more help" label'
      ]
    },
    {
      link: GITHUB_HYSTAX_K8S_COST_METRICS_COLLECTOR,
      usages: ["Cloud Accounts -> Add -> Kubernetes"]
    },
    {
      link: GITHUB_HYSTAX_EXTRACT_LINKED_REPORTS,
      usages: ["Cloud Accounts -> Add -> AWS Linked"]
    },
    {
      link: DOCS_HYSTAX_CLUSTERS,
      usages: ["Cluster types page"]
    },
    {
      link: DOCS_HYSTAX_CLEANUP_SCRIPTS,
      usages: ["Recommendations -> Cleanup scripts button -> Tooltip"]
    }
  ]
};

const getTableData = () =>
  Object.entries(linksDefinition)
    .map(([groupName, links]) => {
      return [
        {
          link: "",
          name: groupName,
          divider: true
        },
        ...links
      ];
    })
    .flat();

export const basic = () => {
  const columns = [
    {
      Header: "Link",
      accessor: "link",
      disableSortBy: true,
      Cell: ({ row: { original } }) =>
        original.divider ? (
          <strong>{original.name}</strong>
        ) : (
          <div style={{ paddingLeft: "16px" }}>
            <Link href={original.link} target="_blank" rel="noopener">
              {original.link}
            </Link>
          </div>
        )
    },
    {
      Header: "Usage",
      accessor: "usages",
      disableSortBy: true,
      Cell: ({ row: { original } }) =>
        !isEmpty(original.usages) && (
          <ul>
            {original.usages.map((usage) => (
              <li>{usage}</li>
            ))}
          </ul>
        )
    }
  ];

  return (
    <WrapperCard>
      <TableUseMemoWrapper data={getTableData()} columns={columns} />
    </WrapperCard>
  );
};
