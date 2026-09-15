export type ApplicationType = "METER_NOT_WORKING" | "MPI_REMOVAL" | "GAS_LEAK";
export type ApplicationStatus = "NEW" | "IN_PROGRESS" | "COMPLETED" | "REJECTED";
export type ApplicationPriority = "NORMAL" | "HIGH" | "CRITICAL";
export type FileType = "METER_PHOTO" | "GAS_LEAK_PHOTO" | "OTHER";
export type AdminRole = "SUPER_ADMIN" | "DISPATCHER" | "OPERATOR";

export const APPLICATION_TYPE_LABELS: Record<ApplicationType, string> = {
  METER_NOT_WORKING: "Счетчик жұмыс жасамайды",
  MPI_REMOVAL: "МПИ-ге шешу",
  GAS_LEAK: "Есептеу құралынан газ шығуы",
};

export const STATUS_LABELS: Record<ApplicationStatus, string> = {
  NEW: "Жаңа",
  IN_PROGRESS: "Өңделуде",
  COMPLETED: "Аяқталды",
  REJECTED: "Қабылданбады",
};

export const PRIORITY_LABELS: Record<ApplicationPriority, string> = {
  NORMAL: "Қалыпты",
  HIGH: "Жоғары",
  CRITICAL: "Авариялық",
};

export const ROLE_LABELS: Record<AdminRole, string> = {
  SUPER_ADMIN: "Супер әкімші",
  DISPATCHER: "Диспетчер",
  OPERATOR: "Оператор",
};

export interface AdminOut {
  id: number;
  name: string;
  email: string;
  role: AdminRole;
  active: boolean;
}

export interface UserOut {
  id: number;
  telegram_user_id: number;
  telegram_username: string | null;
  first_name: string | null;
  last_name: string | null;
  phone_number: string | null;
  created_at: string;
}

export interface FileOut {
  id: number;
  file_type: FileType;
  storage_url: string;
  created_at: string;
}

export interface HistoryOut {
  id: number;
  old_status: ApplicationStatus | null;
  new_status: ApplicationStatus;
  comment: string | null;
  admin: AdminOut | null;
  created_at: string;
}

export interface ApplicationListItem {
  id: number;
  application_number: string;
  personal_account: string;
  application_type: ApplicationType;
  status: ApplicationStatus;
  priority: ApplicationPriority;
  created_at: string;
  user: UserOut;
  assigned_admin: AdminOut | null;
}

export interface ApplicationListResponse {
  items: ApplicationListItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface ApplicationDetail {
  id: number;
  application_number: string;
  personal_account: string;
  application_type: ApplicationType;
  status: ApplicationStatus;
  priority: ApplicationPriority;
  requested_date: string | null;
  latitude: number | null;
  longitude: number | null;
  admin_comment: string | null;
  created_at: string;
  updated_at: string;
  user: UserOut;
  assigned_admin: AdminOut | null;
  files: FileOut[];
  history: HistoryOut[];
}

export interface DashboardStats {
  total: number;
  new: number;
  in_progress: number;
  completed: number;
  rejected: number;
  critical: number;
  by_type: Record<string, number>;
  by_day: { date: string; count: number }[];
}

export interface ReportStats {
  total: number;
  new: number;
  in_progress: number;
  completed: number;
  rejected: number;
  critical: number;
  avg_processing_hours: number | null;
}

export interface SystemSettingsOut {
  organization_name: string;
  contact_phone: string;
  emergency_phone: string;
  max_photo_size_mb: number;
  welcome_text: string;
  status_new_text: string;
  status_in_progress_text: string;
  status_completed_text: string;
  status_rejected_text: string;
}
