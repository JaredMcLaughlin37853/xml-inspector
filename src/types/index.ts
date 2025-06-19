export interface Setting {
  name: string;
  xpath: string;
  expectedValue?: string | number | boolean;
  description?: string;
  required?: boolean;
  type?: 'string' | 'number' | 'boolean';
}

export interface SettingsDocument {
  entityType: string;
  settings: Setting[];
  metadata?: {
    version?: string;
    description?: string;
    author?: string;
  };
}

export interface ValidationResult {
  settingName: string;
  xpath: string;
  expectedValue?: string | number | boolean;
  actualValue?: string | number | boolean;
  status: 'pass' | 'fail' | 'missing';
  message?: string;
  filePath: string;
}

export interface InspectionReport {
  summary: {
    totalChecks: number;
    passed: number;
    failed: number;
    missing: number;
  };
  results: ValidationResult[];
  metadata: {
    timestamp: string;
    entityType: string;
    xmlFiles: string[];
    settingsDocuments: string[];
  };
}

export interface XmlFile {
  path: string;
  content: Document;
}