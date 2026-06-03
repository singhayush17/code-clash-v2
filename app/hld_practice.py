from __future__ import annotations
from typing import Any
from .lld_practice import Lesson, Task

# --- Core Concepts (9 chapters) ---
from .hld_core import networking_lesson as _hld_networking, api_design_lesson as _hld_api, data_modeling_lesson as _hld_dm
from .hld_core2 import db_indexing_lesson as _hld_idx, caching_lesson as _hld_cache
from .hld_core3 import sharding_lesson as _hld_shard, consistent_hashing_lesson as _hld_ch, cap_theorem_lesson as _hld_cap, numbers_lesson as _hld_num
# --- Patterns (7 chapters) ---
from .hld_patterns import realtime_updates_lesson as _hld_rt, contention_lesson as _hld_cnt, multistep_lesson as _hld_ms, scaling_reads_lesson as _hld_sr
from .hld_patterns2 import scaling_writes_lesson as _hld_sw, large_blobs_lesson as _hld_lb, long_running_tasks_lesson as _hld_lt
# --- Key Technologies (9 chapters) ---
from .hld_tech import redis_lesson as _hld_redis, elasticsearch_lesson as _hld_es, kafka_lesson as _hld_kafka
from .hld_tech2 import api_gateway_lesson as _hld_gw, cassandra_lesson as _hld_cass, dynamodb_lesson as _hld_ddb
from .hld_tech3 import postgresql_lesson as _hld_pg, flink_lesson as _hld_flink, zookeeper_lesson as _hld_zk
# --- Advanced Topics (3 chapters) ---
from .hld_advanced import bigdata_ds_lesson as _hld_bd, vector_db_lesson as _hld_vec, timeseries_db_lesson as _hld_ts
# --- Case Studies / Breakdowns (29 chapters) ---
from .hld_breakdowns1 import (
    bitly_lesson as _hld_bitly, dropbox_lesson as _hld_dropbox, delivery_service_lesson as _hld_delivery,
    news_aggregator_lesson as _hld_news, ticketmaster_lesson as _hld_ticketmaster,
    fb_news_feed_lesson as _hld_fb_feed, tinder_lesson as _hld_tinder, leetcode_lesson as _hld_leetcode,
    whatsapp_lesson as _hld_whatsapp, yelp_lesson as _hld_yelp
)
from .hld_breakdowns2 import (
    strava_lesson as _hld_strava, rate_limiter_lesson as _hld_rl, online_auction_lesson as _hld_auction,
    live_comments_lesson as _hld_comments, fb_post_search_lesson as _hld_search,
    price_tracking_lesson as _hld_price, instagram_lesson as _hld_insta, youtube_top_k_lesson as _hld_topk,
    uber_lesson as _hld_uber, robinhood_lesson as _hld_robinhood
)
from .hld_breakdowns3 import (
    google_docs_lesson as _hld_docs, distributed_cache_lesson as _hld_dist_cache,
    youtube_lesson as _hld_youtube, job_scheduler_lesson as _hld_scheduler,
    web_crawler_lesson as _hld_crawler, ad_click_aggregator_lesson as _hld_ad,
    payment_system_lesson as _hld_pay, metrics_monitoring_lesson as _hld_metrics,
    chatgpt_lesson as _hld_chatgpt
)

LESSONS: list[Lesson] = [
    # Core Concepts
    _hld_networking(), _hld_api(), _hld_dm(), _hld_idx(), _hld_cache(),
    _hld_shard(), _hld_ch(), _hld_cap(), _hld_num(),
    # Patterns
    _hld_rt(), _hld_cnt(), _hld_ms(), _hld_sr(), _hld_sw(), _hld_lb(), _hld_lt(),
    # Key Technologies
    _hld_redis(), _hld_es(), _hld_kafka(), _hld_gw(), _hld_cass(), _hld_ddb(), _hld_pg(), _hld_flink(), _hld_zk(),
    # Advanced Topics
    _hld_bd(), _hld_vec(), _hld_ts(),
    # Case Studies
    _hld_bitly(), _hld_dropbox(), _hld_delivery(), _hld_news(), _hld_ticketmaster(),
    _hld_fb_feed(), _hld_tinder(), _hld_leetcode(), _hld_whatsapp(), _hld_yelp(),
    _hld_strava(), _hld_rl(), _hld_auction(), _hld_comments(), _hld_search(),
    _hld_price(), _hld_insta(), _hld_topk(), _hld_uber(), _hld_robinhood(),
    _hld_docs(), _hld_dist_cache(), _hld_youtube(), _hld_scheduler(), _hld_crawler(),
    _hld_ad(), _hld_pay(), _hld_metrics(), _hld_chatgpt(),
]

LESSON_BY_ID = {lesson.id: lesson for lesson in LESSONS}

NOTES_BY_LESSON = {
    # Core Concepts
    "hld-networking": "https://www.hellointerview.com/learn/system-design/deep-dives/networking",
    "hld-api-design": "https://www.hellointerview.com/learn/system-design/deep-dives/api-design",
    "hld-data-modeling": "https://www.hellointerview.com/learn/system-design/deep-dives/data-modeling",
    "hld-db-indexing": "https://www.hellointerview.com/learn/system-design/deep-dives/db-indexing",
    "hld-caching": "https://www.hellointerview.com/learn/system-design/deep-dives/caching",
    "hld-sharding": "https://www.hellointerview.com/learn/system-design/deep-dives/sharding",
    "hld-consistent-hashing": "https://www.hellointerview.com/learn/system-design/deep-dives/consistent-hashing",
    "hld-cap-theorem": "https://www.hellointerview.com/learn/system-design/deep-dives/cap-theorem",
    "hld-numbers": "https://www.hellointerview.com/learn/system-design/deep-dives/numbers",
    # Patterns
    "hld-realtime-updates": "https://www.hellointerview.com/learn/system-design/in-a-hurry/common-patterns",
    "hld-contention": "https://www.hellointerview.com/learn/system-design/in-a-hurry/common-patterns",
    "hld-multistep": "https://www.hellointerview.com/learn/system-design/in-a-hurry/common-patterns",
    "hld-scaling-reads": "https://www.hellointerview.com/learn/system-design/in-a-hurry/common-patterns",
    "hld-scaling-writes": "https://www.hellointerview.com/learn/system-design/in-a-hurry/common-patterns",
    "hld-large-blobs": "https://www.hellointerview.com/learn/system-design/in-a-hurry/common-patterns",
    "hld-long-tasks": "https://www.hellointerview.com/learn/system-design/in-a-hurry/common-patterns",
    # Key Technologies
    "hld-redis": "https://www.hellointerview.com/learn/system-design/deep-dives/redis",
    "hld-elasticsearch": "https://www.hellointerview.com/learn/system-design/deep-dives/elasticsearch",
    "hld-kafka": "https://www.hellointerview.com/learn/system-design/deep-dives/kafka",
    "hld-api-gateway": "https://www.hellointerview.com/learn/system-design/deep-dives/api-gateway",
    "hld-cassandra": "https://www.hellointerview.com/learn/system-design/deep-dives/cassandra",
    "hld-dynamodb": "https://www.hellointerview.com/learn/system-design/deep-dives/dynamodb",
    "hld-postgresql": "https://www.hellointerview.com/learn/system-design/deep-dives/postgresql",
    "hld-flink": "https://www.hellointerview.com/learn/system-design/deep-dives/flink",
    "hld-zookeeper": "https://www.hellointerview.com/learn/system-design/deep-dives/zookeeper",
    # Advanced Topics
    "hld-bigdata-ds": "https://www.hellointerview.com/learn/system-design/deep-dives/bloom-filters",
    "hld-vector-db": "https://www.hellointerview.com/learn/system-design/deep-dives/vector-dbs",
    "hld-timeseries-db": "https://www.hellointerview.com/learn/system-design/deep-dives/timeseries-dbs",
    # Case Studies
    "hld-bitly": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/bitly",
    "hld-dropbox": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/dropbox",
    "hld-delivery": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/local-delivery",
    "hld-news-aggregator": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/news-aggregator",
    "hld-ticketmaster": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster",
    "hld-fb-news-feed": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/fb-news-feed",
    "hld-tinder": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/tinder",
    "hld-leetcode": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/leetcode",
    "hld-whatsapp": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/whatsapp",
    "hld-yelp": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/yelp",
    "hld-strava": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/strava",
    "hld-rate-limiter": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/rate-limiter",
    "hld-online-auction": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/online-auction",
    "hld-live-comments": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/fb-live-comments",
    "hld-post-search": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/fb-post-search",
    "hld-price-tracking": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/price-tracking-service",
    "hld-instagram": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/instagram",
    "hld-top-k": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/youtube-top-k",
    "hld-uber": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/uber",
    "hld-robinhood": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/robinhood",
    "hld-google-docs": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/google-docs",
    "hld-dist-cache": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/distributed-cache",
    "hld-youtube": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/youtube",
    "hld-job-scheduler": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/job-scheduler",
    "hld-web-crawler": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/web-crawler",
    "hld-ad-aggregator": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/ad-click-aggregator",
    "hld-payment": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/payment-system",
    "hld-metrics": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/metrics-monitoring",
    "hld-chatgpt": "https://www.hellointerview.com/learn/system-design/problem-breakdowns/chatgpt",
}

def lesson_index() -> list[dict[str, Any]]:
    return [
        {
            "id": lesson.id,
            "number": lesson.number,
            "title": lesson.title,
            "focus": list(lesson.focus),
            "taskCount": len(lesson.tasks),
            "patternCount": len(lesson.patterns),
            "badge": lesson.badge,
            "notesUrl": NOTES_BY_LESSON.get(lesson.id, ""),
        }
        for lesson in LESSONS
    ]

def task_payload(task: Task) -> dict[str, Any]:
    return {
        "id": task.id,
        "kind": task.kind,
        "prompt": task.prompt,
        "difficulty": task.difficulty,
        "tags": list(task.tags),
        "options": list(task.options),
        "hint": task.hint,
        "checklist": list(task.checklist),
    }

def lesson_payload(lesson_id: str) -> dict[str, Any]:
    lesson = get_lesson(lesson_id)
    return {
        "id": lesson.id,
        "number": lesson.number,
        "title": lesson.title,
        "focus": list(lesson.focus),
        "overview": lesson.overview,
        "badge": lesson.badge,
        "notesUrl": NOTES_BY_LESSON.get(lesson.id, ""),
        "patterns": [],
        "tasks": [task_payload(task) for task in lesson.tasks],
    }

def get_lesson(lesson_id: str) -> Lesson:
    if lesson_id in LESSON_BY_ID:
        return LESSON_BY_ID[lesson_id]
    return LESSONS[0]

def get_task(lesson: Lesson, task_id: str) -> Task:
    for task in lesson.tasks:
        if task.id == task_id:
            return task
    return lesson.tasks[0]

def check_hld(lesson_id: str, task_id: str, *, answer: int | None = None) -> dict[str, Any]:
    lesson = get_lesson(lesson_id)
    task = get_task(lesson, task_id)

    if answer is None:
        raise ValueError("Choose an option first.")
    correct = answer == task.answer_index
    return {
        "correct": correct,
        "message": "Correct." if correct else "Not quite.",
        "explanation": task.explanation,
        "expectedIndex": task.answer_index,
        "solution": task.options[task.answer_index] if task.answer_index is not None else "",
    }
