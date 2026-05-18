from services.tests.mini_test_engine import build_final_mini_test


def test_final_mini_test_has_four_questions():
    text = build_final_mini_test()
    assert "1)" in text
    assert "2)" in text
    assert "3)" in text
    assert "4)" in text
