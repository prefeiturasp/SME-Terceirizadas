import pytest


@pytest.fixture(params=[
    # codigo eol, total esperado
    ('000213', 246),
    ('094731', 827),
    ('000086', 491)
])
def escola_total_params(request):
    return request.param
