from pathlib import Path

from paper_daily_fetch.figures import select_figure_from_html


def test_select_figure_prefers_overview_caption():
    html = Path("tests/fixtures/arxiv_page_with_code_and_figures.html").read_text()

    figure = select_figure_from_html(
        html,
        base_url="https://arxiv.org/html/2603.00001v1",
    )

    assert figure.url == "https://arxiv.org/figures/fig2.png"
    assert figure.reason == "matched:overview"


def test_select_figure_falls_back_to_first_image():
    html = Path("tests/fixtures/arxiv_page_without_code.html").read_text()

    figure = select_figure_from_html(
        html,
        base_url="https://arxiv.org/html/2603.00001v1",
    )

    assert figure.url == "https://arxiv.org/figures/fig0.png"
    assert figure.reason == "fallback:first-image"

