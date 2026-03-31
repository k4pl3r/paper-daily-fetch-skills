from paper_daily_fetch.figures import select_figure_from_html


def test_select_figure_from_html_ignores_nested_images_in_svg_composites():
    html = (
        '<figure>'
        '<svg><foreignObject><img src="images/preview.png" /></foreignObject></svg>'
        '<figcaption>Overview of PiJEPA.</figcaption>'
        '</figure>'
    )

    assert select_figure_from_html(html, "https://arxiv.org/html/2603.25981v1/") is None


def test_select_figure_from_html_prefers_pdf_fallback_over_unrelated_later_images():
    html = (
        '<figure>'
        '<svg><foreignObject><img src="images/preview.png" /></foreignObject></svg>'
        '<figcaption>Overview of PiJEPA.</figcaption>'
        '</figure>'
        '<figure>'
        '<img src="images/frame_00.png" />'
        '<figcaption>Qualitative trajectory comparison.</figcaption>'
        '</figure>'
    )

    assert select_figure_from_html(html, "https://arxiv.org/html/2603.25981v1/") is None
