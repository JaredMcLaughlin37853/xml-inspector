import { DOMParser } from 'xmldom';
import * as xpath from 'xpath';
import * as fs from 'fs';
import { XmlFile } from '../types';

export class XmlParser {
  private domParser: DOMParser;

  constructor() {
    this.domParser = new DOMParser();
  }

  parseXmlFile(filePath: string): XmlFile {
    try {
      const xmlContent = fs.readFileSync(filePath, 'utf-8');
      const document = this.domParser.parseFromString(xmlContent, 'text/xml');
      
      if (this.hasParseErrors(document)) {
        throw new Error(`Invalid XML in file: ${filePath}`);
      }

      return {
        path: filePath,
        content: document
      };
    } catch (error) {
      throw new Error(`Failed to parse XML file ${filePath}: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  parseXmlFiles(filePaths: string[]): XmlFile[] {
    return filePaths.map(filePath => this.parseXmlFile(filePath));
  }

  evaluateXPath(document: Document, xpathExpression: string): string | null {
    try {
      const result = xpath.select(xpathExpression, document);
      
      if (Array.isArray(result) && result.length > 0) {
        const node = result[0];
        if (typeof node === 'string') {
          return node;
        }
        if (node && typeof node === 'object' && 'nodeValue' in node) {
          return (node as any).nodeValue || (node as any).textContent || null;
        }
        if (node && typeof node === 'object' && 'textContent' in node) {
          return (node as any).textContent || null;
        }
      }
      
      return null;
    } catch (error) {
      throw new Error(`XPath evaluation failed for expression "${xpathExpression}": ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  private hasParseErrors(document: Document): boolean {
    const parseErrors = document.getElementsByTagName('parsererror');
    return parseErrors.length > 0;
  }
}