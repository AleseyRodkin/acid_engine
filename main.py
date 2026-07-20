import sys, csv
from acid_engine.parser.parser import parse_contract
from acid_engine.runtime.runner import StageRunner
from acid_engine.logger import AcidLogger
from acid_engine.reports.html_reporter import HTMLReporter
from acid_engine.testing.test_generator import ContractTestGenerator
from acid_engine.exporters.excel_exporter import export_to_excel

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py <contract.ae> --input <data.csv> [--generate-tests]")
        sys.exit(1)

    contract_file = sys.argv[1]
    generate_tests = "--generate-tests" in sys.argv
    input_file = None
    for i, arg in enumerate(sys.argv):
        if arg == "--input":
            input_file = sys.argv[i+1]
            break

    if not generate_tests and not input_file:
        print("Please specify --input <data.csv> or --generate-tests")
        sys.exit(1)

    logger = AcidLogger()
    logger.log({"event": "run_start", "contract": contract_file, "input": input_file})

    ast = parse_contract(contract_file)
    ast["_source_file"] = contract_file

    if generate_tests:
        gen = ContractTestGenerator(ast)
        output = gen.generate("test_contract.py")
        print(f"Tests generated: {output}")
        sys.exit(0)

    sources = {}
    for src in ast.get("input", []):
        name = src["name"]
        path = f"{name}.csv"
        sources[name] = path

    main_source_name = ast["input"][0]["name"] if ast["input"] else "orders"
    main_file = sources.get(main_source_name, input_file)

    with open(main_file, 'r') as f:
        data = list(csv.DictReader(f))

    all_errors = []
    overall_pass = overall_fail = overall_skipped = 0

    for stage_ast in ast["implementation"]:
        runner = StageRunner(stage_ast, sources=sources, logger=logger)
        validated, report, errors = runner.run(data, collect_errors=True)
        print(f"Stage: {stage_ast['name']}")
        print(f"PASS: {report['pass']}, FAIL: {report['fail']}, SKIPPED: {report['skipped']}")
        overall_pass += report['pass']
        overall_fail += report['fail']
        overall_skipped += report['skipped']
        all_errors.extend(errors)

    project_name = ast['project']['name']
    project_version = ast['project']['version']

    # HTML-отчёт
    reporter = HTMLReporter(project_name, project_version)
    reporter.add_summary(overall_pass, overall_fail, overall_skipped)
    if all_errors:
        error_counts = {}
        for err in all_errors:
            msg = err.get("message", "Unknown error")
            error_counts[msg] = error_counts.get(msg, 0) + 1
        top_violations = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        reporter.add_top_violations(top_violations)
        reporter.add_error_examples(all_errors)
    with open("report.html", "w") as f:
        f.write(reporter.render())

    # Markdown-отчёт
    report_lines = []
    report_lines.append("# AcidEngine Execution Report")
    report_lines.append(f"**Project:** {project_name} v{project_version}")
    report_lines.append("")
    report_lines.append("## Overall Statistics")
    report_lines.append(f"- **Total PASS:** {overall_pass}")
    report_lines.append(f"- **Total FAIL:** {overall_fail}")
    report_lines.append(f"- **Total SKIPPED:** {overall_skipped}")
    report_lines.append("")
    if all_errors:
        error_counts = {}
        for err in all_errors:
            msg = err.get("message", "Unknown error")
            error_counts[msg] = error_counts.get(msg, 0) + 1
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        report_lines.append("## Top Violations")
        for msg, count in sorted_errors:
            report_lines.append(f"- {msg}: {count}")
        report_lines.append("")
        report_lines.append("## Error Examples (first 3)")
        for err in all_errors[:3]:
            row = err.get("row", {})
            report_lines.append(f"### Row: {row}")
            if "reason" in err:
                report_lines.append(f"- Reason: {err['reason']}")
            if "expected" in err:
                report_lines.append(f"- Expected: {err['expected']}")
            if "received" in err:
                report_lines.append(f"- Received: {err['received']}")
            report_lines.append("")
    with open("report.md", "w") as f:
        f.write("\n".join(report_lines))

    # Excel-отчёт
    if all_errors:
        try:
            export_to_excel(all_errors, "validation_report.xlsx")
            print("Excel report saved to validation_report.xlsx")
        except Exception as e:
            print(f"Excel export failed: {e}")

    logger.log({"event": "run_end"})