import pytest
import pytest_golden.yaml

from datetime import datetime

from bs4 import BeautifulSoup

from vactracher import App, Infos, Info, extract_info

pytest_golden.yaml.register_class(Infos)
pytest_golden.yaml.register_class(Info)

app = App(None, None, None, None, None)


@pytest.mark.golden_test("templates_test/*.yml")
def test_render_tweet(golden):
    assert app.render_tweet(golden["input"], "en_US") == golden.out["output"]


def test_extract_info(golden):
    h = """
        <table class="bag-key-value-list__table">
            <!---->
            <tbody>
                <tr class="">
                    <th><span class="bag-key-value-list__entry-key"><!----><span>Received vaccine doses</span></span><span class="bag-key-value-list__entry-key-description">Source: AFLO – Status: 17.03.2021, 18.00h</span>
                        <!---->
                    </th>
                    <td><span class="bag-key-value-list__entry-value">1 388 325</span>
                        <!---->
                    </td>
                </tr>
                <tr class="">
                    <th><span class="bag-key-value-list__entry-key"><span aria-hidden="true" class="bag-key-value-list__color-square" style="background-color:#6D9B6C;"></span>
                        <!----><span>Vaccine doses delivered to cantons and FL</span></span><span class="bag-key-value-list__entry-key-description">Source: AFLO – Status: 17.03.2021, 18.00h</span>
                        <!---->
                    </th>
                    <td><span class="bag-key-value-list__entry-value">1 336 275</span>
                        <!---->
                    </td>
                </tr>
                <tr class="">
                    <th><span class="bag-key-value-list__entry-key"><span aria-hidden="true" class="bag-key-value-list__color-square" style="background-color:#C2DABD;"></span>
                        <!----><span>Administered vaccine doses</span></span><span class="bag-key-value-list__entry-key-description">Source: FOPH – Status: 17.03.2021, 23.59h</span>
                        <!---->
                    </th>
                    <td><span class="bag-key-value-list__entry-value">1 181 090</span>
                        <!---->
                    </td>
                </tr>
                <tr class="">
                    <th><span class="bag-key-value-list__entry-key"><!----><span>Fully vaccinated people</span></span><span class="bag-key-value-list__entry-key-description">Source: FOPH – Status: 17.03.2021, 23.59h</span>
                        <!---->
                    </th>
                    <td><span class="bag-key-value-list__entry-value">433 411</span>
                        <!---->
                    </td>
                </tr>
                <!---->
            </tbody>
        </table>
    """
    s = BeautifulSoup(h, features="html.parser")
    assert extract_info(s, "Vaccine doses delivered to cantons and FL") == Info(
        1336275, datetime(2021, 3, 17, 18, 0), "AFLO"
    )
    assert extract_info(s, "Administered vaccine doses") == Info(
        1181090, datetime(2021, 3, 17, 23, 59), "FOPH"
    )
    assert extract_info(s, "Fully vaccinated people") == Info(
        433411, datetime(2021, 3, 17, 23, 59), "FOPH"
    )
