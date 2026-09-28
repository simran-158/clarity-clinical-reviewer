from alembic import context
from app.config import Settings
from app.db import Database
from app.models import Base

config = context.config
url = config.attributes.get("database_url") or Settings().database_url
if context.is_offline_mode():
    context.configure(url=url, target_metadata=Base.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    database = Database(url)
    with database.engine.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()
    database.engine.dispose()
