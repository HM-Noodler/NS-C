// API Response Types for FastAPI Integration

export interface CollectionMetrics {
  successful_collections: number;
  successful_collections_amount: number;
  active_email_campaigns: number;
  active_email_campaigns_amount: number;
  email_escalation_queue: number;
  email_escalation_queue_amount: number;
  total_email_communications: number;
}

// Backend OpenAPI Schema Types
export interface ContactReadyClient {
  client_id: string;
  account_name: string;
  email_address?: string | null;
  invoice_aging_snapshots: AgingSnapshotSummary[];
  total_outstanding_across_invoices: string;
  dnc_status: boolean;
}

export interface AgingSnapshotSummary {
  invoice_number: string;
  invoice_date: string;
  snapshot_date: string;
  days_0_30: string;
  days_31_60: string;
  days_61_90: string;
  days_91_120: string;
  days_over_120: string;
}

export interface ImportResultSchema {
  success: boolean;
  total_rows: number;
  successful_rows: number;
  failed_rows: number;
  accounts_created?: number;
  contacts_created?: number;
  invoices_created?: number;
  invoices_updated?: number;  
  aging_snapshots_created?: number;
  contact_ready_clients: ContactReadyClient[];
  errors: ImportErrorSchema[];
  processing_time_seconds: number;
}

export interface ImportErrorSchema {
  row_number: number;
  field?: string | null;
  error_message: string;
  row_data?: any;
}

export interface EscalationResult {
  account: string;
  email_address: string;
  email_subject: string;
  email_body: string;
  escalation_degree: 1 | 2 | 3;
  template_used: string;
  invoice_count: number;
  total_outstanding: string;
  email_sent?: boolean;
  email_sent_at?: string | null;
  email_message_id?: string | null;
  email_send_error?: string | null;
  invoice_details?: InvoiceDetail[];
  aging_summary?: AgingSummary | null;
}

export interface InvoiceDetail {
  invoice_id: string;
  invoice_number: string;
  invoice_amount: string;
  total_outstanding: string;
  days_overdue: number;
  aging_bucket: string;
}

export interface AgingSummary {
  days_0_30: string;
  days_31_60: string;
  days_61_90: string;
  days_91_120: string;
  days_over_120: string;
  total: string;
}

export interface EscalationBatchResponse {
  success: boolean;
  processed_count: number;
  emails_generated: number;
  skipped_count: number;
  escalation_results: EscalationResult[];
  skipped_reasons: Record<string, number>;
  processing_time_seconds: number;
  errors?: string[];
  email_sending_summary?: EmailSendingSummary | null;
  email_sending_details?: EmailSendingDetail[];
}

export interface EscalationPreviewResponse {
  preview_results: EscalationResult[];
  summary: any;
  template_usage: Record<string, number>;
}

export interface EmailSendingSummary {
  total_attempts: number;
  successful_sends: number;  
  failed_sends: number;
  retry_attempts: number;
  send_duration_seconds: number;
}

export interface EmailSendingDetail {
  account_id: string;
  account_name: string;
  email_address: string;
  email_sent: boolean;
  email_sent_at?: string | null;
  email_message_id?: string | null;
  email_subject: string;
  email_send_error?: string | null;
  escalation_degree: 1 | 2 | 3;
  template_used: string;
  invoice_count: number;
  total_outstanding: string;
  oldest_invoice_days: number;
  invoices: InvoiceDetail[];
  aging_summary: AgingSummary;
}

export interface EscalationItem {
  id: string;
  company_name: string;
  amount: number;
  invoice_count: number;
  days_in_queue: number;
  last_contact: string;
  contact_email?: string;
  phone?: string;
  status: 'pending' | 'in_progress' | 'resolved';
}

export interface EmailActivity {
  id: string;
  company_name: string;
  amount: number;
  email_type: 'manual' | 'concierge';
  sent_date: string;
  status: 'sent' | 'opened' | 'responded' | 'bounced';
}

export interface ReceivablesData {
  paid_collections: number;
  paid_percentage: number;
  outstanding_receivables: number;
  outstanding_percentage: number;
  total_amount: number;
}

export interface ActivitySummary {
  concierge_emails: number;
  concierge_emails_percentage: number;
  total_activity: number;
  recent_emails: number;
}

export interface DashboardData {
  metrics: CollectionMetrics;
  escalation_queue: EscalationItem[];
  recent_activity: EmailActivity[];
  receivables: ReceivablesData;
  activity_summary: ActivitySummary;
}

// API Error Response
export interface APIError {
  detail: string;
  error_code?: string;
}

// API Response wrapper
export interface APIResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

// File Upload Types
export interface FileUploadResponse {
  filename: string;
  file_id: string;
  size: number;
  upload_date: string;
  processed: boolean;
}

// Navigation Types
export interface NavigationItem {
  name: string;
  href: string;
  icon: string;
  active: boolean;
}

// Email Workflow Types
export interface WorkflowStage {
  id: string;
  name: string;
  day: number;
  status: 'completed' | 'current' | 'pending';
  description: string;
  actions: string[];
}

export interface EmailCollectionWorkflow {
  clientName: string;
  totalAmount: number;
  invoiceCount: number;
  stages: WorkflowStage[];
  lastContact: string;
  totalEmails: number;
  currentStage: string;
}