export type ProjectStatus = "active" | "archived";
export type ProjectLanguage = "vi" | "en" | "mixed";
export type GenreProfile = "xianxia" | "mystery" | "literary" | "romance" | "custom";
export type ProjectTemplate = "blank" | "xianxia_starter" | "mystery_starter";
export type BibleSection =
  | "world_rules"
  | "locations"
  | "factions"
  | "glossary"
  | "timeline"
  | "characters"
  | "objects";
export type ChapterStatus =
  | "planned"
  | "drafting"
  | "continuity_pending"
  | "settled"
  | "locked";

export interface PaginationMeta {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>[];
  };
}

export interface ProjectSummary {
  id: string;
  slug: string;
  title: string;
  description?: string | null;
  language?: ProjectLanguage;
  genre_profile: GenreProfile;
  template?: ProjectTemplate;
  status: ProjectStatus;
  bible_version_current: number;
  progress_percent?: number;
  updated_at: string;
}

export interface ProjectDetail extends ProjectSummary {
  created_by: string;
  created_at: string;
  settings?: Record<string, unknown>;
  chapter_count: number;
  bible_entry_count: number;
}

export interface ProjectCreateRequest {
  title: string;
  description?: string;
  language: ProjectLanguage;
  genre_profile: GenreProfile;
  template: ProjectTemplate;
  slug?: string;
}

export interface ProjectListResponse {
  items: ProjectSummary[];
  pagination: PaginationMeta;
}

export interface BibleEntry {
  id: string;
  project_id: string;
  entry_key: string;
  section: BibleSection;
  title: string;
  content_md: string;
  metadata: Record<string, unknown>;
  base_bible_version: number;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface BibleEntryCreateRequest {
  entry_key: string;
  section: BibleSection;
  title: string;
  content_md?: string;
  metadata?: Record<string, unknown>;
}

export interface BibleEntryUpdateRequest {
  title?: string;
  content_md?: string;
  metadata?: Record<string, unknown>;
  section?: BibleSection;
}

export interface BibleEntryListResponse {
  items: BibleEntry[];
  pagination: PaginationMeta;
}

export interface BibleVersionSummary {
  version: number;
  settled_from_chapter_id?: string | null;
  created_at: string;
  entry_count?: number;
}

export interface BibleVersionDetail extends BibleVersionSummary {
  project_id: string;
  snapshot_json: Record<string, unknown>;
}

export interface BibleVersionListResponse {
  items: BibleVersionSummary[];
  pagination: PaginationMeta;
}

export interface Chapter {
  id: string;
  project_id: string;
  number: number;
  title: string;
  status: ChapterStatus;
  word_count: number;
  bible_version_at_draft?: number | null;
  created_at: string;
  updated_at: string;
}

export interface ChapterListResponse {
  items: Chapter[];
  pagination: PaginationMeta;
}

export interface Character {
  id: string;
  project_id: string;
  display_name: string;
  role_one_liner?: string | null;
  tier: 0;
  psyche_card?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface CharacterListResponse {
  items: Character[];
  pagination: PaginationMeta;
}
