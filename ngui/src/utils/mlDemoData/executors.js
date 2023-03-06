const executors = [
  {
    /**
     * custom params to search executors for applications and runs
     */
    applicationIds: ["1e0815a2-72d2-418b-afad-bedc99a5e9d2"],
    runIds: ["66ad45dc-025f-4204-8261-e27383b50fcb", "76ad45dc-025f-4204-8261-e27383b50fcb"],

    instance_type: "t2.medium",
    instance_region: "us-east-1",
    discovered: true,
    resource: {
      _id: "4a5291c5-94a3-41fe-a48f-8bbf6ce037a4",
      cloud_account_id: "6a7c3077-9f46-40d9-8630-9658b3c05ba8",
      cloud_resource_id: "i-0729a34d6f5b91f83-x2",
      first_seen: 1674739172,
      last_seen: 1674805862,
      name: "sunflower-eu-fra",
      total_cost: 412.6214,
      meta: {
        flavor: "t2.medium"
      },
      region: "us-east-1",
      cloud_account: {
        name: "AWS HQ",
        type: "aws_cnr",
        id: "f420726e-2a4e-4a7c-8594-b4dd4caeb47e"
      }
    }
  },
  {
    /**
     * custom params to search executors for applications and runs
     */
    applicationIds: ["1e0815a2-72d2-418b-afad-bedc99a5e9d2"],
    runIds: ["86ad45dc-025f-4204-8261-e27383b50fcb"],

    instance_type: "Standard_D16ds_v5",
    instance_region: "Germany West Central",
    discovered: true,
    resource: {
      _id: "d18c4176-e35e-400a-808f-ae90a26129cf",
      cloud_account_id: "12978ba9-cc9c-42b2-b717-02fc0d1120bc",
      cloud_resource_id:
        "/subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourcegroups/orchid-engineering/providers/microsoft.compute/virtualmachines/orchid-staging",
      first_seen: 1674739172,
      last_seen: 1674805862,
      name: "orchid-staging",
      total_cost: 512.621,
      meta: {
        flavor: "Standard_D16ds_v5"
      },
      region: "Germany West Central",
      cloud_account: {
        name: "Dev environment",
        type: "azure_cnr",
        id: "12978ba9-cc9c-42b2-b717-02fc0d1120bc"
      }
    }
  }
];

export { executors };
