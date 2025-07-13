{{ config(materialized='incremental', unique_key='message_id') }}

SELECT
    stg.message_id,
    stg.message_timestamp,
    stg.message_text,
    stg.is_outgoing,
    stg.is_post,
    stg.media_type,
    stg.photo_id,
    stg.document_id,
    stg.channel_id,
    dc.channel_name, -- Join with dim_channels for channel name
    stg.loaded_at
FROM
    {{ ref('stg_telegram_messages') }} stg
LEFT JOIN
    {{ ref('dim_channels') }} dc ON stg.channel_id = dc.channel_id

{% if is_incremental() %}
  -- This tells dbt to only process new records since the last run
  WHERE stg.loaded_at > (SELECT MAX(loaded_at) FROM {{ this }})
{% endif %}