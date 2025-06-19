import { SettingsParser } from '../../parsers/settings-parser';
import * as fs from 'fs';
import * as path from 'path';

describe('SettingsParser', () => {
  let parser: SettingsParser;

  beforeEach(() => {
    parser = new SettingsParser();
  });

  describe('parseSettingsDocument', () => {
    const testJsonPath = path.join(__dirname, 'test-data', 'settings.json');
    const testYamlPath = path.join(__dirname, 'test-data', 'settings.yaml');

    beforeAll(() => {
      const testDataDir = path.dirname(testJsonPath);
      if (!fs.existsSync(testDataDir)) {
        fs.mkdirSync(testDataDir, { recursive: true });
      }

      const settingsContent = {
        entityType: 'device-config',
        settings: [
          {
            name: 'network-ip',
            xpath: '//network/ip/text()',
            expectedValue: '192.168.1.100',
            description: 'Device IP address',
            type: 'string'
          },
          {
            name: 'network-port',
            xpath: '//network/port/text()',
            expectedValue: 8080,
            type: 'number'
          }
        ],
        metadata: {
          version: '1.0',
          description: 'Test settings'
        }
      };

      fs.writeFileSync(testJsonPath, JSON.stringify(settingsContent, null, 2));
      
      const yamlContent = `entityType: device-config
settings:
  - name: network-ip
    xpath: //network/ip/text()
    expectedValue: 192.168.1.100
    description: Device IP address
    type: string
  - name: network-port
    xpath: //network/port/text()
    expectedValue: 8080
    type: number
metadata:
  version: "1.0"
  description: Test settings`;
      
      fs.writeFileSync(testYamlPath, yamlContent);
    });

    afterAll(() => {
      [testJsonPath, testYamlPath].forEach(file => {
        if (fs.existsSync(file)) {
          fs.unlinkSync(file);
        }
      });
    });

    it('should parse JSON settings document', () => {
      const result = parser.parseSettingsDocument(testJsonPath);
      
      expect(result.entityType).toBe('device-config');
      expect(result.settings).toHaveLength(2);
      expect(result.settings[0].name).toBe('network-ip');
      expect(result.settings[0].xpath).toBe('//network/ip/text()');
      expect(result.settings[0].expectedValue).toBe('192.168.1.100');
    });

    it('should parse YAML settings document', () => {
      const result = parser.parseSettingsDocument(testYamlPath);
      
      expect(result.entityType).toBe('device-config');
      expect(result.settings).toHaveLength(2);
      expect(result.settings[1].name).toBe('network-port');
      expect(result.settings[1].expectedValue).toBe(8080);
    });

    it('should throw error for unsupported format', () => {
      const txtPath = path.join(__dirname, 'test-data', 'settings.txt');
      fs.writeFileSync(txtPath, 'invalid content');
      
      try {
        expect(() => {
          parser.parseSettingsDocument(txtPath);
        }).toThrow('Unsupported settings file format');
      } finally {
        fs.unlinkSync(txtPath);
      }
    });
  });

  describe('mergeSettingsDocuments', () => {
    it('should merge multiple settings documents', () => {
      const doc1 = {
        entityType: 'device-config',
        settings: [
          { name: 'setting1', xpath: '//test1', expectedValue: 'value1', required: true, type: 'string' as const }
        ]
      };

      const doc2 = {
        entityType: 'device-config',
        settings: [
          { name: 'setting2', xpath: '//test2', expectedValue: 'value2', required: true, type: 'string' as const }
        ]
      };

      const result = parser.mergeSettingsDocuments([doc1, doc2]);
      
      expect(result.entityType).toBe('device-config');
      expect(result.settings).toHaveLength(2);
      expect(result.settings.map(s => s.name)).toEqual(['setting1', 'setting2']);
    });

    it('should override duplicate settings', () => {
      const doc1 = {
        entityType: 'device-config',
        settings: [
          { name: 'setting1', xpath: '//test1', expectedValue: 'value1', required: true, type: 'string' as const }
        ]
      };

      const doc2 = {
        entityType: 'device-config',
        settings: [
          { name: 'setting1', xpath: '//test1', expectedValue: 'value2', required: true, type: 'string' as const }
        ]
      };

      const result = parser.mergeSettingsDocuments([doc1, doc2]);
      
      expect(result.settings).toHaveLength(1);
      expect(result.settings[0].expectedValue).toBe('value2');
    });

    it('should throw error for mismatched entity types', () => {
      const doc1 = {
        entityType: 'device-config',
        settings: []
      };

      const doc2 = {
        entityType: 'server-config',
        settings: []
      };

      expect(() => {
        parser.mergeSettingsDocuments([doc1, doc2]);
      }).toThrow('Entity type mismatch');
    });
  });
});