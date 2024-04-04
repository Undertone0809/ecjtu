import asyncio

from ecjtu import AsyncECJTU

client = AsyncECJTU(stud_id="xxx", password="xxx")


async def main():
    courses = await client.scheduled_courses.today()
    print(courses)


asyncio.run(main())
