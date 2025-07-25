"""Command-line interface for XML Inspector DSL validation."""

import sys
from pathlib import Path
from typing import List, Optional
import logging

import click
from colorama import Fore, Style, init as colorama_init

from .core.inspector import XmlInspector, InspectionOptions, InspectionError
from .parsers.settings_parser import SettingsParseError
from .types import DslValidationSettings

# Initialize colorama for cross-platform colored output
colorama_init(autoreset=True)

# Set up logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def validate_file_exists(file_path: str) -> None:
    """Validate that a file exists and is readable."""
    path = Path(file_path)
    if not path.exists():
        raise click.BadParameter(f"File not found: {file_path}")
    if not path.is_file():
        raise click.BadParameter(f"Path is not a file: {file_path}")


def validate_files_exist(file_paths: List[str]) -> None:
    """Validate that all files in a list exist and are readable."""
    for file_path in file_paths:
        validate_file_exists(file_path)


@click.group()
@click.version_option(version="1.0.0")
@click.option(
    "--verbose", "-v", 
    is_flag=True, 
    help="Enable verbose output"
)
def cli(verbose: bool) -> None:
    """XML Inspector - DSL-based quality assurance tool for XML files."""
    if verbose:
        logging.getLogger().setLevel(logging.INFO)


@cli.command()
@click.option(
    "--xml", "-x",
    multiple=True,
    required=True,
    help="XML files to inspect (can be specified multiple times)"
)
@click.option(
    "--dsl", "-d",
    required=True,
    help="DSL validation document (JSON format)"
)
@click.option(
    "--output", "-o",
    help="Output file path for the report"
)
@click.option(
    "--format", "-f", "output_format",
    type=click.Choice(["json", "html"]),
    default="json",
    help="Output format for the report"
)
def inspect(
    xml: tuple,
    dsl: str,
    output: Optional[str],
    output_format: str
) -> None:
    """Inspect XML files against DSL validation rules."""
    try:
        # Validate input files
        xml_files = list(xml)
        validate_files_exist(xml_files)
        validate_file_exists(dsl)
        
        # Create inspector and options
        inspector = XmlInspector()
        options = InspectionOptions(
            xml_files=xml_files,
            dsl_settings_file=dsl,
            output_path=output,
            output_format=output_format  # type: ignore
        )
        
        # Display inspection info
        click.echo(f"{Fore.BLUE}🔍 Starting DSL-based XML inspection...")
        click.echo(f"{Fore.CYAN}XML Files: {', '.join(xml_files)}")
        click.echo(f"{Fore.CYAN}DSL Document: {dsl}")
        
        # Perform inspection
        report = inspector.inspect(options)
        
        # Display results
        click.echo(f"\n{Fore.GREEN}✅ Inspection completed!")
        click.echo(f"\n{Fore.BLUE}📊 Summary:")
        click.echo(f"  Total Checks: {report.summary.total_checks}")
        click.echo(f"  {Fore.GREEN}Passed: {report.summary.passed}")
        click.echo(f"  {Fore.RED}Failed: {report.summary.failed}")
        click.echo(f"  {Fore.YELLOW}Missing: {report.summary.missing}")
        
        if output:
            click.echo(f"\n{Fore.BLUE}📄 Report saved to: {output}")
        
        # Exit with error code if there are issues
        if report.summary.failed > 0 or report.summary.missing > 0:
            click.echo(f"\n{Fore.RED}⚠️  Issues found! Check the detailed report for more information.")
            sys.exit(1)
        else:
            click.echo(f"\n{Fore.GREEN}🎉 All checks passed!")
        
    except (InspectionError, SettingsParseError) as e:
        click.echo(f"{Fore.RED}❌ Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}❌ Unexpected error: {e}", err=True)
        logger.exception("Unexpected error during inspection")
        sys.exit(1)


@cli.command()
@click.option(
    "--file", "-f",
    required=True,
    help="DSL validation document to validate (JSON format)"
)
def validate_settings(file: str) -> None:
    """Validate a DSL document structure."""
    try:
        validate_file_exists(file)
        
        inspector = XmlInspector()
        
        click.echo(f"{Fore.BLUE}🔍 Validating DSL document...")
        settings_doc = inspector.validate_settings_document(file)
        
        click.echo(f"{Fore.GREEN}✅ DSL document is valid!")
        click.echo(f"\n{Fore.BLUE}📋 Document Info:")
        click.echo(f"  Validation Rules Count: {len(settings_doc.validation_settings)}")
        
        # Show rule type breakdown
        rule_types = {}
        for rule in settings_doc.validation_settings:
            rule_types[rule.type] = rule_types.get(rule.type, 0) + 1
        
        if rule_types:
            click.echo(f"  Rule Types:")
            for rule_type, count in rule_types.items():
                click.echo(f"    {rule_type}: {count}")
        
    except (InspectionError, SettingsParseError) as e:
        click.echo(f"{Fore.RED}❌ Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}❌ Unexpected error: {e}", err=True)
        logger.exception("Unexpected error during DSL validation")
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()