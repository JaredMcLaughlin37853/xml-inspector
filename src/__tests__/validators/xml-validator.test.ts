import { XmlValidator } from '../../validators/xml-validator';
import { DOMParser } from 'xmldom';

describe('XmlValidator', () => {
  let validator: XmlValidator;
  let sampleXmlFile: any;

  beforeEach(() => {
    validator = new XmlValidator();
    
    const xmlContent = `<?xml version="1.0" encoding="UTF-8"?>
<device>
  <settings>
    <network>
      <ip>192.168.1.100</ip>
      <port>8080</port>
      <enabled>true</enabled>
    </network>
    <security>
      <timeout>30</timeout>
    </security>
  </settings>
</device>`;

    const parser = new DOMParser();
    sampleXmlFile = {
      path: '/test/sample.xml',
      content: parser.parseFromString(xmlContent, 'text/xml')
    };
  });

  describe('validateXmlFiles', () => {
    it('should validate settings with exact matches', () => {
      const settingsDocument = {
        entityType: 'device-config',
        settings: [
          {
            name: 'network-ip',
            xpath: '//network/ip/text()',
            expectedValue: '192.168.1.100',
            required: true,
            type: 'string' as const
          },
          {
            name: 'network-port',
            xpath: '//network/port/text()',
            expectedValue: 8080,
            required: true,
            type: 'number' as const
          }
        ]
      };

      const results = validator.validateXmlFiles([sampleXmlFile], settingsDocument);
      
      expect(results).toHaveLength(2);
      expect(results[0].status).toBe('pass');
      expect(results[0].settingName).toBe('network-ip');
      expect(results[0].actualValue).toBe('192.168.1.100');
      
      expect(results[1].status).toBe('pass');
      expect(results[1].settingName).toBe('network-port');
      expect(results[1].actualValue).toBe(8080);
    });

    it('should fail validation for mismatched values', () => {
      const settingsDocument = {
        entityType: 'device-config',
        settings: [
          {
            name: 'network-ip',
            xpath: '//network/ip/text()',
            expectedValue: '192.168.1.200',
            required: true,
            type: 'string' as const
          }
        ]
      };

      const results = validator.validateXmlFiles([sampleXmlFile], settingsDocument);
      
      expect(results).toHaveLength(1);
      expect(results[0].status).toBe('fail');
      expect(results[0].actualValue).toBe('192.168.1.100');
      expect(results[0].expectedValue).toBe('192.168.1.200');
      expect(results[0].message).toContain('Expected 192.168.1.200, got 192.168.1.100');
    });

    it('should handle missing settings', () => {
      const settingsDocument = {
        entityType: 'device-config',
        settings: [
          {
            name: 'missing-setting',
            xpath: '//nonexistent/text()',
            expectedValue: 'some-value',
            required: true,
            type: 'string' as const
          }
        ]
      };

      const results = validator.validateXmlFiles([sampleXmlFile], settingsDocument);
      
      expect(results).toHaveLength(1);
      expect(results[0].status).toBe('missing');
      expect(results[0].actualValue).toBeNull();
      expect(results[0].message).toContain('Setting not found at XPath');
    });

    it('should handle boolean type conversion', () => {
      const settingsDocument = {
        entityType: 'device-config',
        settings: [
          {
            name: 'network-enabled',
            xpath: '//network/enabled/text()',
            expectedValue: true,
            required: true,
            type: 'boolean' as const
          }
        ]
      };

      const results = validator.validateXmlFiles([sampleXmlFile], settingsDocument);
      
      expect(results).toHaveLength(1);
      expect(results[0].status).toBe('pass');
      expect(results[0].actualValue).toBe(true);
    });

    it('should handle number type conversion', () => {
      const settingsDocument = {
        entityType: 'device-config',
        settings: [
          {
            name: 'security-timeout',
            xpath: '//security/timeout/text()',
            expectedValue: 30,
            required: true,
            type: 'number' as const
          }
        ]
      };

      const results = validator.validateXmlFiles([sampleXmlFile], settingsDocument);
      
      expect(results).toHaveLength(1);
      expect(results[0].status).toBe('pass');
      expect(results[0].actualValue).toBe(30);
    });

    it('should pass validation when no expected value is provided', () => {
      const settingsDocument = {
        entityType: 'device-config',
        settings: [
          {
            name: 'network-ip',
            xpath: '//network/ip/text()',
            required: true,
            type: 'string' as const
          }
        ]
      };

      const results = validator.validateXmlFiles([sampleXmlFile], settingsDocument);
      
      expect(results).toHaveLength(1);
      expect(results[0].status).toBe('pass');
      expect(results[0].actualValue).toBe('192.168.1.100');
    });
  });
});