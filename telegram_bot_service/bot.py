import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from config import BOT_API_TOKEN, ErrorLogger, DJANGO_API_BASE
from services.api_client import APIClient
from uuid import uuid4
from datetime import datetime

bot = Bot(token=BOT_API_TOKEN)
dp = Dispatcher()
api = APIClient()
commands = [
    {"command":"start",'description':'Restart the bot'},
    {"command":"latest",'description':'Latest uploaded jobs'},
]
@dp.message(CommandStart())
async def start_command(message: types.Message):
    me = await bot.get_me()
    my_username = me.username
    await message.answer(
        "👋 Hi! I’m your RemoteOk clone Bot.\n\n"
        "I can help you find the latest remote jobs from RemoteOK.com\n\n"
        "Use the inline mode anywhere by typing:\n"
        f"<code>@{my_username} job_keyword</code>\n\n"
        f"Example: @{my_username} accountant\n\n"
        "Or try the command:\n"
        "/latest - to get the most recent jobs right here.\n\n"
        "Happy job hunting! 🚀",
        parse_mode="HTML"
    )


@dp.message(Command('latest'))
async def start_handl(message: types.Message):
    logger=ErrorLogger().getLogger()
    try:
        jobs = api.get_jobs().get('results',[])

        if not jobs:
            await message.reply("We couldn't find any jobs in the database. Check in later :)")
            return

        for job in jobs:
            posted_at=datetime.strptime(job.get('posted_at', 'Unknown'),"%Y-%m-%dT%H:%M:%SZ")
            valid=datetime.strptime(job.get('validThrough', 'Unknown'),"%Y-%m-%dT%H:%M:%SZ")
            tags=', '.join(['<a href=\"https://remoteok.com/remote-'+tag['tag']+'-jobs\">'+tag['tag']+'</a>' for tag in job.get('tags', [])]) or 'None'
            message_text = (
                f"<b>{job['title']}</b>\n"
                f"🏢 Company: {job.get('company', {}).get('name', 'Unknown')}\n"
                f"💰 Salary: {job.get('salary', {}).get('min', 'N/A')} - {job.get('salary', {}).get('max', 'N/A')} "
                f"{job.get('salary', {}).get('currency', '')} per {job.get('salary', {}).get('unit', '')}\n"
                f"📍 Location: {', '.join([loc['location'] for loc in job.get('jobLocation', [])]) or 'Not specified'}\n"
                f"🌍 Applicant Location: {', '.join([loc['location'] for loc in job.get('applicantLocationRequirements', [])]) or 'Any'}\n"
                f"🕒 Work Hours: {job.get('workHours', 'Not specified')}\n"
                f"🧾 Employment Type: {job.get('employmentType', 'Unknown')}\n"
                f"📅 Posted at: {posted_at.strftime('%b %d, %Y')}\n"
                f"⏳ Valid Through: {valid.strftime('%b %d, %Y')}\n"
                f"🎁 Benefits: {job.get('benefits', '') or 'Not specified'}\n"
                f"🏷️ Tags: {tags}\n\n"
                f"{job.get('description','')[:511]}\n\n"
                f"🔗 <b><a href=\"{job.get('url')}\">Apply here</a></b>"
            )
            await message.answer(message_text,parse_mode="HTML",disable_web_page_preview=True)
    except Exception as _:
        logger.error(f"Error occured while fetching and sending data from \"{DJANGO_API_BASE} to user {message.from_user.id}\"\n\n",exc_info=True)
        print("Error occured: See logs/bot_errors.log")
        await message.answer(
                "Error\nError occured on the server. Please try again later or contact the developer.\nFor contact: @developer"
            )

        

@dp.inline_query()
async def inline_query_handler(inline_query: types.InlineQuery):
    query = inline_query.query.strip()
    offset = int(inline_query.offset) if inline_query.offset else 1
    if not query:
        await inline_query.answer([], cache_time=1)
        return
    logger = ErrorLogger().getLogger()
    try:
        jobs = api.get_jobs({"search": query,'page':offset}).get('results',[])
        results = []

        if not jobs and offset!=1:
            return

        for job in jobs:
            posted_at=datetime.strptime(job.get('posted_at', 'Unknown'),"%Y-%m-%dT%H:%M:%SZ")
            valid=datetime.strptime(job.get('validThrough', 'Unknown'),"%Y-%m-%dT%H:%M:%SZ")
            tags=', '.join(['<a href=\"https://remoteok.com/remote-'+tag['tag']+'-jobs\">'+tag['tag']+'</a>' for tag in job.get('tags', [])]) or 'None'
            message_text = (
                f"<b>{job['title']}</b>\n"
                f"🏢 Company: {job.get('company', {}).get('name', 'Unknown')}\n"
                f"💰 Salary: {job.get('salary', {}).get('min', 'N/A')} - {job.get('salary', {}).get('max', 'N/A')} "
                f"{job.get('salary', {}).get('currency', '')} per {job.get('salary', {}).get('unit', '')}\n"
                f"📍 Location: {', '.join([loc['location'] for loc in job.get('jobLocation', [])]) or 'Not specified'}\n"
                f"🌍 Applicant Location: {', '.join([loc['location'] for loc in job.get('applicantLocationRequirements', [])]) or 'Any'}\n"
                f"🕒 Work Hours: {job.get('workHours', 'Not specified')}\n"
                f"🧾 Employment Type: {job.get('employmentType', 'Unknown')}\n"
                f"📅 Posted at: {posted_at.strftime('%b %d, %Y')}\n"
                f"⏳ Valid Through: {valid.strftime('%b %d, %Y')}\n"
                f"🎁 Benefits: {job.get('benefits', '') or 'Not specified'}\n"
                f"🏷️ Tags: {tags}\n\n"
                f"{job.get('description','')[:511]}\n\n"
                f"🔗 <b><a href=\"{job.get('url')}\">Apply here</a></b>"
            )
            
            
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    thumbnail_url=job.get('image','') or 'https://via.placeholder.com/300x200.png?text=job',
                    title=job["title"],
                    description=job.get("company", {}).get("name", "Unknown"),
                    input_message_content=InputTextMessageContent(message_text=message_text,parse_mode='HTML',disable_web_page_preview=True),
                    hide_url=True
                )
            )
        if not results:
            results=[
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="No data",
                    description="The job you're looking for doesn't seem to be found in our databases. Try other keywords.",
                    input_message_content=InputTextMessageContent(message_text=f"Check out results on the site: <a href=\"https://remoteok.com/remote-{query}-jobs\">{query}</a>",parse_mode="HTML",disable_web_page_preview=True),
                    hide_url=True
                )
            ]

        await inline_query.answer(results, cache_time=1,next_offset=str(offset+1))
    except Exception as _:
        logger.error(f"Error occured while fetching and sending data from \"{DJANGO_API_BASE} to user {inline_query.from_user.id}\"\n\n",exc_info=True)
        print("Error occured: See logs/bot_errors.log")

        await inline_query.answer(
            [InlineQueryResultArticle(
                id=str(uuid4()),
                title="Error",
                description="Error occured on the server. Please try again later or contact the developer.",
                input_message_content=InputTextMessageContent(message_text="For contact: @developer")
            )],
            cache_time=5
        )

async def main():
    await bot.set_my_commands(commands)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
 