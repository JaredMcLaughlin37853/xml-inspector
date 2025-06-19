import * as fs from 'fs';
import * as path from 'path';
import { InspectionReport, ValidationResult } from '../types';

export class ReportGenerator {
  generateReport(
    results: ValidationResult[],
    xmlFiles: string[],
    settingsDocuments: string[],
    entityType: string
  ): InspectionReport {
    const summary = this.generateSummary(results);
    
    return {
      summary,
      results,
      metadata: {
        timestamp: new Date().toISOString(),
        entityType,
        xmlFiles,
        settingsDocuments
      }
    };
  }

  saveReportToFile(report: InspectionReport, outputPath: string, format: 'json' | 'html' = 'json'): void {
    const dir = path.dirname(outputPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    switch (format) {
      case 'json':
        this.saveJsonReport(report, outputPath);
        break;
      case 'html':
        this.saveHtmlReport(report, outputPath);
        break;
      default:
        throw new Error(`Unsupported report format: ${format}`);
    }
  }

  private generateSummary(results: ValidationResult[]) {
    const totalChecks = results.length;
    const passed = results.filter(r => r.status === 'pass').length;
    const failed = results.filter(r => r.status === 'fail').length;
    const missing = results.filter(r => r.status === 'missing').length;

    return {
      totalChecks,
      passed,
      failed,
      missing
    };
  }

  private saveJsonReport(report: InspectionReport, outputPath: string): void {
    const jsonContent = JSON.stringify(report, null, 2);
    fs.writeFileSync(outputPath, jsonContent, 'utf-8');
  }

  private saveHtmlReport(report: InspectionReport, outputPath: string): void {
    const htmlContent = this.generateHtmlContent(report);
    fs.writeFileSync(outputPath, htmlContent, 'utf-8');
  }

  private generateHtmlContent(report: InspectionReport): string {
    const { summary, results, metadata } = report;
    
    const passedResults = results.filter(r => r.status === 'pass');
    const failedResults = results.filter(r => r.status === 'fail');
    const missingResults = results.filter(r => r.status === 'missing');

    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XML Inspector Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }
        .summary { background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .summary-item { display: inline-block; margin-right: 20px; }
        .pass { color: #28a745; }
        .fail { color: #dc3545; }
        .missing { color: #ffc107; }
        .results-section { margin-bottom: 30px; }
        .result-item { border: 1px solid #ddd; padding: 10px; margin: 5px 0; border-radius: 3px; }
        .result-pass { border-left: 4px solid #28a745; }
        .result-fail { border-left: 4px solid #dc3545; }
        .result-missing { border-left: 4px solid #ffc107; }
        .metadata { font-size: 0.9em; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>XML Inspector Report</h1>
        <div class="metadata">
            <p><strong>Entity Type:</strong> ${metadata.entityType}</p>
            <p><strong>Generated:</strong> ${new Date(metadata.timestamp).toLocaleString()}</p>
            <p><strong>XML Files:</strong> ${metadata.xmlFiles.join(', ')}</p>
            <p><strong>Settings Documents:</strong> ${metadata.settingsDocuments.join(', ')}</p>
        </div>
    </div>

    <div class="summary">
        <h2>Summary</h2>
        <div class="summary-item"><strong>Total Checks:</strong> ${summary.totalChecks}</div>
        <div class="summary-item pass"><strong>Passed:</strong> ${summary.passed}</div>
        <div class="summary-item fail"><strong>Failed:</strong> ${summary.failed}</div>
        <div class="summary-item missing"><strong>Missing:</strong> ${summary.missing}</div>
    </div>

    ${failedResults.length > 0 ? `
    <div class="results-section">
        <h2 class="fail">Failed Checks (${failedResults.length})</h2>
        ${failedResults.map(result => `
        <div class="result-item result-fail">
            <strong>${result.settingName}</strong> - ${result.filePath}<br>
            <strong>XPath:</strong> ${result.xpath}<br>
            <strong>Expected:</strong> ${result.expectedValue || 'N/A'}<br>
            <strong>Actual:</strong> ${result.actualValue || 'N/A'}<br>
            ${result.message ? `<strong>Message:</strong> ${result.message}` : ''}
        </div>
        `).join('')}
    </div>
    ` : ''}

    ${missingResults.length > 0 ? `
    <div class="results-section">
        <h2 class="missing">Missing Settings (${missingResults.length})</h2>
        ${missingResults.map(result => `
        <div class="result-item result-missing">
            <strong>${result.settingName}</strong> - ${result.filePath}<br>
            <strong>XPath:</strong> ${result.xpath}<br>
            ${result.message ? `<strong>Message:</strong> ${result.message}` : ''}
        </div>
        `).join('')}
    </div>
    ` : ''}

    ${passedResults.length > 0 ? `
    <div class="results-section">
        <h2 class="pass">Passed Checks (${passedResults.length})</h2>
        ${passedResults.map(result => `
        <div class="result-item result-pass">
            <strong>${result.settingName}</strong> - ${result.filePath}<br>
            <strong>XPath:</strong> ${result.xpath}<br>
            <strong>Value:</strong> ${result.actualValue || 'N/A'}
        </div>
        `).join('')}
    </div>
    ` : ''}

</body>
</html>`;
  }
}