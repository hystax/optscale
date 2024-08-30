import enum


class Err(enum.Enum):
    OEXXXX = [
        "Mock error",
        "-",
        [],
        []
    ]
    OE0002 = [
        "%s %s not found",
        ["Entity type", "UUID"],
        ["Rule", "34b44313-fada-4605-b809-7f31f65db037"]
    ]
    OE0003 = [
        "Database error: %s",
        ["Traceback error from DB"],
        ["Traceback (most recent call last): Exception: unexpected"]
    ]
    OE0004 = [
        "Type error: %s",
        ["Traceback when try to set wrong value for enum type"],
        ["'unexpected' is not a valid ConditionTypes"]
    ]
    OE0005 = [
        "%s %s doesn't exist",
        ["Field name", "provided value"],
        ["approver_id", "34b44313-fada-4605-b809-7f31f65db037"]
    ]
    OE0128 = [
        "Invalid model type: %s",
        ["Value of provided db type"],
        ["postgres"]
    ]
    OE0149 = [
        "%s with name \"%s\" already exists",
        ["Entity type", "provided name"],
        ["Partner", "Development"]
    ]
    OE0166 = [
        "Action \"%s\" is not supported",
        ["Provided unsupported action"],
        ["cancel"]
    ]
    OE0173 = [
        "Type or/and uuid is missing",
        [],
        []
    ]
    OE0174 = [
        "Type %s is invalid",
        ["Provided type"],
        ["rule"]
    ]
    OE0177 = [
        "Non unique parameters in get request",
        [],
        []
    ]
    OE0211 = [
        "Parameter \"%s\" is immutable",
        ["Parameter name"],
        ["created_at"]
    ]
    OE0212 = [
        "Unexpected parameters: %s",
        ["Comma separated list of unexpected field names"],
        ["pool_id, user_id"]
    ]
    OE0214 = [
        "%s should be a string",
        ["Field name"],
        ["name"]
    ]
    OE0215 = [
        "%s should contain %s characters",
        ["Filed name", "max count of chars or range"],
        ["name", "max 255"]
    ]
    OE0216 = [
        "%s is not provided",
        ["Field name"],
        ["business_unit_id"]
    ]
    OE0217 = [
        "Invalid %s",
        ["Field name"],
        ['filter_by']
    ]
    OE0218 = [
        "%s \"%s\" has incorrect format",
        ["Field name", "provided field value"],
        ["email", "wrong_email@com"]
    ]
    OE0219 = [
        "%s should be a string with valid JSON",
        ["Field name"],
        ["meta_info"]
    ]
    OE0223 = [
        "%s should be integer",
        ["Filed name"],
        ["limit"]
    ]
    OE0224 = [
        "Value of \"%s\" should be between %s and %s",
        ["Filed name", "min value", "max value"],
        ["limit", 0, 2147483647]
    ]
    OE0225 = [
        "%s is not valid fqdn or ip",
        ["Field name"],
        ["Address"]
    ]
    OE0226 = [
        "%s should be True or False",
        ["Field name"],
        ["Active"]
    ]
    OE0233 = [
        "Incorrect request body received",
        [],
        []
    ]
    OE0234 = [
        "Forbidden",
        [],
        []
    ]
    OE0235 = [
        "Unauthorized",
        [],
        []
    ]
    OE0236 = [
        "Bad secret",
        [],
        []
    ]
    OE0237 = [
        "This resource requires authorization",
        [],
        []
    ]
    OE0239 = [
        "Unable to modify upper level rule",
        [],
        []
    ]
    OE0240 = [
        "Missing is_inherited parameter",
        [],
        []
    ]
    OE0245 = [
        "%s method not allowed",
        ["Method name"],
        ["POST"]
    ]
    OE0257 = [
        "Not found",
        [],
        []
    ]
    OE0287 = [
        "Bad request: %s",
        ["Traceback"],
        ["'unexpected' is not a valid ConditionTypes"]
    ]
    OE0344 = [
        "%s should be a dictionary",
        ["Field name"],
        ["optscale_params"]
    ]
    OE0356 = [
        "%s should be a valid IPv4",
        ["Field name"],
        ["Address"]
    ]
    OE0371 = [
        "Unable to configure billing report: %s",
        ["Traceback"],
        ["Not enough permissions to configure report: AccessDenied"]
    ]
    OE0373 = [
        "User with email %s is not assigned to any organization",
        ["Users email"],
        ["user1@domain.com"]
    ]
    OE0374 = [
        "Duplicated scope_id for email %s",
        ["Users email"],
        ["user1@domain.com"]
    ]
    OE0378 = [
        "Current user is not a member in provided organization",
        [],
        []
    ]
    OE0379 = [
        "Target owner %s doesn't have enough permissions for target pool",
        ["Owner name"],
        ["John Doe"]
    ]
    OE0380 = [
        "Current user doesn't have enough permissions for target pool",
        [],
        []
    ]
    OE0381 = [
        "Current user doesn't have enough permissions for target cloud resource %s",
        ["Cloud resource id"],
        ["i-095a8e515029f5153"]
    ]
    OE0382 = [
        "Employee for user %s already exists in organization %s",
        ["User uuid", "Organization uuid"],
        ["5c9c947b-8833-474d-a2f1-c99758196c76",
         "4dd93c56-0fa9-43ff-965c-0b83806b9dc2"]
    ]
    OE0383 = [
        "Invite yourself is forbidden",
        [],
        []
    ]
    OE0384 = [
        "Invalid resource type: %s",
        ["Provided resource type"],
        ["region"]
    ]
    OE0385 = [
        "%s should be a list",
        ["Field name"],
        ["resources"]
    ]
    OE0386 = [
        "Invalid contacts: %s",
        ["Comma separated list of employee ids"],
        ["84cba2e0-aeb9-412e-afc6-8044089c8071, 5b87b63a-b2a9-43b5-a074-5b651a9248b0"]
    ]
    OE0388 = [
        "Invalid regions %s for resources discovery",
        ["Comma separated list of invalid regions"],
        ["us-west-8, ru-msk-0"]
    ]
    OE0389 = [
        "Invalid sort condition %s for type %s, allowed types %s",
        ["Provided value", "Resource type",
         "Comma separated list of allowed values"],
        ["size", "instance", "name, flavor"]
    ]
    OE0390 = [
        "Invalid filter name %s",
        ["Comma separated list of invalid filters"],
        ["size, ttl"]
    ]
    OE0391 = [
        "Current user can't accept/decline this assignment request",
        [],
        []
    ]
    OE0392 = [
        "Filters should be a dict",
        [],
        []
    ]
    OE0393 = [
        "Value for filter %s should be a list",
        ["Filter key"],
        ["flavor"]
    ]
    OE0394 = [
        "Sort condition must be a dict",
        [],
        []
    ]
    OE0395 = [
        "Sort condition should be one",
        [],
        []
    ]
    OE0397 = [
        "Resource type is required",
        [],
        []
    ]
    OE0398 = [
        "%s should be a json string",
        ["Invalid argument name"],
        ["filters"]
    ]
    OE0399 = [
        "Sort order should be asc or desc",
        [],
        []
    ]
    OE0400 = [
        "Tasks API works only for organization",
        [],
        []
    ]
    OE0402 = [
        "Cloud account for this account already exist",
        [],
        []
    ]
    OE0404 = [
        "Cloud account %s already exists for organization %s",
        ["Cloud account name", "organization uuid"],
        ["Aws HQ", "d3706242-47a9-4e55-b7ab-b9f58fa9ec31"]
    ]
    OE0407 = [
        "Child pool limit value exceeds parent limit",
        [],
        []
    ]
    OE0410 = [
        "Method %s not supported",
        ["Provided unsupported full method name"],
        ["ec2.describe_instance_regions"]
    ]
    OE0411 = [
        "%s %s has not deleted children",
        ["Entity type", "Entity name"],
        ["Parent", "dev"]
    ]
    OE0412 = [
        "Resources with ids %s were not found",
        ["Comma separated list of cloud resource ids"],
        ["i-067a8e515029f5153, i-045a8e515029f5153"]
    ]
    OE0413 = [
        "Cloud call failed: %s",
        ["Traceback"],
        ["Traceback (most recent call last): Exception: unexpected"]
    ]
    OE0414 = [
        "Parent pool limit with value %s and id %s is less than the limit of the child pools",
        ["Pool limit value", "pool uuid"],
        [450, "66c0780f-f6b3-49a3-839e-093b24f9396d"]
    ]
    OE0415 = [
        "Requested creation time is in future",
        [],
        []
    ]
    OE0416 = [
        "%s should not contain only whitespaces",
        ["Filed name"],
        ["name"]
    ]
    OE0418 = [
        "%s is not an organization",
        ["business unit id"],
        ["bddd5946-25cc-4f39-a694-e7060eec91a8"]
    ]
    OE0419 = [
        "Current user can't cancel this assignment request",
        [],
        []
    ]
    OE0424 = [
        "Can't create assignment request for the same user",
        [],
        []
    ]
    OE0425 = [
        "Behavior %s is not supported",
        ["Provided behavior value"],
        ["dont_skip_existing"]
    ]
    OE0426 = [
        "Request body should be a dictionary",
        [],
        []
    ]
    OE0427 = [
        "Current_only and exclude_myself could not be true at the same time",
        [],
        []
    ]
    OE0428 = [
        "Pool_id or employee_id should be provided",
        [],
        []
    ]
    OE0430 = [
        "Unsupported condition type %s",
        ["Provided unsupported condition type"],
        ["organization_is"]
    ]
    OE0431 = [
        "Rule with name \"%s\" is already exist",
        ["Rule name"],
        ["QA instances"]
    ]
    OE0433 = [
        "Cloud error: %s",
        ["Traceback"],
        ["Traceback (most recent call last): Exception: unexpected"]
    ]
    OE0434 = [
        'Uploading reports is not available for clouds with type %s',
        ["Cloud type"],
        ["aws_cnr"]
    ]
    OE0435 = [
        "Service call error: %s",
        ["Traceback"],
        ["Traceback (most recent call last): Exception: unexpected"]
    ]
    OE0436 = [
        "%s type is not supported",
        ["provided unsupported cloud type"],
        ["mail_cloud"]
    ]
    OE0437 = [
        "Can’t connect the %s subscription: %s",
        ["cloud_type", "Error message"],
        ["Azure", "Subscription 628bd278-b8ef-4250-9ac9-4ad6a29f572b does not have usage "
                  "data yet or doesn\'t support UsageDetails API"]
    ]
    OE0438 = [
        "Wasn't able to discover resources. Timeout is reached",
        [],
        []
    ]
    OE0444 = [
        "Account is not supported: %s",
        ["Error message"],
        ["currency \"RUB\" is not supported"]
    ]
    OE0441 = [
        'Constraint with type "%s" already exists for resource "%s"',
        ['constraint_type', 'constraint_id'],
        ["TTL", "d3706242-47a9-4e55-b7ab-b9f58fa9ec31"]
    ]
    OE0443 = [
        'Resource %s is not active',
        ['resource_id'],
        ["c3706242-47a9-4e55-b7ab-b9f58fa9ec31"]
    ]
    OE0440 = [
        'Policy with type "%s" already exists for pool "%s"',
        ['policy_type', 'pool_id'],
        ['ttl', "a3706242-47a9-4e55-b7ab-b9f58fa9ec31"]
    ]
    OE0445 = [
        "Organization %s (%s) doesn't have any cloud accounts connected",
        ["organization_name", "organization_id"],
        ["Organization Hystax (e3706242-47a9-4e55-b7ab-b9f58fa9ec31) doesn't have "
         "any cloud accounts connected"]
    ]
    OE0446 = [
        '%s should be greater than %s',
        ['end_date', 'start_date'],
        ['end_date should be greater than start_date']
    ]
    OE0447 = [
        'Root pool can\'t be deleted',
        [],
        []
    ]
    OE0448 = [
        "Unable to discover for %s because of: %s",
        ['resource_type', 'Error message'],
        ["Unable to discover for instance because of: An error occurred (AccessDenied) "
         "when calling the ListBuckets operation: Access Denied"]
    ]
    OE0449 = [
        '%s of %s can\'t be changed',
        ['purpose', 'root pool'],
        ['purpose of root pool can\'t be changed']
    ]
    OE0450 = [
        "Failed to load Live Demo template",
        [],
        []
    ]
    OE0451 = [
        "Failed to generate Live Demo organization: %s",
        ['Error message'],
        ["Failed to generate Live Demo organization: Cannot add or update a child row"]
    ]
    OE0452 = [
        "Live Demo template missing",
        [],
        []
    ]
    OE0453 = [
        "Invalid cached value: %s",
        ["Provided cached value"],
        [False]
    ]
    OE0454 = [
        "%s %s does not belong to the organization",
        ["Pool", "c3706242-47a9-4e55-b7ab-b9f58fa9ec31"],
        ["Pool c3706242-47a9-4e55-b7ab-b9f58fa9ec31 is not belong to the "
         "organization"]
    ]
    OE0455 = [
        "Cloud connection error: %s",
        ["Error message"],
        ["Cloud connection error: Could not connect to cloud by subscription subscription_id: connection timed out."]
    ]
    OE0456 = [
        "Duplicate path parameters in the request body: %s",
        ["organization_id"],
        ["Duplicate path parameters in the request body: organization_id"]
    ]
    OE0457 = [
        "Unable to find policy for pool, please specify TTL",
        [],
        []
    ]
    OE0459 = [
        "The pool %s does not have default_owner_id",
        ["pool_id"],
        ["The pool c3706242-47a9-4e55-b7ab-b9f58fa9ec31 does not have default_owner_id"]
    ]
    OE0460 = [
        "Status should be active, dismissed or excluded",
        [],
        []
    ]
    OE0461 = [
        "%s can't be in past",
        ["Limit"],
        ["Limit can't be in past"]
    ]
    OE0462 = [
        'One of [%s] should be specified',
        ['slack_channel_id, employee_id'],
        ['One of [slack_channel_id, employee_id] should be specified']
    ]
    OE0463 = [
        "Cluster type %s already exists in organization %s",
        ["name", "organization_id"],
        ["Cluster type test already exists in organization c3706242-47a9-4e55-b7ab-b9f58fa9ec31"]
    ]
    OE0464 = [
        'Resource %s is a part of cluster',
        ['resource_id'],
        ["c3706242-47a9-4e55-b7ab-b9f58fa9ec31"]
    ]
    OE0465 = [
        "Can't activate/dismiss cluster optimization",
        [],
        []
    ]
    OE0466 = [
        "%s should be float",
        ["Field name"],
        ["cpu_hour"]
    ]
    OE0467 = [
        "Invalid cluster type id %s in resource type",
        ["cluster_type_id"],
        ["c3706242-47a9-4e55-b7ab-b9f58fa9ec31"]
    ]
    OE0468 = [
        "%s should be a date in format YYYYMMDD",
        ["date"],
        ["start_date should be a date in format YYYYMMDD"]
    ]
    OE0469 = [
        "Pool expense export for pool %s already exists",
        ["pool_id"],
        ["Pool expense export for pool c3706242-47a9-4e55-b7ab-b9f58fa9ec31 already exists"]
    ]
    OE0470 = [
        "The following %s filter values do not match any object: %s",
        ["filter", ["value1", "value2", "etc"]],
        ["The following owner_id filter values do not match any object: ['abcd', '1234']"]
    ]
    OE0471 = [
        "Not enough permissions to extend the pool %s (%s)",
        ["test", "7a4106a5-1a54-433c-ae8f-546cc40b9e1b"],
        ["Not enough permissions to extend the pool test (7a4106a5-1a54-433c-ae8f-546cc40b9e1b)"]
    ]
    OE0472 = [
        "%s %s has a removed associated %s %s",
        ["object_type", "id", "associated_object_type", "parent_id"],
        ["pool c3706242-47a9-4e55-b7ab-b9f58fa9ec31 has a removed associated "
         "organization c3706242-47a9-4e55-b7ab-b9f58fa9ec32"]
    ]
    OE0473 = [
        'Format %s is not allowed',
        ['Format name'],
        ['xls'],
    ]
    OE0474 = [
        "%s should be multiple of %s",
        ['param', 'value'],
        "interval should be multiple of 900",
    ]
    OE0475 = [
        'Invalid request. Parameters provider_id, flavor and hourly_price are all required',
        [],
        []
    ]
    OE0476 = [
        'Environment cloud account does not support recommendations',
        [],
        []
    ]
    OE0477 = [
        'Environment cloud account can\'t be deleted',
        [],
        []
    ]
    OE0478 = [
        "Current resource can't be shared, resource type is invalid for sharing %s",
        ["cloud_resource_id"],
        ["Current resource can't be shared, resource type is invalid for sharing i-095a8e515029f5153"],
    ]
    OE0479 = [
        "%s should be False",
        ["shareable"],
        ["shareable should be False"]
    ]
    OE0480 = [
        '%s %s is not shareable',
        ['Cluster', 'c3706242-47a9-4e55-b7ab-b9f58fa9ec33'],
        ['Cluster c3706242-47a9-4e55-b7ab-b9f58fa9ec33 is not shareable'],
    ]
    OE0481 = [
        'Clustered resource %s cannot have own shareable schedule booking',
        ['c3706242-47a9-4e55-b7ab-b9f58fa9ec33'],
        ['Clustered resource c3706242-47a9-4e55-b7ab-b9f58fa9ec33 cannot have own shareable schedule booking'],
    ]
    OE0482 = [
        'Shareable booking slot is already used. Select another one or '
        'release the existing before',
        [],
        [],
    ]
    OE0483 = [
        "Clusters are not supported",
        [],
        [],
    ]
    OE0484 = [
        'Deleting of shareable booking %s is not allowed',
        ['c3706242-47a9-4e55-b7ab-b9f58fa9ec33'],
        ['Deleting of shareable booking c3706242-47a9-4e55-b7ab-b9f58fa9ec33 is not allowed'],
    ]
    OE0488 = [
        'Environment resource %s cannot be not shareable',
        ['c3706242-47a9-4e55-b7ab-b9f58fa9ec33'],
        ['Environment resource c3706242-47a9-4e55-b7ab-b9f58fa9ec33 cannot be not shareable'],
    ]
    OE0485 = [
        'Calendar synchronization is unsupported',
        [],
        []
    ]
    OE0486 = [
        "Calendar synchronization not found for organization %s",
        ["organization id"],
        ["Calendar synchronization not found for organization 34b44313-fada-4605-b809-7f31f65db037"]
    ]
    OE0487 = [
        "Calendar %s already linked to organization %s",
        ["Calendar id", "organization id"],
        ["Calendar some_user@gmail.com already linked to organization d3706242-47a9-4e55-b7ab-b9f58fa9ec31"]
    ]
    OE0489 = [
        "Unable to create calendar event: %s",
        ["Reason"],
        ["Calendar not found"]
    ]
    OE0490 = [
        "Unable to list calendar events: %s",
        ["Reason"],
        ["Calendar not found"]
    ]
    OE0491 = [
        "Unable to modify calendar event: %s",
        ["Reason"],
        ["Calendar not found"]
    ]
    OE0492 = [
        "Unable to delete calendar event: %s",
        ["Reason"],
        ["Calendar not found"]
    ]
    OE0493 = [
        "Calendar validation failed: %s",
        ["Reason"],
        ["Calendar not found"]
    ]
    OE0494 = [
        'User %s already exists',
        ['email'],
        ['User resu@sure.com already exists']
    ]
    OE0495 = [
        'Creating a shareable booking in the past is not allowed',
        [],
        [],
    ]
    OE0496 = [
        "%s should not consist of only wildcards",
        ["Field name"],
        ["name_like"]
    ]
    OE0497 = [
        'Deleting of the last organization manager is not allowed.',
        [],
        [],
    ]
    OE0498 = [
        "Release of shareable booking %s is not allowed.",
        ['c3706242-47a9-4e55-b7ab-b9f58fa9ec33'],
        [
            'Release of shareable booking c3706242-47a9-4e55-b7ab-b9f58fa9ec33 is not allowed.']
    ]
    OE0499 = [
        "Incorrect resource type identity",
        [],
        []
    ]
    OE0500 = [
        '%s cannot be changed while organization has connected cloud accounts',
        ['field'],
        ['currency']
    ]
    OE0501 = [
        'Shareable booking belongs to another user',
        [],
        [],
    ]
    OE0502 = [
        'Jira issue already attached to shareable booking',
        [],
        [],
    ]
    OE0503 = [
        'Webhook %s already exists for object %s',
        ['webhook_action', 'object_id'],
        ['booking_acquire', 'b8fd2a65-8757-44c9-ab78-2f51761b2c0a']
    ]
    OE0504 = [
        '%s filtering by %s is unavailable',
        ['entity', 'entity value'],
        ['region', 'us-west-1']
    ]
    OE0505 = [
        "Employee %s (%s) doesn't have enough permissions"
    ]
    OE0506 = [
        'ssh_key with fingerprint %s already exist',
        ['fingerprint'],
        ['12:f8:7e:78:61:b4:bf:e2:de:24:15:96:4e:d4:72:53']
    ]
    OE0507 = [
        'Invalid public SSH key',
        [],
        []
    ]
    OE0508 = [
        'Manually disabling default ssh_key is prohibited. Assign another default key',
        [],
        []
    ]
    OE0509 = [
        'Deleting a non-last default ssh_key is prohibited',
        [],
        []
    ]
    OE0510 = [
        "ssh_key %s does not belong to the employee %s",
        ["ssh_key_id", "employee_id"],
        ["ssh_key c3706242-47a9-4e55-b7ab-b9f58fa9ec31 is not belong to the "
         "employee b8fd2a65-8757-44c9-ab78-2f51761b2c0a"]
    ]
    OE0511 = [
        "ssh_key should be default for employee",
        [],
        []
    ]
    OE0512 = [
        "File size limit exceeded"
    ]
    OE0513 = [
        "Cloud validation is timed out. Please retry later"
    ]
    OE0514 = [
        "%s should be a valid JSON",
        ["filters should be a valid JSON"],
        ["filters"]
    ]
    OE0515 = [
        "The interval between dates should be less than a year"
    ]
    OE0516 = [
        "Organization limit hit for constraint %s already exists in "
        "organization %s",
        ["constraint_id", "organization_id"],
        ["Organization limit hit for constraint "
         "5c9c947b-8833-474d-a2f1-c99758196c76 already exists "
         "in 4dd93c56-0fa9-43ff-965c-0b83806b9dc2"]
    ]
    OE0517 = [
        "%s or %s should be provided",
        ['param1', 'param2'],
        ['tag or without_tag should be provided']
    ]
    OE0518 = [
        "DiscoveryInfo with type %s already exists for cloud account %s",
        ["resource_type", "cloud_account_id"],
        ["DiscoveryInfo with type instance already exists for "
         "cloud account 4dd93c56-0fa9-43ff-965c-0b83806b9dc2"]
    ]
    OE0519 = [
        "%s processing task with time range %s - %s already exists for "
        "cloud account \"%s\"",
        ["task_type", "start_date", "end_date", "cloud_account_id"],
        ['Traffic processing task with time range '
         '1609448400 - 1609534800 already exists for '
         'cloud account "e7471a7e-1cb7-4525-bf90-52e767e6acd4"']
    ]
    OE0520 = [
        "Precision should be one of %s",
        ["comma separated precisions"],
        ["Precision should be one of 1, 2, 3"]
    ]
    OE0521 = [
        "Invalid state transition from %s to %s",
        ['state', 'state'],
        ['ACTIVE', 'FAILED']
    ]
    OE0522 = [
        "%s should be empty dict",
        ['last_run_result'],
        ['last_run_result should be empty dict']
    ]
    OE0523 = [
        "%s must be empty for %s status",
        ["propery", "status"],
        ["last_error_code must be empty for SUCCESS status"]
    ]
    OE0524 = [
        "Max number of users (%s) has been already reached ",
        ["max_user_count"],
        ["Max number of users (5) has been already reached "]
    ]
    OE0525 = [
        "%s must be not empty for %s status",
        ["propery", "status"],
        ["last_error_code must be not empty for FAILED status"]
    ]
    OE0526 = [
        "Profiling token already exists in organization %s",
        ["Organization uuid"],
        ["5c9c947b-8833-474d-a2f1-c99758196c76"]
    ]
    OE0527 = [
        "Profiling token not found for %s %s",
        ["Object type", "object uuid"],
        ["organization", "5c9c947b-8833-474d-a2f1-c99758196c76"]
    ]
    OE0528 = [
        "Cannot use organization_id with cloud_account_id",
        [],
        []
    ]

    OE0529 = [
        "Cannot use cloud_account_type without organization_id",
        [],
        []
    ]
    OE0530 = [
        "Priority should be 1...9",
        [],
        []
    ]
    OE0531 = [
        "period should be used exclusively",
        [],
        []
    ]
    OE0532 = [
        "period, organization_id or cloud_account_id is required",
        [],
        []
    ]
    OE0533 = [
        "invalid cloud account type: %s",
        ["cloud_account_type"],
        ["invalid"]
    ]
    OE0534 = [
        "%s with key \"%s\" already exists",
        ['Object', 'key'],
        ['Task', 'test_key']
    ]
    OE0535 = [
        "Metric with key \"%s\" is already exist",
        ['Metric key'],
        ['test_key']
    ]
    OE0536 = [
        "Currency %s is not supported",
        ["currency"],
        ["BRL"]
    ]
    OE0537 = [
        "Template %s can't be deleted because of existing runsets",
        ['template_id'],
        ["a3706242-47a9-4e55-b7ab-b9f58fa9ec31"]
    ]
    OE0538 = [
        "Runset %s should be one of %s",
        ['param', "comma separated value"],
        ['Runset instance_type should be one of m5, m1']
    ]
    OE0539 = [
        "Runset %s should be %s",
        ["param", "value"],
        ['Runset name_prefix should be "test_"']
    ]
    OE0540 = [
        "Unfilled or undefined hyperparameters %s",
        ["param"],
        ['Unfilled or undefined hyperparameters MODEL_URL, LEARNING_RATE']
    ]
    OE0541 = [
        '%s should be less than %s',
        ['param', 'value'],
        ['budget should be less than 1234']
    ]
    OE0542 = [
        'Instance types %s are unsupported on regions %s',
        ['comma separaated instance types', 'comma separated regions'],
        ['m2, t5', 'us-east-1, eu-central-1']
    ]
    OE0543 = [
        "Unauthorized: %s",
        ['reason'],
        ['Token not found']
    ]
    OE0544 = [
        "Runset %s state transition %s is not allowed",
        ['runset_id', 'state'],
        ["a3706242-47a9-4e55-b7ab-b9f58fa9ec31", '3']
    ]
    OE0545 = [
        "Action %s is not supported",
        ['state'],
        ['power off']
    ]
    OE0546 = [
        "Parameter %s is not supported for type %s",
        ['param', 'bi_type'],
        ['key', 'AWS_RAW_EXPORT']
    ]
    OE0547 = [
        "Payload should be less than %d bytes",
        [],
        []
    ]
    OE0548 = [
        "Argument %s is required",
        [],
        []
    ]
    OE0549 = [
        "Leaderboard template already exists for task %s",
        ["task_id"],
        ["a3706242-47a9-4e55-b7ab-b9f58fa9ec31"]
    ]
    OE0550 = [
        "Parameter %s should be time string in format HH:MM",
        ['param'],
        ['power_on']
    ]
    OE0551 = [
        "%s with %s \"%s\" already exists",
        ["entity type", "param name",  "provided name"],
        ["Partner", "name", "Development"]
    ]
    OE0552 = [
        "Parameter %s can\'t be equal to %s",
        ['param', 'param'],
        ['power_on', 'power_off']
    ]
    OE0553 = [
        "%s should be a timezone name",
        ['param'],
        ['timezone']
    ]
    OE0554 = [
        "Metric with id \"%s\" used in leaderboard(s)",
        ['Metric id'],
        []
    ]
    OE0555 = [
        "Dataset with id \"%s\" used in leaderboard(s)",
        ['Dataset id'],
        []
    ]
    OE0556 = [
        "Metric is used in task leaderboard(s)",
        [],
        []
    ]
    OE0557 = [
        "Model version already exists",
        [],
        []
    ]
