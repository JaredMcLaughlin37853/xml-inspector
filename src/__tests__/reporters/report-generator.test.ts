import { ReportGenerator } from '../../reporters/report-generator';
import { ValidationResult } from '../../types';
import * as fs from 'fs';
import * as path from 'path';

describe('ReportGenerator', () => {
  let generator: ReportGenerator;

  beforeEach(() => {
    generator = new ReportGenerator();
  });

  describe('generateReport', () => {
    it('should generate a complete report', () => {
      const results: ValidationResult[] = [
        {
          settingName: 'network-ip',
          xpath: '//network/ip/text()',
          expectedValue: '192.168.1.100',
          actualValue: '192.168.1.100',
          status: 'pass',
          filePath: '/test/sample.xml'
        },
        {
          settingName: 'network-port',
          xpath: '//network/port/text()',
          expectedValue: 8080,
          actualValue: 9090,
          status: 'fail',
          message: 'Expected 8080, got 9090',
          filePath: '/test/sample.xml'
        },
        {
          settingName: 'missing-setting',
          xpath: '//missing/text()',
          expectedValue: 'value',
          actualValue: null,
          status: 'missing',
          message: 'Setting not found',
          filePath: '/test/sample.xml'
        }
      ];

      const report = generator.generateReport(
        results,
        ['/test/sample.xml'],
        ['/test/settings.json'],
        'device-config'
      );

      expect(report.summary.totalChecks).toBe(3);
      expect(report.summary.passed).toBe(1);
      expect(report.summary.failed).toBe(1);
      expect(report.summary.missing).toBe(1);
      expect(report.results).toEqual(results);
      expect(report.metadata.entityType).toBe('device-config');
      expect(report.metadata.xmlFiles).toEqual(['/test/sample.xml']);
      expect(report.metadata.settingsDocuments).toEqual(['/test/settings.json']);
      expect(report.metadata.timestamp).toBeDefined();
    });
  });

  describe('saveReportToFile', () => {
    const testDir = path.join(__dirname, 'test-output');
    
    beforeAll(() => {
      if (!fs.existsSync(testDir)) {
        fs.mkdirSync(testDir, { recursive: true });
      }
    });

    afterAll(() => {
      if (fs.existsSync(testDir)) {
        fs.rmSync(testDir, { recursive: true });
      }
    });

    it('should save JSON report', () => {
      const results: ValidationResult[] = [
        {
          settingName: 'test-setting',
          xpath: '//test/text()',
          expectedValue: 'value',
          actualValue: 'value',
          status: 'pass',
          filePath: '/test/sample.xml'
        }
      ];

      const report = generator.generateReport(
        results,
        ['/test/sample.xml'],
        ['/test/settings.json'],
        'test-config'
      );

      const outputPath = path.join(testDir, 'report.json');
      generator.saveReportToFile(report, outputPath, 'json');

      expect(fs.existsSync(outputPath)).toBe(true);
      
      const savedContent = fs.readFileSync(outputPath, 'utf-8');
      const savedReport = JSON.parse(savedContent);
      
      expect(savedReport.summary.totalChecks).toBe(1);
      expect(savedReport.results).toHaveLength(1);
    });

    it('should save HTML report', () => {
      const results: ValidationResult[] = [
        {
          settingName: 'test-setting',
          xpath: '//test/text()',
          expectedValue: 'value',
          actualValue: 'different',
          status: 'fail',
          message: 'Values do not match',
          filePath: '/test/sample.xml'
        }
      ];

      const report = generator.generateReport(
        results,
        ['/test/sample.xml'],
        ['/test/settings.json'],
        'test-config'
      );

      const outputPath = path.join(testDir, 'report.html');
      generator.saveReportToFile(report, outputPath, 'html');

      expect(fs.existsSync(outputPath)).toBe(true);
      
      const savedContent = fs.readFileSync(outputPath, 'utf-8');
      expect(savedContent).toContain('<!DOCTYPE html>');
      expect(savedContent).toContain('XML Inspector Report');
      expect(savedContent).toContain('test-setting');
      expect(savedContent).toContain('Failed Checks');
    });

    it('should create directories if they do not exist', () => {
      const nestedDir = path.join(testDir, 'nested', 'path');
      const outputPath = path.join(nestedDir, 'report.json');
      
      const report = generator.generateReport([], [], [], 'test-config');
      generator.saveReportToFile(report, outputPath, 'json');

      expect(fs.existsSync(outputPath)).toBe(true);
    });
  });
});