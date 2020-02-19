import pytest


@pytest.fixture(params=[
    ('2013-06-18T00:00:00', 2013, 6, 18),
    ('2014-02-15T00:00:00', 2014, 2, 15),
    ('1989-10-02T00:00:00', 1989, 10, 2),
])
def datas_nascimento_api(request):
    return request.param
