 SELECT distinct inserted_at::timestamp::date  FROM reddit_posts where  inserted_at BETWEEN  now()::date - 8      AND      now()::date - 7 order by inserted_at desc;
SELECT distinct inserted_at::timestamp::date  FROM reddit_posts where  inserted_at > now() - 7  order by inserted_at desc;