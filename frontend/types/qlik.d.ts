/**
 * Type definitions for Qlik Sense Capability APIs
 * Ces types permettent d'utiliser l'API Qlik avec TypeScript
 */

export interface QlikConfig {
  host: string;
  port: number;
  prefix: string;
  isSecure: boolean;
  appName?: string;
}

export interface QlikApp {
  getList(type: string, callback: (reply: any) => void): void;
  visualization: {
    create(
      id: string,
      dimensions?: any[],
      measures?: any[],
      options?: QlikVisualizationOptions
    ): Promise<QlikVisualization>;
  };
  createList(listDef: any, callback?: (reply: any) => void): QlikGenericObject;
  getObject(id: string): Promise<QlikVisualization>;
  doReload(mode?: number, partial?: boolean): Promise<void>;
  forward(): void;
  back(): void;
  clearAll(): void;
  field(name: string): QlikField;
}

export interface QlikVisualization {
  show(element: string | HTMLElement): void;
  close(): void;
  resize(): void;
  exportData(options?: ExportDataOptions): Promise<string>;
  exportImg(options?: ExportImgOptions): Promise<string>;
  exportPdf(options?: ExportPdfOptions): Promise<void>;
}

export interface QlikVisualizationOptions {
  noInteraction?: boolean;
  noSelections?: boolean;
}

export interface QlikGenericObject {
  close(): void;
}

export interface QlikField {
  clear(): void;
  select(values: string | string[], toggle?: boolean): void;
  selectAll(): void;
  selectAlternative(): void;
  selectExcluded(): void;
  selectPossible(): void;
  toggleSelect(match: string, softlock?: boolean): void;
}

export interface ExportDataOptions {
  format?: 'CSV_C' | 'CSV_T' | 'OOXML';
  state?: 'A' | 'P';
  download?: boolean;
}

export interface ExportImgOptions {
  format?: 'jpg' | 'png';
  height?: number;
  width?: number;
}

export interface ExportPdfOptions {
  documentSize?: {
    width?: number;
    height?: number;
  };
  orientation?: 'portrait' | 'landscape';
  aspectRatio?: number;
}

export interface QlikGlobal {
  openApp(appId: string, config?: QlikConfig): QlikApp;
  setOnError(callback: (error: any) => void): void;
  callRepository(path: string, method?: string, body?: string): Promise<any>;
  getGlobal(config?: QlikConfig): QlikApp;
  resize(): void;
}

export interface RequireConfig {
  baseUrl?: string;
  webIntegrationId?: string;
  config?: {
    [key: string]: any;
  };
}

declare global {
  interface Window {
    require: {
      (modules: string[], callback: (qlik: QlikGlobal) => void): void;
      config(config: RequireConfig): void;
    };
  }
}

export {};
