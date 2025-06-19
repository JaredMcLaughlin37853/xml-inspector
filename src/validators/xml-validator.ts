import { XmlParser } from '../core/xml-parser';
import { SettingsDocument, XmlFile, ValidationResult, Setting } from '../types';

export class XmlValidator {
  private xmlParser: XmlParser;

  constructor() {
    this.xmlParser = new XmlParser();
  }

  validateXmlFiles(xmlFiles: XmlFile[], settingsDocument: SettingsDocument): ValidationResult[] {
    const results: ValidationResult[] = [];

    for (const xmlFile of xmlFiles) {
      for (const setting of settingsDocument.settings) {
        const result = this.validateSetting(xmlFile, setting);
        results.push(result);
      }
    }

    return results;
  }

  private validateSetting(xmlFile: XmlFile, setting: Setting): ValidationResult {
    try {
      const actualValue = this.xmlParser.evaluateXPath(xmlFile.content, setting.xpath);
      
      if (actualValue === null || actualValue === undefined) {
        return {
          settingName: setting.name,
          xpath: setting.xpath,
          expectedValue: setting.expectedValue,
          actualValue: null,
          status: 'missing',
          message: `Setting not found at XPath: ${setting.xpath}`,
          filePath: xmlFile.path
        };
      }

      const convertedActualValue = this.convertValue(actualValue, setting.type || 'string');
      const isValid = this.compareValues(convertedActualValue, setting.expectedValue, setting.type);

      return {
        settingName: setting.name,
        xpath: setting.xpath,
        expectedValue: setting.expectedValue,
        actualValue: convertedActualValue,
        status: isValid ? 'pass' : 'fail',
        message: isValid 
          ? undefined 
          : `Expected ${setting.expectedValue}, got ${convertedActualValue}`,
        filePath: xmlFile.path
      };
    } catch (error) {
      return {
        settingName: setting.name,
        xpath: setting.xpath,
        expectedValue: setting.expectedValue,
        actualValue: null,
        status: 'fail',
        message: `Validation error: ${error instanceof Error ? error.message : String(error)}`,
        filePath: xmlFile.path
      };
    }
  }

  private convertValue(value: string, type: string): string | number | boolean {
    switch (type) {
      case 'number':
        const numValue = parseFloat(value);
        if (isNaN(numValue)) {
          throw new Error(`Cannot convert "${value}" to number`);
        }
        return numValue;
      case 'boolean':
        const lowerValue = value.toLowerCase().trim();
        if (lowerValue === 'true' || lowerValue === '1') return true;
        if (lowerValue === 'false' || lowerValue === '0') return false;
        throw new Error(`Cannot convert "${value}" to boolean`);
      case 'string':
      default:
        return value.trim();
    }
  }

  private compareValues(
    actualValue: string | number | boolean, 
    expectedValue: string | number | boolean | undefined,
    type?: string
  ): boolean {
    if (expectedValue === undefined) {
      return true;
    }

    if (type === 'number') {
      return Number(actualValue) === Number(expectedValue);
    }

    if (type === 'boolean') {
      return Boolean(actualValue) === Boolean(expectedValue);
    }

    return String(actualValue) === String(expectedValue);
  }
}