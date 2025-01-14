from streamlit.testing.v1 import AppTest

def test_app():
    at = AppTest.from_file("streamlit.py").run()
    assert not at.exception