import * as fs from 'fs';
import * as yaml from 'js-yaml';
import { SettingsDocument, Setting } from '../types';

export class SettingsParser {
  parseSettingsDocument(filePath: string): SettingsDocument {
    try {
      const content = fs.readFileSync(filePath, 'utf-8');
      const extension = filePath.toLowerCase().split('.').pop();

      switch (extension) {
        case 'json':
          return this.parseJsonSettings(content);
        case 'yaml':
        case 'yml':
          return this.parseYamlSettings(content);
        default:
          throw new Error(`Unsupported settings file format: ${extension}`);
      }
    } catch (error) {
      throw new Error(`Failed to parse settings document ${filePath}: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  parseMultipleSettingsDocuments(filePaths: string[]): SettingsDocument[] {
    return filePaths.map(filePath => this.parseSettingsDocument(filePath));
  }

  mergeSettingsDocuments(documents: SettingsDocument[]): SettingsDocument {
    if (documents.length === 0) {
      throw new Error('No settings documents provided for merging');
    }

    const baseDocument = documents[0];
    const mergedSettings: Setting[] = [...baseDocument.settings];

    for (let i = 1; i < documents.length; i++) {
      const currentDoc = documents[i];
      
      if (currentDoc.entityType !== baseDocument.entityType) {
        throw new Error(`Entity type mismatch: ${baseDocument.entityType} vs ${currentDoc.entityType}`);
      }

      for (const setting of currentDoc.settings) {
        const existingIndex = mergedSettings.findIndex(s => s.name === setting.name);
        if (existingIndex >= 0) {
          mergedSettings[existingIndex] = { ...mergedSettings[existingIndex], ...setting };
        } else {
          mergedSettings.push(setting);
        }
      }
    }

    return {
      entityType: baseDocument.entityType,
      settings: mergedSettings,
      metadata: {
        ...baseDocument.metadata,
        description: 'Merged settings document'
      }
    };
  }

  private parseJsonSettings(content: string): SettingsDocument {
    const parsed = JSON.parse(content);
    return this.validateSettingsDocument(parsed);
  }

  private parseYamlSettings(content: string): SettingsDocument {
    const parsed = yaml.load(content) as any;
    return this.validateSettingsDocument(parsed);
  }

  private validateSettingsDocument(data: any): SettingsDocument {
    if (!data || typeof data !== 'object') {
      throw new Error('Settings document must be an object');
    }

    if (!data.entityType || typeof data.entityType !== 'string') {
      throw new Error('Settings document must have a valid entityType');
    }

    if (!Array.isArray(data.settings)) {
      throw new Error('Settings document must have a settings array');
    }

    const settings: Setting[] = data.settings.map((setting: any, index: number) => {
      if (!setting || typeof setting !== 'object') {
        throw new Error(`Setting at index ${index} must be an object`);
      }

      if (!setting.name || typeof setting.name !== 'string') {
        throw new Error(`Setting at index ${index} must have a valid name`);
      }

      if (!setting.xpath || typeof setting.xpath !== 'string') {
        throw new Error(`Setting at index ${index} must have a valid xpath`);
      }

      return {
        name: setting.name,
        xpath: setting.xpath,
        expectedValue: setting.expectedValue,
        description: setting.description,
        required: setting.required !== false,
        type: setting.type || 'string'
      };
    });

    return {
      entityType: data.entityType,
      settings,
      metadata: data.metadata || {}
    };
  }
}