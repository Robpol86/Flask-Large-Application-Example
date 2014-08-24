from pypi_portal.extensions import db
from pypi_portal.models.helpers import count
from pypi_portal.models.pypi import Package


def test_count():
    Package.query.delete()
    db.session.commit()

    assert 0 == count(Package.name, '')
    assert 0 == count(Package.name, '%')
    assert 0 == count(Package.name, '%', True)

    db.session.add(Package(name='packageA', summary='Test Package', latest_version='1.0.0'))
    db.session.commit()

    assert 0 == count(Package.name, '%')
    assert 1 == count(Package.name, '%', True)

    db.session.add(Package(name='packageB', summary='Test Package', latest_version='1.0.0'))
    db.session.commit()

    assert 0 == count(Package.name, 'package')
    assert 1 == count(Package.name, 'packagea')
    assert 0 == count(Package.name, 'package%')
    assert 2 == count(Package.name, 'package%', True)
