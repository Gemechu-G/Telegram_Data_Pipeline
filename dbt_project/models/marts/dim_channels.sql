{{ config(materialized='table') }}

SELECT
    channel_id,
    MIN(SUBSTRING(file_path FROM 'telegram_images\\(\d{4}-\d{2}-\d{2})\\(.*?)_(\d{4}-\d{2}-\d{2})\.json')) AS channel_name, -- This will extract the directory name
    COUNT(DISTINCT message_id) AS total_messages,
    MIN(message_timestamp) AS first_message_at,
    MAX(message_timestamp) AS last_message_at
FROM
    {{ ref('stg_telegram_messages') }}
GROUP BY
    channel_id