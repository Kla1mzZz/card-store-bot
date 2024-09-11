from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine('sqlite+aiosqlite:///database.db', connect_args={"timeout": 15})

async_session = async_sessionmaker(engine)