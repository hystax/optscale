class AwsTemplates:
    @staticmethod
    def get_data_export_template(name, bucket, prefix, region):
        return {
            'DataQuery': {
                'QueryStatement':
                    'SELECT '
                    'bill_bill_type, bill_billing_entity, bill_billing_period_end_date,'
                    'bill_billing_period_start_date, bill_invoice_id, bill_invoicing_entity, '
                    'bill_payer_account_id, bill_payer_account_name, cost_category, discount, '
                    'discount_bundled_discount, discount_total_discount, identity_line_item_id, '
                    'identity_time_interval, line_item_availability_zone, line_item_blended_cost, '
                    'line_item_blended_rate, line_item_currency_code, line_item_legal_entity, '
                    'line_item_line_item_description, line_item_line_item_type, line_item_net_unblended_cost, '
                    'line_item_net_unblended_rate, line_item_normalization_factor, line_item_normalized_usage_amount, '
                    'line_item_operation, line_item_product_code, line_item_resource_id, line_item_tax_type, '
                    'line_item_unblended_cost, line_item_unblended_rate, line_item_usage_account_id, '
                    'line_item_usage_account_name, line_item_usage_amount, line_item_usage_end_date, '
                    'line_item_usage_start_date, line_item_usage_type, pricing_currency, pricing_lease_contract_length, '
                    'pricing_offering_class, pricing_public_on_demand_cost, pricing_public_on_demand_rate, '
                    'pricing_purchase_option, pricing_rate_code, pricing_rate_id, pricing_term, pricing_unit, '
                    'product, product_comment, product_fee_code, product_fee_description, product_from_location, '
                    'product_from_location_type, product_from_region_code, product_instance_family, product_instance_type, '
                    'product_instancesku, product_location, product_location_type, product_operation, product_pricing_unit, '
                    'product_product_family, product_region_code, product_servicecode, product_sku, product_to_location, '
                    'product_to_location_type, product_to_region_code, product_usagetype, '
                    'reservation_amortized_upfront_cost_for_usage, reservation_amortized_upfront_fee_for_billing_period, '
                    'reservation_availability_zone, reservation_effective_cost, reservation_end_time, '
                    'reservation_modification_status, reservation_net_amortized_upfront_cost_for_usage, '
                    'reservation_net_amortized_upfront_fee_for_billing_period, reservation_net_effective_cost, '
                    'reservation_net_recurring_fee_for_usage, reservation_net_unused_amortized_upfront_fee_for_billing_period, '
                    'reservation_net_unused_recurring_fee, reservation_net_upfront_value, reservation_normalized_units_per_reservation, '
                    'reservation_number_of_reservations, reservation_recurring_fee_for_usage, reservation_reservation_a_r_n, '
                    'reservation_start_time, reservation_subscription_id, reservation_total_reserved_normalized_units, '
                    'reservation_total_reserved_units, reservation_units_per_reservation, '
                    'reservation_unused_amortized_upfront_fee_for_billing_period, reservation_unused_normalized_unit_quantity, '
                    'reservation_unused_quantity, reservation_unused_recurring_fee, reservation_upfront_value, resource_tags, '
                    'savings_plan_amortized_upfront_commitment_for_billing_period, savings_plan_end_time, '
                    'savings_plan_instance_type_family, savings_plan_net_amortized_upfront_commitment_for_billing_period, '
                    'savings_plan_net_recurring_commitment_for_billing_period, savings_plan_net_savings_plan_effective_cost, '
                    'savings_plan_offering_type, savings_plan_payment_option, savings_plan_purchase_term, '
                    'savings_plan_recurring_commitment_for_billing_period, savings_plan_region, savings_plan_savings_plan_a_r_n, '
                    'savings_plan_savings_plan_effective_cost, savings_plan_savings_plan_rate, savings_plan_start_time, '
                    'savings_plan_total_commitment_to_date, savings_plan_used_commitment '
                    'FROM COST_AND_USAGE_REPORT',
                'TableConfigurations': {
                    'COST_AND_USAGE_REPORT': {
                        "INCLUDE_MANUAL_DISCOUNT_COMPATIBILITY": "FALSE",
                        "INCLUDE_RESOURCES": "TRUE",
                        "INCLUDE_SPLIT_COST_ALLOCATION_DATA": "TRUE",
                        "TIME_GRANULARITY": "DAILY"
                    }
                }
            },
            'Description': 'Optscale data export',
            'DestinationConfigurations': {
                'S3Destination': {
                    'S3Bucket': bucket,
                    'S3OutputConfigurations': {
                        'Compression': 'GZIP',
                        'Format': 'TEXT_OR_CSV',
                        'OutputType': 'CUSTOM',
                        'Overwrite': 'OVERWRITE_REPORT'
                    },
                    'S3Prefix': prefix,
                    'S3Region': region,
                }
            },
            'Name': name,
            'RefreshCadence': {
                'Frequency': 'SYNCHRONOUS'
            }
        }

    @staticmethod
    def get_bucket_policy(bucket_name, account_id):
        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "EnableAWSDataExportsToWriteToS3AndCheckPolicy",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": [
                            "billingreports.amazonaws.com",
                            "bcm-data-exports.amazonaws.com"
                        ]
                    },
                    "Action": [
                        "s3:PutObject",
                        "s3:GetBucketPolicy"
                    ],
                    "Resource": [
                        "arn:aws:s3:::{}/*".format(bucket_name),
                        "arn:aws:s3:::{}".format(bucket_name)
                    ],
                    "Condition": {
                        "StringLike": {
                            "aws:SourceAccount": "{}".format(account_id),
                            "aws:SourceArn": [
                                "arn:aws:cur:us-east-1:{}:definition/*".format(account_id),
                                "arn:aws:bcm-data-exports:us-east-1:{}:export/*".format(account_id)
                            ]
                        }
                    }
                }
            ]
        }
