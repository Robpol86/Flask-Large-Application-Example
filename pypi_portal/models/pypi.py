"""Holds all data cached from PyPI."""

from sqlalchemy import Column, String, Text

from pypi_portal.models.helpers import Base


class Package(Base):
    """Holds all of the packages on PyPI."""
    name = Column(String(255), unique=True, nullable=False)
    summary = Column(Text, nullable=False)
    latest_version = Column(String(128), nullable=False)
