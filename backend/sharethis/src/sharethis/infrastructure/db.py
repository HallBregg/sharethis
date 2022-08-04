import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import ConcreteBase
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker, Session

from sharethis.infrastructure.models import Base


class SQLAlchemyDatabase:
    """
    Abstraction over SQLAlchemy DAL.
    """
    def __init__(
        self,
        connection_string: str,
        logger: logging.Logger = logging.getLogger(__name__)
    ):
        self._logger = logger
        # TODO add retry for db connection.
        self._connection_string = connection_string
        self._engine = create_engine(
            self._connection_string,
            pool_size=10,
            max_overflow=4,
            pool_pre_ping=True,
        )
        self._session_maker = scoped_session(
            sessionmaker(
                bind=self._engine,
                autocommit=False,
                expire_on_commit=False
            )
        )

    def get_session(self) -> Session:
        """
        Create and return SQLAlchemy session instance.

        Args:
        Returns: Session()
        """
        return self._session_maker()

    def get_session_factory(self) -> scoped_session:
        """
        Return SQLAlchemy session class. This method acts as a factory for database session.

        Args:
        Returns: Session
        """
        return self._session_maker

    def create_database(self, base: ConcreteBase = Base):
        """
        Generate SQL schema and create all models from Base class.
        """
        base.metadata.create_all(self._engine)
        self._logger.info('Database created.')

    def drop_database(self, base: ConcreteBase = Base):
        """
        Drop existing database.
        """
        base.metadata.drop_all(self._engine)
        self._logger.info('Database deleted.')

    @property
    def healthy(self):
        # noinspection PyBroadException
        try:
            with self.get_session() as session:
                session.execute('SELECT 1;')
        except Exception:
            return False
        return True
