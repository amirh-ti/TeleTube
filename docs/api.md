# مرجع ماژول‌های داخلی

## `core/qualities.py`
- `fetch_available_qualities(url) -> (heights, title, error)`
- `filter_standard_qualities(heights) -> list[int]`

## `core/downloader.py`
- `download_video(url, quality, progress_hook=None) -> (file_path, title, thumb_path, message)`

## `core/uploader.py`
- `send_to_channel(file_path, title, thumb_path=None, status=None) -> message_id | None`

## `core/thumbnail.py`
- `prepare_thumbnail(info, video_id, unique_id) -> thumb_path | None`

## `core/cleanup.py`
- `schedule_cleanup(context, file_path, thumb_path=None, delay=30)`

## `tg/telethon_client.py`
- `start_telethon_client()` / `get_client()` / `stop_telethon_client()`

## `tg/bot.py`
- `build_application() -> telegram.ext.Application`

## `handlers/*.py`
- `handlers.start.start` — دستور `/start`
- `handlers.download.handle_url` — دریافت لینک و نمایش کیفیت‌ها
- `handlers.callback.button_click` / `auto_select_callback` / `process_download`
- `handlers.progress.report_progress` — گزارش زنده‌ی پیشرفت

## `utils/*.py`
- `utils.helpers.extract_video_id / sanitize_filename / progress_bar`
- `utils.validators.is_valid_youtube_url`
- `utils.logger.setup_logging / logger`
