"""Command-line interface for XML Inspector Python validation."""

import sys
from pathlib import Path
from typing import List, Optional, Tuple
import logging

import click
from colorama import Fore, Style, init as colorama_init

from .core.inspector import XmlInspector, InspectionOptions, InspectionError
from .parsers.python_settings_parser import SettingsParseError
from .config.function_loader import FunctionLoader, FunctionRegistrationError
from .types import ValidationSettings
# No built-in validation rules imported

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


def register_custom_functions(inspector: XmlInspector, functions_config: Optional[str] = None, 
                             verbose: bool = False) -> Tuple[int, List[str]]:
    """
    Register custom validation functions from configuration file.
    
    Args:
        inspector: XmlInspector instance
        functions_config: Path to functions config file (auto-discovered if None)
        verbose: Whether to show detailed loading information
        
    Returns:
        Tuple of (registered_count, error_messages)
    """
    # Find configuration file if not specified
    if not functions_config:
        functions_config = FunctionLoader.find_config_file()
    
    if not functions_config or not Path(functions_config).exists():
        return 0, []
        
    try:
        validator = inspector.get_validator()
        registered_count, error_messages = FunctionLoader.register_functions_from_config(
            validator, functions_config, verbose
        )
        
        if verbose and registered_count > 0:
            click.echo(f"{Fore.GREEN}✅ Registered {registered_count} custom validation functions")
            if functions_config:
                click.echo(f"{Fore.CYAN}   From config: {functions_config}")
        
        if error_messages and verbose:
            for error_msg in error_messages:
                click.echo(f"{Fore.YELLOW}⚠️  Warning: {error_msg}")
        
        return registered_count, error_messages
        
    except FunctionRegistrationError as e:
        error_messages = [str(e)]
        if verbose:
            click.echo(f"{Fore.YELLOW}⚠️  Function registration failed: {e}")
        return 0, error_messages


@click.group()
@click.version_option(version="1.0.0")
@click.option(
    "--verbose", "-v", 
    is_flag=True, 
    help="Enable verbose output"
)
def cli(verbose: bool) -> None:
    """XML Inspector - Python-based quality assurance tool for XML files."""
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
    "--settings", "-s",
    required=True,
    help="Validation settings document (JSON format)"
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
@click.option(
    "--functions-config", "-c",
    help="Configuration file for custom validation functions"
)
@click.option(
    "--verbose-loading",
    is_flag=True,
    help="Show detailed function loading information"
)
def inspect(
    xml: tuple,
    settings: str,
    output: Optional[str],
    output_format: str,
    functions_config: Optional[str],
    verbose_loading: bool
) -> None:
    """Inspect XML files against Python validation rules."""
    try:
        # Validate input files
        xml_files = list(xml)
        validate_files_exist(xml_files)
        validate_file_exists(settings)
        
        # Create inspector
        inspector = XmlInspector()
        
        # Register custom validation functions
        registered_count, error_messages = register_custom_functions(
            inspector, functions_config, verbose_loading
        )
        
        validator = inspector.get_validator()
        
        options = InspectionOptions(
            xml_files=xml_files,
            settings_file=settings,
            output_path=output,
            output_format=output_format  # type: ignore
        )
        
        # Display inspection info
        click.echo(f"{Fore.BLUE}🔍 Starting Python-based XML inspection...")
        click.echo(f"{Fore.CYAN}XML Files: {', '.join(xml_files)}")
        click.echo(f"{Fore.CYAN}Settings Document: {settings}")
        
        # Show function registration info
        if registered_count > 0:
            config_path = functions_config or FunctionLoader.find_config_file()
            if config_path:
                click.echo(f"{Fore.CYAN}Functions Config: {config_path}")
        elif verbose_loading:
            click.echo(f"{Fore.YELLOW}No custom validation functions registered")
        
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
    help="Validation settings document to validate (JSON format)"
)
@click.option(
    "--functions-config", "-c",
    help="Configuration file for custom validation functions"
)
def validate_settings(file: str, functions_config: Optional[str]) -> None:
    """Validate a settings document structure."""
    try:
        validate_file_exists(file)
        
        inspector = XmlInspector()
        
        # Register custom validation functions for more complete validation
        registered_count, _ = register_custom_functions(inspector, functions_config, verbose=False)
        
        click.echo(f"{Fore.BLUE}🔍 Validating settings document...")
        settings_doc = inspector.validate_settings_document(file)
        
        click.echo(f"{Fore.GREEN}✅ Settings document is valid!")
        click.echo(f"\n{Fore.BLUE}📋 Document Info:")
        click.echo(f"  Validation Rules Count: {len(settings_doc.validation_rules)}")
        
        # Show available rules
        validator = inspector.get_validator()
        available_rules = validator.get_registered_rules()
        
        click.echo(f"  Available Rules: {', '.join(available_rules)}")
        
        # Check for unknown rules
        unknown_rules = [rule for rule in settings_doc.validation_rules if rule not in available_rules]
        if unknown_rules:
            click.echo(f"  {Fore.YELLOW}⚠️  Unknown Rules: {', '.join(unknown_rules)}")
            if not functions_config and not FunctionLoader.find_config_file():
                click.echo(f"  {Fore.YELLOW}   Consider adding a functions configuration file")
                click.echo(f"  {Fore.YELLOW}   Use --functions-config to specify custom validation functions")
        
        # Show registration info
        if registered_count > 0:
            config_path = functions_config or FunctionLoader.find_config_file()
            click.echo(f"  Custom Functions: {registered_count} registered from {config_path}")
        
    except (InspectionError, SettingsParseError) as e:
        click.echo(f"{Fore.RED}❌ Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}❌ Unexpected error: {e}", err=True)
        logger.exception("Unexpected error during settings validation")
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()