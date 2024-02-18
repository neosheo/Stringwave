import pytest
import os

def test_initial_setup():
    assert os.path.isdir('/stringwave/config')
    assert os.path.isfile('/stringwave/config/ezstream-main.xml')
    assert os.path.isfile('/stringwave/config/ezstream-new.xml')
    assert os.path.isfile('/stringwave/config/icecast.xml')
    assert os.path.isdir('/stringwave/dl_data')
    assert os.path.isfile('/stringwave/dl_data/urls')
    assert os.path.isfile('/stringwave/dl_data/search_queries')
