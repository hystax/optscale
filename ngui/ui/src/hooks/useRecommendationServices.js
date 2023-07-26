import { AWS_CNR, AZURE_CNR, ALIBABA_CNR, GCP_CNR, NEBIUS } from "utils/constants";
import { useIsNebiusConnectionEnabled } from "./useIsNebiusConnectionEnabled";

export const ALL_SERVICES = "all";

export const ALIBABA_ECS = "alibabaEcs";
export const ALIBABA_ECS_VPC = "alibabaEcsVpc";
export const ALIBABA_EBS = "alibabaEbs";
export const ALIBABA_RDS = "alibabaRds";

export const AWS_IAM = "awsIam";
export const AWS_EC2 = "awsEc2";
export const AWS_EC2_EBS = "awsEc2Ebs";
export const AWS_EC2_VPC = "awsEc2Vpc";
export const AWS_RDS = "awsRds";
export const AWS_KINESIS = "awsKinesis";
export const AWS_S3 = "awsS3";

export const AZURE_COMPUTE = "azureCompute";
export const AZURE_NETWORK = "azureNetwork";

export const GCP_COMPUTE_ENGINE = "gcpComputeEngine";

export const NEBIUS_SERVICE = "nebius";

const ALIBABA_SERVICES = Object.freeze({
  [ALIBABA_ECS]: {
    type: ALIBABA_CNR,
    name: "services.ecs"
  },
  [ALIBABA_ECS_VPC]: {
    type: ALIBABA_CNR,
    name: "services.ecs::vpc"
  },
  [ALIBABA_EBS]: {
    type: ALIBABA_CNR,
    name: "services.ebs"
  },
  [ALIBABA_RDS]: {
    type: ALIBABA_CNR,
    name: "services.rds"
  }
});

const AWS_SERVICES = Object.freeze({
  [AWS_IAM]: {
    type: AWS_CNR,
    name: "services.iam"
  },
  [AWS_EC2]: {
    type: AWS_CNR,
    name: "services.ec2"
  },
  [AWS_EC2_EBS]: {
    type: AWS_CNR,
    name: "services.ec2::ebs"
  },
  [AWS_EC2_VPC]: {
    type: AWS_CNR,
    name: "services.ec2::vpc"
  },
  [AWS_RDS]: {
    type: AWS_CNR,
    name: "services.rds"
  },
  [AWS_KINESIS]: {
    type: AWS_CNR,
    name: "services.kinesis"
  },
  [AWS_S3]: {
    type: AWS_CNR,
    name: "services.s3"
  }
});

const AZURE_SERVICES = Object.freeze({
  [AZURE_COMPUTE]: {
    type: AZURE_CNR,
    name: "services.compute"
  },
  [AZURE_NETWORK]: {
    type: AZURE_CNR,
    name: "services.network"
  }
});

const GCP_SERVICES = Object.freeze({
  [GCP_COMPUTE_ENGINE]: {
    type: GCP_CNR,
    name: "services.computeEngine"
  }
});

const NEBIUS_SERVICES = Object.freeze({
  [NEBIUS_SERVICE]: {
    type: NEBIUS,
    name: "services.nebius"
  }
});

export const useRecommendationServices = () => {
  const isNebiusConnectionEnabled = useIsNebiusConnectionEnabled();

  return {
    [ALL_SERVICES]: {
      name: ALL_SERVICES
    },
    ...ALIBABA_SERVICES,
    ...AWS_SERVICES,
    ...AZURE_SERVICES,
    ...GCP_SERVICES,
    ...(isNebiusConnectionEnabled ? NEBIUS_SERVICES : {})
  };
};
