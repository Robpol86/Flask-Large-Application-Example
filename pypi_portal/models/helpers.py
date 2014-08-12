"""Convenience functions which interact with SQLAlchemy models."""

from sqlalchemy import Column, func, Integer
from sqlalchemy.ext.declarative import declared_attr

from pypi_portal.extensions import db


class Base(db.Model):
  """Convenience base DB model class. Makes sure tables in MySQL are created as InnoDB.

  This is to enforce foreign key constraints (MyISAM doesn't support constraints) outside of
  production. Tables are also named to avoid collisions.
  """

  @declared_attr
  def __tablename__(self):
    return '{}_{}'.format(self.__module__.split('.')[-1], self.__name__.lower())

  __abstract__ = True  # Ignore checkstyle.
  __table_args__ = dict(mysql_charset='utf8', mysql_engine='InnoDB')  # Ignore checkstyle.
  id = Column(Integer, primary_key=True, autoincrement=True, nullable=True)


def count(column, value, glob=False):
  """Counts number of rows with value in a column. This function is case-insensitive.

  Positional arguments:
  column -- the SQLAlchemy column object to search in (e.g. Table.a_column).
  value -- the value to search for, any string.

  Keyword arguments:
  glob -- enable %globbing% search (default False).

  Returns:
  Number of rows that match. Equivalent of SELECT count(*) FROM.
  """
  query = db.session.query(func.count('*'))
  if glob:
    query = query.filter(column.ilike(value))
  else:
    query = query.filter(func.lower(column) == value.lower())
  return query.one()[0]
