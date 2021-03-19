import pytest
import pytest_golden.yaml

from vactracher import App, Infos

pytest_golden.yaml.register_class(Infos)

app = App(None, None, None, None, None)


@pytest.mark.golden_test("templates_test/*.yml")
def test_render_tweet(golden):
    assert app.render_tweet(golden["input"], "en_US") == golden.out["output"]
