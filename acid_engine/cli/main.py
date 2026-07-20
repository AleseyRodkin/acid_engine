import sys, os, csv, argparse
from acid_engine.parser.parser import parse_contract
from acid_engine.runtime.runner import StageRunner
from acid_engine.logger import AcidLogger
from acid_engine.reports.html_reporter import HTMLReporter
from acid_engine.testing.test_generator import ContractTestGenerator
from acid_engine.exporters.json_schema import to_json_schema_string
from acid_engine.exporters.pydantic_exporter import to_pydantic_model
from acid_engine.diff import diff_contracts
from acid_engine.modules.core import ModuleCore
from acid_engine.testing.manifest_tester import ManifestTestGenerator
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description='AcidEngine CLI – Contract-Driven Data Control')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Команда run
    run_parser = subparsers.add_parser('run', help='Запустить пайплайн')
    run_parser.add_argument('target', help='Путь к .ae файлу или директории модуля')
    run_parser.add_argument('--input', help='Путь к CSV файлу с данными (для .ae)')
    run_parser.add_argument('--module', action='store_true', help='Запустить как ModuleCore (директория)')
    run_parser.add_argument('--output-html', default='report.html', help='Путь к HTML отчёту')
    run_parser.add_argument('--output-md', default='report.md', help='Путь к Markdown отчёту')
    run_parser.add_argument('--output-xlsx', default='validation_report.xlsx', help='Путь к Excel отчёту')

    # Команда diff
    diff_parser = subparsers.add_parser('diff', help='Сравнить два контракта')
    diff_parser.add_argument('old', help='Старый контракт .ae')
    diff_parser.add_argument('new', help='Новый контракт .ae')

    # Команда export
    export_parser = subparsers.add_parser('export', help='Экспортировать контракт')
    export_parser.add_argument('contract', help='Путь к .ae файлу')
    export_parser.add_argument('--format', choices=['json-schema', 'pydantic'], required=True, help='Формат экспорта')
    export_parser.add_argument('--output', default='exported', help='Файл для сохранения (без расширения)')

    # Команда test
    test_parser = subparsers.add_parser('test', help='Генерировать тесты')
    test_parser.add_argument('contract', help='Путь к .ae файлу')
    test_parser.add_argument('--output', default='test_contract.py', help='Путь к файлу с тестами')

    # Команда manifest-test
    manifest_test_parser = subparsers.add_parser('manifest-test', help='Генерировать интеграционные тесты из манифеста')
    manifest_test_parser.add_argument('module_dir', help='Путь к директории модуля')
    manifest_test_parser.add_argument('--output', default='test_module_integration.py', help='Путь к файлу с тестами')

    args = parser.parse_args()

    if args.command == 'run':
        _handle_run(args)
    elif args.command == 'diff':
        _handle_diff(args)
    elif args.command == 'export':
        _handle_export(args)
    elif args.command == 'test':
        _handle_test(args)
    elif args.command == 'manifest-test':
        gen = ManifestTestGenerator(args.module_dir)
        output = gen.generate(args.output)
        print(f"Integration tests generated: {output}")

def _handle_run(args):
    if args.module:
        if not os.path.isdir(args.target):
            print(f"Error: {args.target} is not a directory")
            sys.exit(1)
        if not args.input:
            print("Error: --input is required for module mode")
            sys.exit(1)
        df = pd.read_csv(args.input)
        module = ModuleCore(args.target, hot_reload=True, resume=True)
        result = module.execute(df)
        print("Result:\n", result)
        print(module.report())
        result.to_csv("module_output.csv", index=False)
        print("Output saved to module_output.csv")
    else:
        if not args.input:
            print("Error: --input is required for .ae mode")
            sys.exit(1)
        logger = AcidLogger()
        logger.log({"event": "run_start", "contract": args.target, "input": args.input})

        ast = parse_contract(args.target)

        with open(args.input, 'r') as f:
            data = list(csv.DictReader(f))

        sources = {}
        for src in ast.get("input", []):
            name = src["name"]
            sources[name] = f"{name}.csv"

        all_errors = []
        total_pass = total_fail = total_skipped = 0

        for stage_ast in ast["implementation"]:
            runner = StageRunner(stage_ast, sources=sources, logger=logger)
            validated, report, errors = runner.run(data, collect_errors=True)
            print(f"Stage: {stage_ast['name']}")
            print(f"  PASS: {report['pass']}, FAIL: {report['fail']}, SKIPPED: {report['skipped']}")
            total_pass += report['pass']
            total_fail += report['fail']
            total_skipped += report['skipped']
            all_errors.extend(errors)

        reporter = HTMLReporter(ast['project']['name'], ast['project']['version'])
        reporter.add_summary(total_pass, total_fail, total_skipped)
        if all_errors:
            from collections import Counter
            error_counts = Counter(err.get("message", "Unknown") for err in all_errors)
            top_violations = error_counts.most_common(5)
            reporter.add_top_violations(top_violations)
            reporter.add_error_examples(all_errors)
        with open(args.output_html, "w") as f:
            f.write(reporter.render())
        print(f"HTML report: {args.output_html}")

def _handle_diff(args):
    old_ast = parse_contract(args.old)
    new_ast = parse_contract(args.new)
    from acid_engine.core import Contract, Field
    def ast_to_contract(ast):
        schema = {}
        for stage in ast.get("implementation", []):
            for field_def in stage.get("schema", []):
                if isinstance(field_def, dict):
                    f_type = field_def.get("value")
                    if f_type == "integer":
                        schema[field_def["field"]] = Field(type=int)
                    elif f_type == "float":
                        schema[field_def["field"]] = Field(type=float)
                    else:
                        schema[field_def["field"]] = Field(type=str)
            break
        return Contract(schema=schema)
    old_contract = ast_to_contract(old_ast)
    new_contract = ast_to_contract(new_ast)
    print(diff_contracts(old_contract, new_contract))

def _handle_export(args):
    ast = parse_contract(args.contract)
    from acid_engine.core import Contract, Field
    schema = {}
    for stage in ast.get("implementation", []):
        for field_def in stage.get("schema", []):
            if isinstance(field_def, dict):
                f_type = field_def.get("value")
                if f_type == "integer":
                    schema[field_def["field"]] = Field(type=int)
                elif f_type == "float":
                    schema[field_def["field"]] = Field(type=float)
                else:
                    schema[field_def["field"]] = Field(type=str)
        break
    contract = Contract(schema=schema)
    if args.format == 'json-schema':
        output = to_json_schema_string(contract)
        with open(f"{args.output}.json", "w") as f:
            f.write(output)
        print(f"JSON Schema saved to {args.output}.json")
    elif args.format == 'pydantic':
        output = to_pydantic_model(contract)
        with open(f"{args.output}.py", "w") as f:
            f.write(output)
        print(f"Pydantic model saved to {args.output}.py")

def _handle_test(args):
    ast = parse_contract(args.contract)
    ast["_source_file"] = args.contract
    gen = ContractTestGenerator(ast)
    gen.generate(args.output)
    print(f"Tests generated: {args.output}")