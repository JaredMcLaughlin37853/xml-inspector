import { XmlParser } from './xml-parser';
import { SettingsParser } from '../parsers/settings-parser';
import { XmlValidator } from '../validators/xml-validator';
import { ReportGenerator } from '../reporters/report-generator';
import { InspectionReport, SettingsDocument } from '../types';

export interface InspectionOptions {
  xmlFiles: string[];
  standardSettingsFile: string;
  projectSettingsFile?: string;
  entityType: string;
  outputPath?: string;
  outputFormat?: 'json' | 'html';
}

export class XmlInspector {
  private xmlParser: XmlParser;
  private settingsParser: SettingsParser;
  private validator: XmlValidator;
  private reportGenerator: ReportGenerator;

  constructor() {
    this.xmlParser = new XmlParser();
    this.settingsParser = new SettingsParser();
    this.validator = new XmlValidator();
    this.reportGenerator = new ReportGenerator();
  }

  async inspect(options: InspectionOptions): Promise<InspectionReport> {
    try {
      const xmlFiles = this.xmlParser.parseXmlFiles(options.xmlFiles);
      
      const settingsDocuments: SettingsDocument[] = [];
      settingsDocuments.push(this.settingsParser.parseSettingsDocument(options.standardSettingsFile));
      
      if (options.projectSettingsFile) {
        settingsDocuments.push(this.settingsParser.parseSettingsDocument(options.projectSettingsFile));
      }

      const mergedSettings = settingsDocuments.length > 1 
        ? this.settingsParser.mergeSettingsDocuments(settingsDocuments)
        : settingsDocuments[0];

      if (mergedSettings.entityType !== options.entityType) {
        throw new Error(`Entity type mismatch: expected ${options.entityType}, got ${mergedSettings.entityType}`);
      }

      const validationResults = this.validator.validateXmlFiles(xmlFiles, mergedSettings);

      const report = this.reportGenerator.generateReport(
        validationResults,
        options.xmlFiles,
        [options.standardSettingsFile, ...(options.projectSettingsFile ? [options.projectSettingsFile] : [])],
        options.entityType
      );

      if (options.outputPath) {
        this.reportGenerator.saveReportToFile(report, options.outputPath, options.outputFormat);
      }

      return report;
    } catch (error) {
      throw new Error(`Inspection failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
}