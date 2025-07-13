{{ config(materialized='view') }}

SELECT
    (message_data->>'id')::bigint AS message_id,
    (message_data->>'date')::timestamp with time zone AS message_timestamp,
    (message_data->>'message')::text AS message_text,
    (message_data->>'out')::boolean AS is_outgoing,
    (message_data->>'mentioned')::boolean AS is_mentioned,
    (message_data->>'media_unread')::boolean AS is_media_unread,
    (message_data->>'silent')::boolean AS is_silent,
    (message_data->>'post')::boolean AS is_post,
    (message_data->>'from_scheduled')::boolean AS is_from_scheduled,
    (message_data->>'legacy')::boolean AS is_legacy,
    (message_data->>'edit_hide')::boolean AS is_edit_hide,
    (message_data->>'pinned')::boolean AS is_pinned,
    (message_data->>'noforwards')::boolean AS no_forwards,
    (message_data->>'media')::text AS media_type,
    (message_data->>'photo_id')::bigint AS photo_id,
    (message_data->>'document_id')::bigint AS document_id,

    -- Extracting from nested JSON (peer_id)
    COALESCE(
        message_data->'peer_id'->>'channel_id',
        message_data->'peer_id'->>'chat_id'
    )::bigint AS channel_id, -- Assuming messages are from channels or chats

    -- Add more fields from message_data JSONB as needed
    loaded_at,
    file_path
FROM
    {{ source('telegram_raw', 'raw_telegram_messages') }}
WHERE
    message_data IS NOT NULL
    -- Add a filter for messages that actually have a message_id, if needed
    AND message_data->>'id' IS NOT NULL