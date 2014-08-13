"""Holds all data cached from PyPI."""

from sqlalchemy import BigInteger, Column, Date, ForeignKey, Integer, String, Text

from pypi_portal.models.helpers import Base


class Package(Base):
    """Holds all of the packages on PyPI as shown in https://pypi.python.org/simple/."""
    name = Column(String(255), unique=True, nullable=False)


class PackageDetails(Base):
    """Non-historical details about a package.

    Class variables:
    name -- foreign key to the package name.
    pypi_url -- url to the package's page on PyPI.
    latest_version
    summary
    description
    """
    name = Column(Integer, ForeignKey(Package.id), nullable=False)
    pypi_url = Column(Text, nullable=False)
    latest_version = Column(String(32), nullable=False)
    summary = Column(Text)
    description = Column(Text)


class PackageVersionHistory(Base):
    """Incremental downloads history for a package. Download counts for all versions are summed up."""
    name = Column(Integer, ForeignKey(Package.id), nullable=False)
    date = Column(Date, nullable=False)
    downloads = Column(BigInteger, nullable=False)
