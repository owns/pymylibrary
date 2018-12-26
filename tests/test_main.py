import pytest
import pymylibrary

@pytest.mark.skip("i don't want to run this test")
def test_skipped():
    print('should NOT run!!!')
    assert 0


def test_two_plus_one_is_three():
    print('tests.test_two_plus_one_is_three: hello from test')
    assert 3 == 2+1