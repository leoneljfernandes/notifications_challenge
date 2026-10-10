"""Datos de ejemplo para desarrollo.

Uso (con las migraciones ya aplicadas):
    uv run python -m app.seed

Es idempotente: si un usuario ya existe (por email) no se vuelve a crear
ni se le agregan notificaciones.
"""
import asyncio

from sqlalchemy import select

from app.auth import hash_password
from app.database import AsyncSessionLocal, engine
from app.models.notification import ChannelType, Notification
from app.models.user import User

SEED_PASSWORD = "Password123"

SEED_USERS = [
    {
        "email": "ana@example.com",
        "name": "Ana Admin",
        "is_admin": True,
        "notifications": [
            {
                "title": "Bienvenida",
                "message": "Tu cuenta fue creada correctamente.",
                "channel_type": ChannelType.EMAIL,
                "channel_metadata": {},
                "is_read": True,  # única notificación leída del seed
            },
            {
                "title": "Código de verificación",
                "message": "Tu código es 482913.",
                "channel_type": ChannelType.SMS,
                "channel_metadata": {"phone_number": "5491112345678"},
            },
        ],
    },
    {
        "email": "bruno@example.com",
        "name": "Bruno Pérez",
        "is_admin": False,
        "notifications": [
            {
                "title": "Nuevo mensaje",
                "message": "Tienes un mensaje sin leer.",
                "channel_type": ChannelType.PUSH,
                "channel_metadata": {"device_token": "device-token-bruno-001"},
            },
            {
                "title": "Resumen semanal",
                "message": "Este es el resumen de tu actividad de la semana.",
                "channel_type": ChannelType.EMAIL,
                "channel_metadata": {},
            },
        ],
    },
    {
        "email": "carla@example.com",
        "name": "Carla Gómez",
        "is_admin": False,
        "notifications": [
            {
                "title": "Alerta de seguridad",
                "message": "Detectamos un inicio de sesión nuevo.",
                "channel_type": ChannelType.SMS,
                "channel_metadata": {"phone_number": "5491187654321"},
            },
            {
                "title": "Promoción",
                "message": "Tienes un 20% de descuento esta semana.",
                "channel_type": ChannelType.PUSH,
                "channel_metadata": {"device_token": "device-token-carla-001"},
            },
        ],
    },
]


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        for data in SEED_USERS:
            exists = await session.scalar(select(User.id).where(User.email == data["email"]))
            if exists:
                print(f"= {data['email']} ya existe, se omite")
                continue

            user = User(
                email=data["email"],
                name=data["name"],
                password_hash=hash_password(SEED_PASSWORD),
                is_admin=data["is_admin"],
            )
            user.notifications = [Notification(**n) for n in data["notifications"]]
            session.add(user)
            print(f"+ {data['email']} creado con {len(user.notifications)} notificaciones")

        await session.commit()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
