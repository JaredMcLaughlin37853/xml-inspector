import { XmlParser } from '../../core/xml-parser';
import * as fs from 'fs';
import * as path from 'path';

describe('XmlParser', () => {
  let parser: XmlParser;
  const testXmlPath = path.join(__dirname, 'test-data', 'sample.xml');
  const testXmlContent = `<?xml version="1.0" encoding="UTF-8"?>
<device>
  <settings>
    <network>
      <ip>192.168.1.100</ip>
      <port>8080</port>
      <enabled>true</enabled>
    </network>
    <security>
      <encryption>AES256</encryption>
      <timeout>30</timeout>
    </security>
  </settings>
</device>`;

  beforeAll(() => {
    const testDataDir = path.dirname(testXmlPath);
    if (!fs.existsSync(testDataDir)) {
      fs.mkdirSync(testDataDir, { recursive: true });
    }
    fs.writeFileSync(testXmlPath, testXmlContent);
  });

  afterAll(() => {
    if (fs.existsSync(testXmlPath)) {
      fs.unlinkSync(testXmlPath);
    }
  });

  beforeEach(() => {
    parser = new XmlParser();
  });

  describe('parseXmlFile', () => {
    it('should parse valid XML file successfully', () => {
      const result = parser.parseXmlFile(testXmlPath);
      
      expect(result.path).toBe(testXmlPath);
      expect(result.content).toBeDefined();
      expect(result.content.documentElement.tagName).toBe('device');
    });

    it('should throw error for non-existent file', () => {
      expect(() => {
        parser.parseXmlFile('/non/existent/file.xml');
      }).toThrow();
    });

    it('should throw error for invalid XML', () => {
      const invalidXmlPath = path.join(__dirname, 'test-data', 'invalid.xml');
      fs.writeFileSync(invalidXmlPath, '<invalid><xml></invalid>');
      
      try {
        expect(() => {
          parser.parseXmlFile(invalidXmlPath);
        }).toThrow();
      } finally {
        fs.unlinkSync(invalidXmlPath);
      }
    });
  });

  describe('parseXmlFiles', () => {
    it('should parse multiple XML files', () => {
      const results = parser.parseXmlFiles([testXmlPath]);
      
      expect(results).toHaveLength(1);
      expect(results[0].path).toBe(testXmlPath);
    });
  });

  describe('evaluateXPath', () => {
    let xmlFile: any;

    beforeEach(() => {
      xmlFile = parser.parseXmlFile(testXmlPath);
    });

    it('should extract string values correctly', () => {
      const ip = parser.evaluateXPath(xmlFile.content, '//network/ip/text()');
      expect(ip).toBe('192.168.1.100');
    });

    it('should extract numeric values correctly', () => {
      const port = parser.evaluateXPath(xmlFile.content, '//network/port/text()');
      expect(port).toBe('8080');
    });

    it('should extract boolean values correctly', () => {
      const enabled = parser.evaluateXPath(xmlFile.content, '//network/enabled/text()');
      expect(enabled).toBe('true');
    });

    it('should return null for non-existent xpath', () => {
      const result = parser.evaluateXPath(xmlFile.content, '//nonexistent/text()');
      expect(result).toBeNull();
    });

    it('should throw error for invalid xpath', () => {
      expect(() => {
        parser.evaluateXPath(xmlFile.content, '//invalid[xpath');
      }).toThrow();
    });
  });
});