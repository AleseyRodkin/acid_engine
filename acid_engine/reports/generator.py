class ReportGenerator:
    """Генерирует Markdown-отчёт по результатам выполнения контракта."""

    def __init__(self, ast, stage_reports, logger=None):
        self.ast = ast
        self.stage_reports = stage_reports  # список словарей {stage_name, report}
        self.logger = logger

    def generate_markdown(self, output_file="report.md"):
        lines = []
        lines.append(f"# AcidEngine Execution Report")
        lines.append(f"**Project:** {self.ast['project']['name']} v{self.ast['project']['version']}")
        lines.append("")

        # Статистика по всем стадиям
        total_pass = 0
        total_fail = 0
        total_skipped = 0
        for sr in self.stage_reports:
            r = sr["report"]
            total_pass += r["pass"]
            total_fail += r["fail"]
            total_skipped += r["skipped"]

        lines.append("## Overall Statistics")
        lines.append(f"- **Total PASS:** {total_pass}")
        lines.append(f"- **Total FAIL:** {total_fail}")
        lines.append(f"- **Total SKIPPED:** {total_skipped}")
        lines.append("")

        # Детали по каждой стадии
        lines.append("## Stage Details")
        for sr in self.stage_reports:
            r = sr["report"]
            lines.append(f"### {sr['stage_name']}")
            lines.append(f"- PASS: {r['pass']}")
            lines.append(f"- FAIL: {r['fail']}")
            lines.append(f"- SKIPPED: {r['skipped']}")
            lines.append("")

        # TODO: добавить топ ошибок из ErrorRecord, если появятся

        md = "\n".join(lines)
        with open(output_file, "w") as f:
            f.write(md)
        return md