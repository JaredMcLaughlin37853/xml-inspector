#!/usr/bin/env node

import { Command } from 'commander';
import { XmlInspector } from './core/inspector';
import * as fs from 'fs';
import * as path from 'path';
import chalk from 'chalk';

const program = new Command();

program
  .name('xml-inspector')
  .description('A quality assurance tool for XML files that validates configuration settings')
  .version('1.0.0');

program
  .command('inspect')
  .description('Inspect XML files against settings documents')
  .requiredOption('-x, --xml <files...>', 'XML files to inspect (space-separated)')
  .requiredOption('-s, --standard <file>', 'Standard settings document (JSON or YAML)')
  .option('-p, --project <file>', 'Project-specific settings document (JSON or YAML)')
  .requiredOption('-t, --type <entityType>', 'Entity type for validation')
  .option('-o, --output <file>', 'Output file path for the report')
  .option('-f, --format <format>', 'Output format (json|html)', 'json')
  .action(async (options) => {
    try {
      validateFiles(options.xml);
      validateFiles([options.standard]);
      if (options.project) {
        validateFiles([options.project]);
      }

      const inspector = new XmlInspector();
      
      console.log(chalk.blue('🔍 Starting XML inspection...'));
      console.log(chalk.gray(`Entity Type: ${options.type}`));
      console.log(chalk.gray(`XML Files: ${options.xml.join(', ')}`));
      console.log(chalk.gray(`Standard Settings: ${options.standard}`));
      if (options.project) {
        console.log(chalk.gray(`Project Settings: ${options.project}`));
      }

      const report = await inspector.inspect({
        xmlFiles: options.xml,
        standardSettingsFile: options.standard,
        projectSettingsFile: options.project,
        entityType: options.type,
        outputPath: options.output,
        outputFormat: options.format
      });

      console.log(chalk.green('\n✅ Inspection completed!'));
      console.log(chalk.blue('\n📊 Summary:'));
      console.log(`  Total Checks: ${report.summary.totalChecks}`);
      console.log(chalk.green(`  Passed: ${report.summary.passed}`));
      console.log(chalk.red(`  Failed: ${report.summary.failed}`));
      console.log(chalk.yellow(`  Missing: ${report.summary.missing}`));

      if (options.output) {
        console.log(chalk.blue(`\n📄 Report saved to: ${options.output}`));
      }

      if (report.summary.failed > 0 || report.summary.missing > 0) {
        console.log(chalk.red('\n⚠️  Issues found! Check the detailed report for more information.'));
        process.exit(1);
      }

    } catch (error) {
      console.error(chalk.red(`❌ Error: ${error instanceof Error ? error.message : String(error)}`));
      process.exit(1);
    }
  });

program
  .command('validate-settings')
  .description('Validate a settings document structure')
  .requiredOption('-f, --file <file>', 'Settings document to validate')
  .action(async (options) => {
    try {
      validateFiles([options.file]);
      
      const { SettingsParser } = await import('./parsers/settings-parser');
      const parser = new SettingsParser();
      
      console.log(chalk.blue('🔍 Validating settings document...'));
      const settings = parser.parseSettingsDocument(options.file);
      
      console.log(chalk.green('✅ Settings document is valid!'));
      console.log(chalk.blue('\n📋 Document Info:'));
      console.log(`  Entity Type: ${settings.entityType}`);
      console.log(`  Settings Count: ${settings.settings.length}`);
      if (settings.metadata?.description) {
        console.log(`  Description: ${settings.metadata.description}`);
      }
      
    } catch (error) {
      console.error(chalk.red(`❌ Error: ${error instanceof Error ? error.message : String(error)}`));
      process.exit(1);
    }
  });

function validateFiles(files: string[]): void {
  for (const file of files) {
    if (!fs.existsSync(file)) {
      throw new Error(`File not found: ${file}`);
    }
    
    const stat = fs.statSync(file);
    if (!stat.isFile()) {
      throw new Error(`Path is not a file: ${file}`);
    }
  }
}

program.parse();