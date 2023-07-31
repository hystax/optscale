import { ML_RUNSET_ABORT_CONDITION_TYPES } from "utils/constants";
import { AWS_DEV, AWS_ML, AWS_QA } from "./dataSources";

const HOURS = 60 * 60;
const MINUTES = 60;

export const awsGpuInstancesRunsets = [
  {
    id: "0e49ebaf-0993-4116-bb4f-4257e877c572",
    number: 3,
    name: "gentle_sky",
    created_at: 1674741319,
    owner: {
      id: "Jack White",
      name: "Jack White"
    },
    duration: 8 * HOURS + 15 * MINUTES,
    configurations_tried: 8,
    expenses: 1200,
    commands:
      "sudo pip install torchvision==0.13.0\nwget https://bucket.s3.eu-central-1.amazonaws.com/model.py\npython3 model.py",
    template_id: "826f8381-9a12-4854-8274-9ca421b19856",
    application_id: "1e0815a2-72d2-418b-afad-bedc99a5e9d2",
    runs: [
      "c362e72e-61a7-49e8-8c7e-71093f55c7b4",
      "fa8a5233-582b-41c6-a321-9c831675cdcf",
      "a362e72e-61a7-49e8-8c7e-71093f55c7b4",
      "66ad45dc-025f-4204-8261-e27383b50fcb",
      "76ad45dc-025f-4204-8261-e27383b50fcb",
      "86ad45dc-025f-4204-8261-e27383b50fcb"
    ],
    region: { id: "us-east-1", name: "us-east-1", cloud_type: "aws_cnr" },
    cloud_account: AWS_ML,
    instance_size: {
      type: "t3a",
      name: "t3.xlarge",
      cloud_type: "aws_cnr"
    },
    max_parallel_runs: 14,
    hyperparameters: {
      MODEL_URL: [
        "https://raw.githubusercontent.com/me/my-awesome-model/train_sample_1.py",
        "https://raw.githubusercontent.com/me/my-awesome-model/train_sample_2.py"
      ].join(", "),
      DATASET_URL: [
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-a.gz",
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-b.gz",
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-c.gz"
      ].join(", "),
      LEARNING_RATE: ["0.001", "0.01", "0.05", "0.005"].join(", ")
    },
    destroy_conditions: {
      [ML_RUNSET_ABORT_CONDITION_TYPES.MAX_BUDGET]: 20,
      [ML_RUNSET_ABORT_CONDITION_TYPES.MAX_DURATION]: 3,
      [ML_RUNSET_ABORT_CONDITION_TYPES.REACHED_GOALS]: true
    },
    spot_settings: { tries: 5 }
  },
  {
    id: "d4264062-969c-4851-9453-89da80881521",
    number: 2,
    name: "wandering_moon",
    created_at: 1674741119,
    template_id: "826f8381-9a12-4854-8274-9ca421b19856",
    owner: {
      id: "Evelyn Grey",
      name: "Evelyn Grey"
    },
    state: "running",
    duration: 6 * HOURS + 53 * MINUTES,
    configurations_tried: 4,
    expenses: 39,
    application_id: "1e0815a2-72d2-418b-afad-bedc99a5e9d2",
    runs: ["380abb2f-dff4-417c-bcf4-c696436e93aa", "176a9c18-a347-4d10-8992-2ca96cc2afc2"],
    region: { id: "us-east-1", name: "us-east-1", cloud_type: "aws_cnr" },
    cloud_account: AWS_QA,
    instance_sizes: {
      type: "t3a",
      name: "t3a.xlarge",
      cloud_type: "aws_cnr"
    },
    commands:
      "sudo pip install torchvision==0.13.0\nwget https://bucket.s3.eu-central-1.amazonaws.com/model.py\npython3 model.py",
    hyperparameters: {
      MODEL_URL: [
        "https://raw.githubusercontent.com/me/my-awesome-model/train_sample_1.py",
        "https://raw.githubusercontent.com/me/my-awesome-model/train_sample_2.py"
      ].join(", "),
      DATASET_URL: [
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-a.gz",
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-b.gz",
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-c.gz"
      ].join(", "),
      LEARNING_RATE: ["0.001", "0.01", "0.05", "0.005"].join(", ")
    },
    max_parallel_runs: 14,
    hyperparams: {
      DATASET_URL: [
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-a.gz",
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-b.gz",
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-c.gz"
      ].join(", "),
      MODEL_URL: [
        "https://raw.githubusercontent.com/me/my-awesome-model/train_sample_1.py",
        "https://raw.githubusercontent.com/me/my-awesome-model/train_sample_2.py"
      ].join(", "),
      LEARNING_RATE: ["0.001", "0.01", "0.05", "0.005"].join(", ")
    },
    destroy_conditions: { max_budget: 20, max_duration: 300 },
    spot_settings: { tries: 2 }
  },
  {
    id: "fc3dd9a8-ed5b-462f-8290-5ac66272518c",
    number: 1,
    name: "blooming_meadow",
    created_at: 1674740719,
    state: "running",
    template_id: "826f8381-9a12-4854-8274-9ca421b19856",
    started_by: "Charlie Fisher",
    owner: {
      id: "Charlie Fisher",
      name: "Charlie Fisher"
    },
    duration: 12 * HOURS + 42 * MINUTES,
    configurations_tried: 7,
    expenses: 98,
    application_id: "1e0815a2-72d2-418b-afad-bedc99a5e9d2",
    runs: ["58ffb238-4691-4a92-88d5-17d0994c1fde"],
    region: { id: "us-east-1", name: "us-east-1", cloud_type: "aws_cnr" },
    cloud_account: AWS_DEV,
    instance_size: {
      name: "t3a.xlarge",
      type: "t3a",
      cloud_type: "aws_cnr"
    },
    max_parallel_runs: 14,
    commands:
      "sudo pip install torchvision==0.13.0\nwget https://bucket.s3.eu-central-1.amazonaws.com/model.py\npython3 model.py",
    hyperparameters: {
      MODEL_URL: [
        "https://raw.githubusercontent.com/me/my-awesome-model/train_sample_1.py",
        "https://raw.githubusercontent.com/me/my-awesome-model/train_sample_2.py"
      ].join(", "),
      DATASET_URL: [
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-a.gz",
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-b.gz",
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-c.gz"
      ].join(", "),
      LEARNING_RATE: ["0.001", "0.01", "0.05", "0.005"].join(", ")
    },
    destroy_conditions: { max_budget: 20, max_duration: 300 },
    spot_settings: { tries: 3 }
  }
];

export const activationFunctionsDatasetsRunsets = [
  {
    id: "ee57963c-e678-4d28-afee-612ef5ba3a4b",
    number: 1,
    name: "solar_gorilla",
    created_at: 1674741319,
    template_id: "ac2adbf7-0793-475d-932c-6a899ceb9c30",
    is_running: false,
    started_by: "Jack White",
    duration: 8 * HOURS + 15 * MINUTES,
    configurations_tried: 8,
    expenses: 1200,
    application_id: "2e0815a2-72d2-418b-afad-bedc99a5e9d2",
    runs: ["9bfaaee6-7280-426c-90f8-89c01c08d2d3", "94cde6d1-10df-4f05-afc5-89d98332e759"],
    region: { id: "us-east-1", name: "us-east-1", cloud_type: "aws_cnr" },
    cloud_account: AWS_DEV,
    instance_size: {
      name: "p4d.24xlarge",
      type: "p4",
      cloud_type: "aws_cnr"
    },
    max_parallel_runs: 14,
    commands:
      "sudo pip install torchvision==0.13.0\nwget https://bucket.s3.eu-central-1.amazonaws.com/model.py\npython3 model.py",
    hyperparameters: {
      MODEL_URL: [
        "https://raw.githubusercontent.com/me/my-awesome-model/train_sample_1.py",
        "https://raw.githubusercontent.com/me/my-awesome-model/train_sample_2.py"
      ].join(", "),
      DATASET_URL: [
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-a.gz",
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-b.gz",
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-c.gz"
      ].join(", "),
      LEARNING_RATE: ["0.001", "0.01", "0.05", "0.005"].join(", ")
    },
    hyperparams: {
      DATASET_URL: [
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-a.gz",
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-b.gz",
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-c.gz"
      ].join(", "),
      MODEL_URL: [
        "https://raw.githubusercontent.com/me/my-awesome-model/train_sample_1.py",
        "https://raw.githubusercontent.com/me/my-awesome-model/train_sample_2.py"
      ].join(", "),
      LEARNING_RATE: ["0.001", "0.01", "0.05", "0.005"].join(", ")
    },
    destroy_conditions: { max_budget: 20, max_duration: 300 },
    spot_settings: { tries: 3 }
  }
];

export const priceSpeedBalanceRunsets = [
  {
    id: "f253907d-0ae1-4a37-b441-ea060c4a9f80",
    number: 1,
    name: "thunder_dragon",
    created_at: 1674741319,
    template_id: "5c7b5a5a-866e-4916-adc4-b56a1f1adb0a",
    started_by: "Jack White",
    duration: 8 * HOURS + 15 * MINUTES,
    configurations_tried: 8,
    is_running: false,
    expenses: 1200,
    application_id: "3e0815a2-72d2-418b-afad-bedc99a5e9d2",
    runs: ["c67054fe-ebfe-4a90-9a8b-3bda0561f588", "e581d2fc-aa78-441e-930f-994630bac526"],
    region: { id: "us-east-1", name: "us-east-1", cloud_type: "aws_cnr" },
    cloud_account: AWS_DEV,
    instance_size: {
      type: "g4ad",
      name: "g4ad.xlarge",
      cloud_type: "aws_cnr"
    },
    max_parallel_runs: 14,
    commands:
      "sudo pip install torchvision==0.13.0\nwget https://bucket.s3.eu-central-1.amazonaws.com/model.py\npython3 model.py",
    hyperparameters: {
      MODEL_URL: [
        "https://raw.githubusercontent.com/me/my-awesome-model/train_sample_1.py",
        "https://raw.githubusercontent.com/me/my-awesome-model/train_sample_2.py"
      ].join(", "),
      DATASET_URL: [
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-a.gz",
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-b.gz",
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-c.gz"
      ].join(", "),
      LEARNING_RATE: ["0.001", "0.01", "0.05", "0.005"].join(", ")
    },
    hyperparams: {
      DATASET_URL: [
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-a.gz",
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-b.gz",
        "https://raw.githubusercontent.com/me/my-perfect-datasets/data-c.gz"
      ],
      MODEL_URL: [
        "https://raw.githubusercontent.com/me/my-awesome-model/train_sample_1.py",
        "https://raw.githubusercontent.com/me/my-awesome-model/train_sample_2.py"
      ],
      LEARNING_RATE: ["0.001", "0.01", "0.05", "0.005"]
    },
    destroy_conditions: { max_budget: 20, max_duration: 300 },
    spot_settings: { tries: 4 }
  }
];

const runsets = [...awsGpuInstancesRunsets, ...activationFunctionsDatasetsRunsets, ...priceSpeedBalanceRunsets];

export { runsets };
