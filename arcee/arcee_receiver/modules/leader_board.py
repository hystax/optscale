from enum import Enum
from sanic.exceptions import SanicException
from sanic.log import logger
from collections import defaultdict


aggregate_func_map = {
    "avg": "$avg",
    "max": "$max",
    "sum": "$sum",
    "last": "$last"
}


class Tendencies(Enum):
    LESS = 'less'
    MORE = 'more'


async def get_leaderboard_params(db, token: str, leaderboard_dataset_id: str):
    pipeline = [
        {"$match": {"_id": leaderboard_dataset_id}},
        {
            "$lookup": {
                "from": "metric",
                "localField": "primary_metric",
                "foreignField": "_id",
                "as": "primary_metric",
            },
        },
        {
            "$lookup": {
                "from": "metric",
                "localField": "other_metrics",
                "foreignField": "_id",
                "as": "other_metrics",
            },
        },
        {
            "$lookup": {
                "from": "leaderboard",
                "localField": "leaderboard_id",
                "foreignField": "_id",
                "as": "leaderboard"
            }
        },
        {"$unwind": "$leaderboard"},
        {"$unwind": "$primary_metric"},
    ]
    ri = None
    cur = db.leaderboard_dataset.aggregate(pipeline)
    try:
        ri = await cur.next()
    except StopAsyncIteration:
        pass
    if not ri:
        raise SanicException("Leaderboard dataset not found", status_code=404)
    dataset_ids = set(ri.get("dataset_ids", []))
    tags = ri.get("grouping_tags", [])
    task_id = ri['leaderboard']["task_id"]
    hyperparams = []
    if ri.get("group_by_hp", False):
        hyperparams = await get_available_hps(db, task_id)

    primary_metric = ri["primary_metric"]
    all_metrics = ri.get("other_metrics", []) + [primary_metric]
    key_metric_map = {}
    id_key_map = {}
    for metric in all_metrics:
        key = metric['key']
        key_metric_map[key] = metric
        id_key_map[metric['_id']] = key

    filters = {}
    for f in ri.get("filters", []):
        key = id_key_map[f['id']]
        min_ = f.get("min")
        max_ = f.get("max")
        filters[key] = (min_, max_)

    dataset_coverage_rules = ri.get('dataset_coverage_rules')
    dataset_coverage = defaultdict(list)
    if dataset_coverage_rules:
        db_labels = db.dataset.aggregate([
            {'$match': {
                'token': token,
                'deleted_at': 0
            }},
            {'$unwind': '$labels'},
            {'$match': {
                'labels': {'$in': list(dataset_coverage_rules.keys())}
            }},
            {'$sort': {'created_at': -1}}
        ])
        try:
            async for i in db_labels:
                label = i['labels']
                if len(dataset_coverage[label]
                       ) < dataset_coverage_rules[label]:
                    dataset_coverage[label].append(i['_id'])
        except StopAsyncIteration:
            pass
    return (task_id, list(dataset_ids), primary_metric,
            key_metric_map, tags, hyperparams, filters, dataset_coverage)


async def qualification_datasets(db, token: str, ids: list):
    pipeline = [
        {
            "$match": {
                "_id": {"$in": ids},
                "token": token,
                "deleted_at": {"$eq": 0},
            }
        },
        {"$sort": {"created_at": -1}},
        {
            "$lookup": {
                "from": "run",
                "as": "run_data",
                "let": {"dsid": "$_id"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$dataset_id", "$$dsid"]},
                                    {"$eq": ["$state", 2]},
                                ]
                            }
                        }
                    },
                    {"$sort": {"start": -1}},
                    {"$limit": 1},
                ],
            }
        },
        {"$unwind": "$run_data"},
    ]

    cur = db.dataset.aggregate(pipeline)
    return [i async for i in cur]


async def get_available_hps(db, task_id: str):
    """
    Gets available hyperparameters for grouping
    """

    result = []
    pipeline = [
        {
            "$match": {
                "task_id": task_id,
            }
        },
        {"$project": {"hpkeys": {"$objectToArray": "$hyperparameters"}}},
        {"$unwind": "$hpkeys"},
        {"$group": {"_id": "null", "keys": {"$addToSet": "$hpkeys.k"}}},
        {"$project": {"_id": 0, "keys": 1}},
    ]
    cur = db.run.aggregate(pipeline)
    try:
        r = await cur.next()
        result = r.get("keys", [])
    except StopAsyncIteration:
        pass
    return result


def update_metrics_pipeline(metrics, group_block, project_block,
                            primary_metric_key):
    for m in metrics:
        metric, func = m
        group_block["$group"][metric] = {func: "$data.%s" % metric}
        # $sum returns `0` on both null and 0 values, so let's count
        # not null values to identify is `0` value null or 0
        group_block["$group"]["%s_not_null_count" % metric] = {
            '$sum': {
                '$cond': [
                    {"$eq": [
                        # handle both null and missing field
                        {'$ifNull': ["$data.%s" % metric, None]}, None]},
                    0, 1]
            }
        }

        metric_project_cond = {
            metric: {
                '$cond': [{
                    '$and': [
                        {'$eq': ["$%s" % metric, 0]},
                        {'$eq': ["$%s_not_null_count" % metric, 0]}
                    ]},
                    None, "$%s" % metric]}}
        if metric == primary_metric_key:
            if project_block["$project"].get("primary_metric") is None:
                project_block["$project"][
                    "primary_metric"] = metric_project_cond
        else:
            if project_block["$project"].get("metrics") is None:
                project_block["$project"]["metrics"] = {}
            project_block["$project"]["metrics"].update(metric_project_cond)
    return group_block, project_block


async def generate_candidates_template(
    task_id: str,
    qual_proto: dict,  # {key: (min, max)}
    group: tuple,  # (tags, hyperparameters)
    metrics: list,  # [(metric key, func), ...]
    primary_metric_key: str
):
    """
    Generates pipeline for calculating leaderboard candidates
    """

    match = {
        "$match": {
            "state": 2,
            "task_id": "%s" % task_id,
        },
    }

    for metric, lim in qual_proto.items():
        # qualification protocol stores in dict, key is metric
        # value is a tuple of (min, max)
        min_, max_ = lim
        limits = {}
        if min_ is not None:
            limits.update({"$gte": min_})
        if max_ is not None:
            limits.update({"$lte": max_})
        match["$match"].update(
            {
                "data.%s" % metric: limits,
            }
        )

    sort = {
        "$sort": {
            "updated_at": -1,
        },
    }

    group_id = {}

    tags, hp = group
    for t in tags:
        # affects orders & filter
        sort["$sort"].update({"tags.%s" % t: -1})
        group_id.update({t: "$tags.%s" % t})
    for h in hp:
        sort["$sort"].update({"hyperparameters.%s" % h: -1})
        group_id.update({h: "$hyperparameters.%s" % h})
    group = {
        "$group": {
            "_id": group_id,
            "task_id": {
                "$last": "$task_id",
            },
            "dataset_ids": {
                "$addToSet": "$dataset_id",
            },
            "run_ids": {
                "$addToSet": "$_id",
            },
        }
    }

    project = {
        "$project": {
            "_id": 0,
            "dataset_ids": 1,
            "run_ids": 1,
        }
    }

    # affects orders & filter
    for t in tags:
        group["$group"][t] = {"$last": "$tags.%s" % t}
        if project["$project"].get("tags") is None:
            project["$project"]["tags"] = {}
        project["$project"]["tags"].update({t: "$%s" % t})
    for h in hp:
        group["$group"][h] = {"$last": "$hyperparameters.%s" % h}
        if project["$project"].get("hyperparams") is None:
            project["$project"]["hyperparams"] = {}
        project["$project"]["hyperparams"].update({h: "$%s" % h})

    group, project = update_metrics_pipeline(metrics, group, project,
                                             primary_metric_key)
    return [match, sort, group, project]


async def update_candidate_template(runs, datasets, tags: list, hp: list,
                                    primary_metric_key: str, metrics: list):
    match = {
        "$match": {
            "$and": [
                {"_id": {"$in": runs}},
                {"dataset_id": {"$in": datasets}},
                {"state": 2},
            ]
        },
    }

    sort = {
        "$sort": {
            "started": -1,
        },
    }
    group_id = {}

    project = {
        "$project": {
            "_id": 0,
            "qual_runs": 1,
        }
    }
    for t in tags:
        # affects orders & filter
        group_id.update({t: "$tags.%s" % t})

    for h in hp:
        group_id.update({h: "$hyperparameters.%s" % h})

    group = {
        "$group": {
            "_id": group_id,
            "qual_runs": {
                "$addToSet": "$_id",
            },
        }
    }
    group, project = update_metrics_pipeline(metrics, group, project,
                                             primary_metric_key)
    return [match, sort, group, project]


async def leaderboard_candidates(
        db,
        task_id: str,
        qual_proto: dict,  # {key: (min, max)}
        group: tuple,  # (tags, hyperparameters)
        metrics: list,  # [(metric key, func), ...]
        primary_metric_key: str):
    """
    Gets leaderboard candidates
    """
    #  We skip token verification here because - move to task map
    # defines metrics priority

    pipeline = await generate_candidates_template(
        task_id, qual_proto, group, metrics, primary_metric_key
    )

    cur = db.run.aggregate(pipeline)
    return [candidate async for candidate in cur]


async def rank_by_datasets(
        db,
        datasets: list,
        candidates: list,
        grp: tuple,
        pri_metric_key: str,
        metrics: list,
        key_metrics_map: dict,
        dataset_coverage: dict
):
    """
    Calculates candidates ranked (qualified) by datasets
    """
    tags, hps = grp

    # use closure to replace metrics
    def update_metrics(m: dict):
        for k, v in m.items():
            # try to get name and func from metrics
            metric_name = key_metrics_map.get(k, {}).get("name")
            func_name = key_metrics_map.get(k, {}).get("func")
            m[k] = {
                "name": metric_name,
                "value": v,
                "func": func_name,
            }

    qual_ds_ids = [x["_id"] for x in datasets]
    for candidate in candidates:
        candidate["dataset_coverage"] = {}
        qualification = set(candidate.get(
            "dataset_ids", list())) & set(qual_ds_ids)
        # add qualification to candidate
        if candidate.get("qualification") is None:
            candidate["qualification"] = []
        for k, v in dataset_coverage.items():
            candidate["dataset_coverage"][k] = list(set(v) & qualification)
        qual = list(qualification)
        # candidate qualification represents calculation only by
        # covered datasets
        candidate["qualification"].extend(qual)
        candidate.update({"qual_runs": []})
        if qual:
            # need to recalculate metrics - generate pipelines based on
            # dataset coverage 2-nd level candidate
            catl_pipeline = await update_candidate_template(
                candidate.get("run_ids", []), qual, tags, hps, pri_metric_key,
                metrics
            )
            catl_cur = db.run.aggregate(catl_pipeline)
            re_ranked = {}
            try:
                re_ranked = await catl_cur.next()
            except StopAsyncIteration:
                # No qual runs
                pass
            candidate.update(re_ranked)
        update_metrics(candidate.get("primary_metric", {}))
        update_metrics(candidate.get("metrics", {}))

    return candidates


async def sort_candidates(candidates: list, primary_metric_key: str,
                          direct=True):
    if direct:
        res = sorted(
            candidates,
            key=lambda candidate: (
                -len(candidate["qualification"]),
                -candidate["primary_metric"][primary_metric_key]["value"],
            ),
        )
    else:
        res = sorted(
            candidates,
            key=lambda candidate: (
                -len(candidate["qualification"]),
                candidate["primary_metric"][primary_metric_key]["value"],
            ),
        )
    return res


async def get_metrics(db, task_id: str):
    pipeline = [
        {"$match": {"_id": "%s" % task_id}},
        {
            "$lookup": {
                "from": "metric",
                "localField": "metrics",
                "foreignField": "_id",
                "as": "task_metrics",
            }
        },
        {"$project": {"_id": 0, "task_metrics": 1}},
    ]
    cur = db.task.aggregate(pipeline)
    metrics = await cur.next()
    result = {}
    for g in metrics["task_metrics"]:
        result[g["key"]] = g
    return result


async def get_aggregation_list(key_metric_map: dict):
    """
    converts metrics map to
    following structure - [(metric key, func), ...]
    :param key_metric_map:
    :return:
    """
    mtr = []
    for metric_key, metric in key_metric_map.items():
        f = aggregate_func_map.get(metric.get("func"))
        mtr.append((metric_key, f))
    return mtr


async def generate_leaderboard(
    db,
    token: str,
    task_id: str,
    tags: list,
    hyperparameters: list,
    primary_metric: dict,
    key_metric_map: dict,
    dataset_ids: list,
    qualification_protocol: dict,  # leaderboard filters : {key: (min, max)}
    dataset_coverage: dict,  # coverage rules datasets : {label: [id_1, id_2]}
):
    # Algorithm

    # 1. Get datasets
    # 2. Generate template for leaderboard candidates
    # 3. Based on template get leaderboard candidates
    # 4. Get "2-nd level" candidates, qualified by datasets
    # 5. Recalculate metrics only by qualification cases
    # 6. Sort according to dataset qualification in dataset order,
    # then primary metric

    # arguments:
    # token
    # token = "6bd6106c-ff94-440d-acae-8c721555f00d"

    # task id
    # task_id = "9acd90c0-22f3-4c11-b3d2-dc38fc21e5be"

    # first iterable - tags, second - hyperparameters

    # tags = ["code_commit",]
    # hyperparameters = ["EPOCHS",]

    # primary metric
    # primary_metric = {
    #     "key": "accuracy",
    #     "func": "sum",
    #     "target_value": 0,
    #     "name": "loss",
    #     "_id": "ebbd10fd-6732-411d-b232-a63e4a83aa23"
    # }

    # map of metric keys and metrics
    # key_metric_map = {
    #     "accuracy": {
    #         "key": "accuracy",
    #         "func": "sum",
    #         "target_value": 0,
    #         "tendency": "less",
    #         "name": "loss",
    #         "_id": "ebbd10fd-6732-411d-b232-a63e4a83aa23"
    #     }
    # }

    # ids of qualification datasets
    # qualification_dss = [
    #         "20c46942-6f79-4bd9-82a9-de9fc68c536e",
    #         "3610fff8-6be2-4f3f-b982-7c0254564644",
    #     ]

    # qualification protocol (leaderboard filters in format: {key: (min, max)})
    # qualification_protocol = {"accuracy": (50, 100)}

    group = (tags, hyperparameters)

    aggr_list = await get_aggregation_list(key_metric_map)

    dataset_ids = set(dataset_ids)
    for _ids in dataset_coverage.values():
        dataset_ids.update(_ids)
    dss = await qualification_datasets(
        db,
        token,
        list(dataset_ids),
    )
    cand = await leaderboard_candidates(
        db, task_id, qualification_protocol, group, aggr_list,
        primary_metric['key'])
    ranked = await rank_by_datasets(db, dss, cand, group,
                                    primary_metric['key'], aggr_list,
                                    key_metric_map, dataset_coverage)
    order = primary_metric.get("tendency",
                               Tendencies.MORE.value) == Tendencies.MORE.value
    # finally, leader board
    return await sort_candidates(ranked, primary_metric['key'], order)


async def get_calculated_leaderboard(db, token: str,
                                     leaderboard_dataset_id: str):
    (
        task_id,
        dataset_ids,
        primary_metric,
        key_metric_map,
        tags,
        hyperparams,
        qualification_protocol,
        dataset_coverage
    ) = await get_leaderboard_params(db, token, leaderboard_dataset_id)
    leaderboard = await generate_leaderboard(
        db,
        token,
        task_id,
        tags,
        hyperparams,
        primary_metric,
        key_metric_map,
        dataset_ids,
        qualification_protocol,
        dataset_coverage
    )
    return leaderboard
