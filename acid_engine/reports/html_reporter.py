# acid_engine/reports/html_reporter.py
# Улучшенный HTML-отчёт с графиками (Chart.js)

class HTMLReporter:
    def __init__(self, project_name, project_version):
        self.project_name = project_name
        self.project_version = project_version
        self.sections = []
        self._total_pass = 0
        self._total_fail = 0
        self._total_skipped = 0
        self._violations_labels = []
        self._violations_data = []

    def add_summary(self, total_pass, total_fail, total_skipped):
        self._total_pass = total_pass
        self._total_fail = total_fail
        self._total_skipped = total_skipped
        self.sections.append(f"""
        <div class="summary">
            <h2>Overall Statistics</h2>
            <div class="stats">
                <div class="stat pass">{total_pass}<span>PASS</span></div>
                <div class="stat fail">{total_fail}<span>FAIL</span></div>
                <div class="stat skipped">{total_skipped}<span>SKIPPED</span></div>
            </div>
            <div class="chart-container" style="width: 300px; margin: 20px auto;">
                <canvas id="summaryChart"></canvas>
            </div>
        </div>
        """)

    def add_top_violations(self, violations):
        rows = ""
        labels = []
        data = []
        for msg, count in violations:
            short_msg = (msg[:30] + "...") if len(msg) > 30 else msg
            rows += f"<tr><td>{msg}</td><td>{count}</td></tr>"
            labels.append(short_msg)
            data.append(count)
        self._violations_labels = labels
        self._violations_data = data
        self.sections.append(f"""
        <div class="violations">
            <h2>Top Violations</h2>
            <table id="violationsTable">
                <thead><tr><th>Violation</th><th>Count</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
            <div class="chart-container" style="width: 400px; margin: 20px auto;">
                <canvas id="violationsChart"></canvas>
            </div>
        </div>
        """)

    def add_error_examples(self, errors):
        examples = ""
        for err in errors[:5]:
            examples += f"""
            <div class="error-card">
                <div class="error-row"><strong>Row:</strong> {err.get('row', {})}</div>
                <div class="error-reason"><strong>Reason:</strong> {err.get('reason', 'N/A')}</div>
                <div class="error-expected"><strong>Expected:</strong> {err.get('expected', 'N/A')}</div>
                <div class="error-received"><strong>Received:</strong> {err.get('received', 'N/A')}</div>
            </div>
            """
        self.sections.append(f"""
        <div class="errors">
            <h2>Error Examples</h2>
            {examples}
        </div>
        """)

    def render(self):
        charts_script = ""
        if self._violations_labels:
            charts_script = f"""
            <script>
            var ctx1 = document.getElementById('summaryChart').getContext('2d');
            new Chart(ctx1, {{
                type: 'doughnut',
                data: {{
                    labels: ['PASS', 'FAIL', 'SKIPPED'],
                    datasets: [{{
                        data: [{self._total_pass}, {self._total_fail}, {self._total_skipped}],
                        backgroundColor: ['#2ecc71', '#e74c3c', '#f39c12']
                    }}]
                }}
            }});
            var ctx2 = document.getElementById('violationsChart').getContext('2d');
            new Chart(ctx2, {{
                type: 'bar',
                data: {{
                    labels: {self._violations_labels},
                    datasets: [{{
                        label: 'Violations',
                        data: {self._violations_data},
                        backgroundColor: '#e74c3c'
                    }}]
                }}
            }});
            </script>
            """
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AcidEngine Report – {self.project_name} v{self.project_version}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.08); padding: 30px; }}
        h1 {{ color: #1a1a2e; margin-bottom: 8px; }}
        h2 {{ color: #333; border-bottom: 1px solid #eee; padding-bottom: 6px; margin-top: 32px; }}
        .version {{ color: #666; font-size: 14px; }}
        .stats {{ display: flex; gap: 20px; margin-top: 16px; }}
        .stat {{ flex: 1; padding: 20px; border-radius: 10px; text-align: center; font-size: 28px; font-weight: bold; color: white; }}
        .stat span {{ display: block; font-size: 14px; font-weight: normal; margin-top: 6px; opacity: 0.9; }}
        .pass {{ background: #2ecc71; }}
        .fail {{ background: #e74c3c; }}
        .skipped {{ background: #f39c12; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; font-weight: 600; cursor: pointer; }}
        th:hover {{ background: #e9ecef; }}
        .error-card {{ background: #fff5f5; border-left: 4px solid #e74c3c; padding: 12px; margin: 12px 0; border-radius: 6px; }}
        .error-card div {{ margin: 4px 0; }}
        .error-reason {{ color: #c0392b; }}
        .error-expected {{ color: #27ae60; }}
        .error-received {{ color: #e67e22; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>AcidEngine Execution Report</h1>
        <div class="version">Project: {self.project_name} v{self.project_version}</div>
        {''.join(self.sections)}
    </div>
    {charts_script}
</body>
</html>"""