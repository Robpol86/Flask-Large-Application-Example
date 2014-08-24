from flask import current_app, render_template_string


def test_template_filters():
    template = """
        Dollar: {{ 0.1 | dollar }}<br>
        Sum Key: {{ data | sum_key('col') }}<br>
        Max Key: {{ data | max_key('col') }}<br>
        Average Key: {{ data | average_key('col') }}<br>
    """

    data = [
        dict(col=0),
        dict(col=0.5),
        dict(col=0.5),
        dict(col=1),
    ]

    with current_app.app_context():
        html = render_template_string(template, data=data)

    assert 'Dollar: $0.10<br>' in html
    assert 'Sum Key: 2.0<br>' in html
    assert 'Max Key: 1<br>' in html
    assert 'Average Key: 0.5<br>' in html
