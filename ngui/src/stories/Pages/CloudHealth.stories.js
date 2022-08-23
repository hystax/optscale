import React from "react";
import CloudHealth from "components/CloudHealth";
import { object } from "@storybook/addon-knobs";
import { KINDS } from "stories";

export default {
  title: `${KINDS.PAGES}/CloudHealth`
};

export const cloudHealth = () => (
  <CloudHealth
    isLoading={false}
    data={{
      best_overall_region: "us-west-2",
      runner_up_region: "us-east-1",
      cheapest_top_five_region: "us-west-2",
      best_az: "us-west-2c",
      best_az_for_spot: "us-west-2c",
      max_score: 10,
      region_scores: [
        object("westcentralus", {
          region: "westcentralus",
          cloud_type: "azure_cnr",
          overall: 5.4,
          proximity: 0,
          network_latency: 9.5,
          price: 5.8,
          capacity_avg: 8,
          capacity_scores: {
            "westcentralus-1": 8
          },
          performance_avg: 10,
          performance_scores: {
            "westcentralus-1": 10
          }
        }),
        object("uaecentral", {
          region: "uaecentral",
          cloud_type: "azure_cnr",
          overall: 3.9,
          proximity: 0,
          network_latency: 3.7,
          price: 3.8,
          capacity_avg: 10,
          capacity_scores: {
            "uaecentral-1": 10
          },
          performance_avg: 10,
          performance_scores: {
            "uaecentral-1": 10
          }
        }),
        object("us-east-1", {
          region: "us-east-1",
          cloud_type: "aws_cnr",
          overall: 9.2,
          proximity: 9.4,
          network_latency: 8.4,
          price: 10,
          capacity_avg: 9,
          capacity_scores: {
            "us-east-1e": 9,
            "us-east-1f": 8,
            "us-east-1b": 10,
            "us-east-1d": 8,
            "us-east-1c": 10,
            "us-east-1a": 9
          },
          performance_avg: 8.5,
          performance_scores: {
            "us-east-1e": 9,
            "us-east-1f": 8,
            "us-east-1b": 10,
            "us-east-1d": 9,
            "us-east-1c": 8,
            "us-east-1a": 7
          }
        }),
        object("us-west-2", {
          region: "us-west-2",
          cloud_type: "aws_cnr",
          overall: 9.6,
          proximity: 10,
          network_latency: 10,
          price: 10,
          capacity_avg: 8.2,
          capacity_scores: {
            "us-west-2d": 8,
            "us-west-2c": 8,
            "us-west-2b": 8,
            "us-west-2a": 9
          },
          performance_avg: 8,
          performance_scores: {
            "us-west-2d": 6,
            "us-west-2c": 9,
            "us-west-2b": 9,
            "us-west-2a": 8
          }
        })
      ]
    }}
  />
);
