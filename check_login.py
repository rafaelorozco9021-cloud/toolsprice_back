from app.db.session import async_session_factory
from app.db.models.models import User
from sqlalchemy import select
import asyncio, bcrypt

async def t():
    async with async_session_factory() as s:
        r=await s.execute(select(User))
        users=r.scalars().all()
        for u in users:
            print(f"USER {u.email} hash {u.password_hash[:30]}")
            # test verify with known password 12345678? for test users we used that
            for pwd in ["12345678","123456789","password123"]:
                ok=bcrypt.checkpw(pwd.encode(), u.password_hash.encode())
                if ok:
                    print(f"  -> password matches '{pwd}'")
                    break

asyncio.run(t())
