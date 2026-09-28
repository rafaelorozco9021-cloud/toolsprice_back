from app.db.session import async_session_factory
from app.db.models.models import User
from sqlalchemy import select
import asyncio, bcrypt

async def t():
    async with async_session_factory() as s:
        email="rafaelorozco9021@gmail.com"
        pwd="demo123"
        r=await s.execute(select(User).filter(User.email==email))
        u=r.scalars().first()
        if u:
            print(f"Usuario ya existe: {u.email} verified={u.email_verified}")
            # actualizar password y verificar
            u.password_hash=bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()
            u.email_verified=True
            await s.commit()
            print("Password actualizado y verificado")
        else:
            import uuid
            new=User(
                id=str(uuid.uuid4()),
                name="Rafael Orozco",
                email=email,
                password_hash=bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode(),
                email_verified=True,
                is_active=True
            )
            s.add(new)
            await s.commit()
            print(f"Usuario creado {email}")

        # verificar login
        r2=await s.execute(select(User).filter(User.email==email))
        u2=r2.scalars().first()
        ok=bcrypt.checkpw(pwd.encode(), u2.password_hash.encode())
        print(f"Verificacion bcrypt para demo123: {ok}")

asyncio.run(t())
