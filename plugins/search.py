import logging
import aiohttp
from urllib.parse import quote
from core.registry import register

logger = logging.getLogger("SearchPlugin")

# Custom User-Agent required by Wikipedia API to avoid HTTP 403 Forbidden
HEADERS = {
    "User-Agent": "BaleSelfBot/1.0 (https://github.com/aminmadaniofficial/baleselfbot; contact@example.com) Python-aiohttp/3.9",
    "Accept": "application/json"
}


@register(["wiki", "ویکی", "دانشنامه"])
async def wikipedia_command(app, msg, chat_id, chat_type, args):
    """
    Searches Persian Wikipedia with two-step automated title matching
    and summary extraction.
    """
    query = args.strip()
    if not query and hasattr(msg, 'replied_to') and msg.replied_to:
        from core.utils import get_text_advanced
        query = get_text_advanced(msg.replied_to).strip()

    if not query:
        await app.send_message(
            chat_id=chat_id,
            text="⚠️ لطفا موضوع مورد نظر را بنویسید. مثال: `.ویکی هوش مصنوعی`",
            chat_type=chat_type
        )
        return

    status = await app.send_message(
        chat_id=chat_id,
        text="📖 *در حال جستجو در ویکی‌پدیا...*",
        chat_type=chat_type,
        reply_to=msg
    )

    # 1. Wikipedia OpenSearch API to get the exact matching page title
    search_api_url = f"https://fa.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote(query)}&utf8=&format=json"

    try:
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            # Step 1: Find best matching title
            matched_title = None
            async with session.get(search_api_url, timeout=10) as search_resp:
                if search_resp.status == 200:
                    search_data = await search_resp.json()
                    search_results = search_data.get("query", {}).get("search", [])

                    if search_results:
                        matched_title = search_results[0]["title"]

            if not matched_title:
                matched_title = query.replace(" ", "_")

            # Step 2: Fetch REST Summary for the matched title
            summary_api_url = f"https://fa.wikipedia.org/api/rest_v1/page/summary/{quote(matched_title.replace(' ', '_'))}"
            async with session.get(summary_api_url, timeout=10) as sum_resp:
                if sum_resp.status == 200:
                    data = await sum_resp.json()
                    title = data.get("title", matched_title)
                    extract = data.get("extract", "توضیحاتی یافت نشد.")
                    page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")

                    out = [
                        f"📚 **دانشنامه ویکی‌پدیا: {title}**\n",
                        f"{extract}\n",
                    ]
                    if page_url:
                        out.append(f"🔗 [مطالعه کامل مقاله در ویکی‌پدیا]({page_url})")

                    try:
                        await app.delete_message(
                            message_id=status.message_id,
                            message_date=0,
                            chat_id=chat_id,
                            chat_type=chat_type
                        )
                    except Exception:
                        pass

                    await app.send_message(
                        chat_id=chat_id,
                        text="\n".join(out),
                        chat_type=chat_type,
                        reply_to=msg
                    )
                else:
                    await app.edit_message(
                        chat_id=chat_id,
                        message_id=status.message_id,
                        text=f"⚠️ مقاله‌ای برای «{query}» در ویکی‌پدیا یافت نشد.",
                        chat_type=chat_type
                    )

    except Exception as e:
        logger.error(f"Wikipedia search failed: {e}", exc_info=True)
        try:
            await app.edit_message(
                chat_id=chat_id,
                message_id=status.message_id,
                text=f"❌ خطای جستجو در ویکی‌پدیا: {e}",
                chat_type=chat_type
            )
        except Exception:
            pass