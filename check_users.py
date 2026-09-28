from app.db.session import async_session_factory
from app.db.models.models import User
from sqlalchemy import select
import asyncio
async def t():
    async with async_session_factory() as s:
        r=await s.execute(select(User))
        users=r.scalars().all()
        print(f'Total users: {len(users)}')
        for u in users[-10:]:
            print(u.email, "|", u.name, "| verified", u.email_verified, "|", u.password_hash[:25])
asyncio.run(t())
