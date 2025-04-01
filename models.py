from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


engine = create_async_engine(("sqlite+aiosqlite:///swqpi.db"))
Session_db = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    pass


class InfoSwPerson(Base):
    __tablename__ = 'Info Star Wars person'

    id: Mapped[int] = mapped_column(primary_key=True)
    birth_year: Mapped[str]
    eye_color: Mapped[str]
    films: Mapped[str]
    gender: Mapped[str]
    hair_color: Mapped[str]
    height: Mapped[str]
    homeworld: Mapped[str]
    mass: Mapped[str]
    name: Mapped[str]
    skin_color: Mapped[str]
    species: Mapped[str]
    starships: Mapped[str]
    vehicles: Mapped[str]


async def open_conn_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_conn_db():
    await engine.dispose()