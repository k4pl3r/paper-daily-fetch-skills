from __future__ import annotations

from .models import PaperRecord


def _escape_md(text: str) -> str:
    """Escape Markdown link/image-syntax special characters in plain text."""
    return text.replace("[", "\\[").replace("]", "\\]")


def render_openclaw_payload(
    papers: list[PaperRecord],
    target_chat: str | None,
    topic_name: str,
) -> dict[str, object]:
    lines = [f"今日论文速递：{topic_name}", ""]
    for index, paper in enumerate(papers, start=1):
        summary = paper.summary_zh or paper.abstract
        lines.extend(
            [
                f"{index}. {paper.title}",
                f"   主题：{', '.join(paper.topic_matches) if paper.topic_matches else '未命中'}",
                f"   摘要：{summary}",
                f"   贡献：{paper.positive_take or '待补充'}",
                f"   锐评：{paper.critical_take or '待补充'}",
                f"   论文：{paper.paper_url}",
                f"   代码：{paper.code_url or '暂无'}",
                f"   配图：{paper.figure_url_or_path or '暂无'}",
                "",
            ]
        )
    return {
        "target_chat": target_chat,
        "message": "\n".join(lines).strip(),
        "papers": [paper.to_dict() for paper in papers],
    }


def render_markdown(
    papers: list[PaperRecord],
    topic_name: str,
    generated_at: str,
) -> str:
    lines = [
        f"# 每日论文速递：{topic_name}",
        "",
        f"- 生成时间：{generated_at}",
        f"- 论文数量：{len(papers)}",
        "",
    ]
    for paper in papers:
        summary = paper.summary_zh or paper.abstract
        lines.extend(
            [
                f"## {paper.title}",
                "",
                f"- arXiv ID：{paper.arxiv_id}",
                f"- 作者：{', '.join(paper.authors) if paper.authors else '未知'}",
                f"- 发布时间：{paper.published_at}",
                f"- 匹配主题：{', '.join(paper.topic_matches)}",
                f"- 论文链接：[{paper.paper_url}]({paper.paper_url})",
                f"- 代码链接：[{paper.code_url}]({paper.code_url})" if paper.code_url else "- 代码链接：暂无",
            ]
        )
        if paper.figure_url_or_path:
            lines.append(f"- 配图：![{_escape_md(paper.title)}]({paper.figure_url_or_path})")
        else:
            lines.append("- 配图：暂无")
        if paper.figure_reason:
            lines.append(f"- 配图说明：{paper.figure_reason}")
        else:
            lines.append("- 配图说明：暂无")
        lines.extend(["", "### 中文摘要", "", summary])
        lines.extend(["", "### 一句话总结贡献（正面）", "", paper.positive_take or "待由宿主 Agent 补充"])
        lines.extend(["", "### 毒舌锐评和其他方法的差异与不足（负面）", "", paper.critical_take or "待由宿主 Agent 补充"])
    return "\n".join(lines) + "\n"
