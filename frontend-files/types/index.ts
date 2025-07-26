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