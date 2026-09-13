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
  | "reviewing"
  | "settled"
  | "locked";

export type ContinuitySeverity = "pass" | "warn" | "fail";
export type ProseSource = "human" | "ai" | "ai_editor";
export type PromptEditProvider = "fake" | "litellm";
export type PromptEditSessionStatus = "active" | "applied" | "discarded";
export type GenreStrictness = "relaxed" | "standard" | "strict";

export interface ChapterUpdateRequest {
  title?: string;
  status?: ChapterStatus;
}

export type SceneType = "scene" | "sequel" | "transition" | "exposition";

export interface PressureTag {
  tag: string;
  source?: string;
  weight?: number;
}

export interface SceneBeat {
  id: string;
  project_id?: string;
  chapter_id: string;
  beat_key: string;
  summary: string;
  sort_order: number;
  completed: boolean;
  goal?: string;
  conflict?: string;
  outcome?: string;
  stakes_level?: number | null;
  pressure_tags?: PressureTag[];
  pov_character_id?: string | null;
  scene_type?: SceneType;
  created_at: string;
  updated_at: string;
}

export interface SceneBeatCreateRequest {
  beat_key: string;
  summary: string;
  sort_order: number;
  completed?: boolean;
  goal?: string;
  conflict?: string;
  outcome?: string;
  stakes_level?: number | null;
  pressure_tags?: PressureTag[];
  pov_character_id?: string | null;
  scene_type?: SceneType;
}

export interface SceneBeatUpdateRequest {
  beat_key?: string;
  summary?: string;
  sort_order?: number;
  completed?: boolean;
  goal?: string;
  conflict?: string;
  outcome?: string;
  stakes_level?: number | null;
  pressure_tags?: PressureTag[];
  pov_character_id?: string | null;
  scene_type?: SceneType;
}

export interface SceneBeatListResponse {
  items: SceneBeat[];
  pagination: PaginationMeta;
}

export interface ProseVersionSummary {
  version: number;
  word_count: number;
  source: ProseSource;
  created_by: string;
  created_at: string;
}

export interface ProseVersionDetail extends ProseVersionSummary {
  content: string;
}

export interface ProseVersionListResponse {
  items: ProseVersionSummary[];
  pagination: PaginationMeta;
}

export interface ProseVersionCreateRequest {
  content: string;
}

export interface ProseVersionCompareResponse {
  from_version: number;
  to_version: number;
  word_count_delta: number;
  created_at_from: string;
  created_at_to: string;
}

export type ContinuityCategory =
  | "character"
  | "timeline"
  | "world"
  | "foreshadow"
  | "psychology"
  | string;

export interface ContinuityIssue {
  fingerprint: string;
  severity: ContinuitySeverity;
  category: ContinuityCategory;
  code: string;
  message: string;
  chapter_refs: number[];
  entity_ids?: string[];
  evidence?: Record<string, unknown>;
}

export interface PsycheCardPatchProposal {
  character_id: string;
  patch: PsycheCard;
  confidence?: "extract_stub" | "author";
}

export interface PsychStateProposal {
  character_id: string;
  chapter_id: string;
  stress_level: number;
  dominant_emotion: string;
  active_goal: string;
  belief_updates?: BeliefUpdate[];
  relationship_stance?: RelationshipStance[];
  value_pressure?: string | null;
  arc_beat?: string | null;
  trigger_event_refs?: string[];
  confidence?: "extract_stub" | "author";
}

export interface StateDiff {
  ledger_proposals: Record<string, unknown>[];
  bible_patch_candidates: Record<string, unknown>[];
  psyche_card_patches?: PsycheCardPatchProposal[];
  psych_state_proposals?: PsychStateProposal[];
}

export interface ContinuityStats {
  passed: number;
  warnings: number;
  errors: number;
}

export interface ContinuityReport {
  report_id: string;
  chapter_id: string;
  prose_version: number;
  result: ContinuitySeverity;
  stats: ContinuityStats;
  issues: ContinuityIssue[];
  state_diff: StateDiff;
}

export interface ContinuityCheckRequest {
  prose_version?: number;
}

export interface ContinuityOverride {
  id: string;
  issue_fingerprint: string;
  severity_at_override: ContinuitySeverity;
  reason: string;
  created_at: string;
}

export interface ContinuityOverrideCreateRequest {
  issue_fingerprint: string;
  reason: string;
}

export interface SettleRequest {
  report_id?: string;
  approve_state_diff?: boolean;
}

export interface SettleResponse {
  chapter_id: string;
  status: ChapterStatus;
  bible_version_before: number;
  bible_version_after: number;
  ledger_events_appended: number;
  settled_at: string;
}

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

export interface ProjectUpdateRequest {
  title?: string;
  description?: string;
  genre_profile?: GenreProfile;
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
  current_prose_version?: number | null;
  settled_at?: string | null;
  locked_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChapterListResponse {
  items: Chapter[];
  pagination: PaginationMeta;
}

export type CharacterStatus = "established" | "provisional" | "archived";
export type ProvisionalStatus = "pending" | "merged" | "rejected";
export type ExtractorSource = "heuristic" | "manual" | "llm";
export type CharacterTier = 0 | 1 | 2 | 3;

export interface Character {
  id: string;
  project_id: string;
  display_name: string;
  role_one_liner?: string | null;
  tier: CharacterTier;
  status: CharacterStatus;
  aliases: string[];
  psyche_card?: Record<string, unknown> | null;
  first_seen_chapter_id?: string | null;
  last_seen_chapter_id?: string | null;
  appearance_count: number;
  merged_from_provisional_id?: string | null;
  metadata?: Record<string, unknown>;
  tier_suggest?: boolean;
  created_at: string;
  updated_at: string;
}

export interface CharacterCreateRequest {
  display_name: string;
  role_one_liner?: string;
  tier?: 0 | 1 | 2;
  aliases?: string[];
  status?: CharacterStatus;
}

export interface CharacterUpdateRequest {
  display_name?: string;
  role_one_liner?: string | null;
  aliases?: string[];
  psyche_card?: Record<string, unknown> | null;
  status?: CharacterStatus;
  metadata?: Record<string, unknown>;
}

export interface CharacterPromoteTierRequest {
  confirm_t3?: boolean;
}

export interface CharacterListResponse {
  items: Character[];
  pagination: PaginationMeta;
}

export interface CharacterSearchResult {
  character: Character;
  match_type: "display_name" | "alias" | "vector";
  matched_alias?: string | null;
  score: number;
}

export interface CharacterSearchResponse {
  items: CharacterSearchResult[];
  search_mode: "keyword" | "vector";
}

export interface CharacterProvisional {
  id: string;
  project_id: string;
  mention_text: string;
  mention_fingerprint?: string;
  chapter_id: string;
  chapter_number: number;
  prose_version: number;
  snippet: string;
  proposed_fields?: Record<string, unknown>;
  status: ProvisionalStatus;
  extractor_source: ExtractorSource;
  matched_character_id?: string | null;
  merged_character_id?: string | null;
  resolved_at?: string | null;
  created_at: string;
}

export interface CharacterProvisionalListResponse {
  items: CharacterProvisional[];
  pagination: PaginationMeta;
  pending_count: number;
}

export interface CharacterProvisionalMergeRequest {
  target_character_id?: string;
  create_new?: boolean;
  display_name?: string;
  initial_tier?: 0 | 1 | 2;
  mark_established?: boolean;
}

export interface CharacterProvisionalMergeResponse {
  provisional: CharacterProvisional;
  character: Character;
  idempotent: boolean;
}

export interface CharacterProvisionalRejectRequest {
  reason?: string;
}

export interface ExtractCharactersRequest {
  prose_version?: number;
  extractor_mode?: "heuristic" | "llm";
  include_beats?: boolean;
}

export interface ExtractCharactersResponse {
  created_count: number;
  skipped_count: number;
  skipped_reasons?: Record<string, number>;
  provisionals: CharacterProvisional[];
}

export interface PsycheArcFlags {
  allow_moral_break?: boolean;
  expected_arc_beats?: string[];
  current_arc_beat?: string | null;
}

export interface RelationshipLensEntry {
  target_character_id: string;
  role_label?: string;
  trust_level?: number;
  notes?: string;
}

export interface PsycheCard {
  drive?: string;
  need?: string;
  wound?: string;
  fear?: string;
  value_hierarchy?: string[];
  defense?: string;
  voice_taboo?: string[];
  stress_behavior?: string;
  moral_boundaries?: string[];
  relationship_lens?: RelationshipLensEntry[];
  arc_flags?: PsycheArcFlags;
  [key: string]: unknown;
}

export interface PsycheCardResponse {
  character_id: string;
  project_id: string;
  tier: CharacterTier;
  psyche_card: PsycheCard;
  updated_at: string;
}

export interface PsycheCardUpdateRequest {
  psyche_card: PsycheCard;
}

export interface BeliefUpdate {
  from_belief?: string;
  to_belief?: string;
  confidence?: "extract_stub" | "author" | "llm";
  trigger_ref?: string;
}

export interface RelationshipStance {
  target_character_id?: string;
  stance?: string;
  trust_delta?: number;
  notes?: string;
}

export interface PsychState {
  id: string;
  character_id: string;
  chapter_id: string;
  chapter_number?: number;
  stress_level: number;
  dominant_emotion: string;
  active_goal: string;
  belief_updates: BeliefUpdate[];
  relationship_stance: RelationshipStance[];
  value_pressure?: string | null;
  arc_beat?: string | null;
  trigger_event_refs: string[];
  settled_at: string;
}

export interface PsychStateListResponse {
  items: PsychState[];
  pagination: PaginationMeta;
}

export interface PsychContextPackRequest {
  chapter_id: string;
  beat_ids?: string[];
  character_ids?: string[];
  include_psyche_card?: boolean;
  psych_history_limit?: number;
}

export interface PsychContextPackEntry {
  character_id: string;
  display_name: string;
  tier: CharacterTier;
  psyche_summary?: PsycheCard;
  latest_psych_state?: Record<string, unknown>;
  included_reason: "scene_beat" | "pov" | "t3_principal" | "explicit";
}

export interface PsychContextPackResponse {
  entries: PsychContextPackEntry[];
  truncated: boolean;
}

export type TwistPlanStatus = "seeded" | "planted" | "armed" | "paid_off" | "abandoned";
export type TwistPlanKind = "twist" | "promise";
export type PlantSalience = "soft" | "hard";
export type TwistFairnessSeverity = "ok" | "warn" | "fail";

export interface TwistFairnessState {
  state: TwistFairnessSeverity;
  issue_codes: string[];
}

export interface TwistPayoffSummary {
  id: string;
  target_chapter_id: string;
  target_chapter_number: number;
  min_plants: number;
  required_plant_ids: string[];
}

export interface TwistPlan {
  id: string;
  project_id: string;
  title: string;
  secret_truth?: string;
  status: TwistPlanStatus;
  kind: TwistPlanKind;
  misdirection?: string | null;
  constraints_json: Record<string, unknown>;
  genre_strictness?: "strict" | "relaxed" | null;
  plant_count: number;
  payoff?: TwistPayoffSummary | null;
  created_at: string;
  updated_at: string;
}

export interface TwistPlanCreateRequest {
  title: string;
  secret_truth: string;
  kind?: TwistPlanKind;
  misdirection?: string | null;
  constraints_json?: Record<string, unknown>;
  genre_strictness?: "strict" | "relaxed" | null;
}

export interface TwistPlanUpdateRequest {
  title?: string;
  secret_truth?: string;
  misdirection?: string | null;
  constraints_json?: Record<string, unknown>;
  genre_strictness?: "strict" | "relaxed" | null;
  status?: TwistPlanStatus;
}

export interface TwistPlanListResponse {
  items: TwistPlan[];
  pagination: PaginationMeta;
}

export interface TwistTransitionRequest {
  status: TwistPlanStatus;
}

export interface TwistPlant {
  id: string;
  project_id: string;
  twist_id: string;
  chapter_id: string;
  chapter_number?: number;
  beat_id?: string | null;
  salience: PlantSalience;
  snippet: string;
  prose_span_start?: number | null;
  prose_span_end?: number | null;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface TwistPlantCreateRequest {
  chapter_id: string;
  beat_id?: string | null;
  salience?: PlantSalience;
  snippet: string;
  prose_span_start?: number | null;
  prose_span_end?: number | null;
  sort_order?: number;
}

export interface TwistPlantUpdateRequest {
  chapter_id?: string;
  beat_id?: string | null;
  salience?: PlantSalience;
  snippet?: string;
  prose_span_start?: number | null;
  prose_span_end?: number | null;
  sort_order?: number;
  twist_id?: string;
}

export interface TwistPlantListResponse {
  items: TwistPlant[];
}

export interface TwistPayoff {
  id: string;
  project_id: string;
  twist_id: string;
  target_chapter_id: string;
  target_chapter_number: number;
  required_plant_ids: string[];
  min_plants: number;
  revealed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface TwistPayoffCreateRequest {
  target_chapter_id: string;
  required_plant_ids?: string[];
  min_plants?: number;
}

export interface TwistPayoffUpdateRequest {
  target_chapter_id?: string;
  required_plant_ids?: string[];
  min_plants?: number;
}

export type TwistBoardColumnId = "secrets" | "plants" | "payoffs" | "revealed";
export type TwistBoardCardType = "twist" | "plant" | "payoff";

export interface TwistBoardCard {
  card_type: TwistBoardCardType;
  twist_id?: string;
  plant_id?: string;
  payoff_id?: string;
  title?: string;
  twist_title?: string;
  status?: TwistPlanStatus;
  kind?: TwistPlanKind;
  secret_truth_preview?: string;
  chapter_number?: number;
  target_chapter_number?: number;
  salience?: PlantSalience;
  snippet?: string;
  min_plants?: number;
  plant_count?: number;
  required_plant_ids?: string[];
  fairness?: TwistFairnessState;
}

export interface TwistBoardColumn {
  id: TwistBoardColumnId;
  label: string;
  cards: TwistBoardCard[];
}

export interface TwistBoardResponse {
  columns: TwistBoardColumn[];
}

export interface PowerSystemSettings {
  project_id: string;
  enabled: boolean;
  priority_gap: number;
  max_rank_jump_per_chapter: number;
  require_breakthrough_event: boolean;
  updated_at: string;
}

export interface PowerSystemSettingsUpdate {
  enabled?: boolean;
  priority_gap?: number;
  max_rank_jump_per_chapter?: number;
  require_breakthrough_event?: boolean;
}

export interface PowerRankSubStage {
  key: string;
  display_name: string;
  sort_order: number;
}

export interface PowerRank {
  id: string;
  rank_key: string;
  display_name: string;
  sort_order: number;
  sub_stages: PowerRankSubStage[];
  constraints_md?: string;
}

export interface PowerRankListResponse {
  items: PowerRank[];
}

export interface PowerRankCreateRequest {
  rank_key: string;
  display_name: string;
  sort_order?: number;
  sub_stages?: PowerRankSubStage[];
  constraints_md?: string;
}

export interface PowerRankUpdateRequest {
  rank_key?: string;
  display_name?: string;
  sort_order?: number;
  sub_stages?: PowerRankSubStage[];
  constraints_md?: string;
}

export interface PowerRankReorderRequest {
  rank_ids: string[];
}

export interface PowerTechnique {
  id: string;
  technique_key: string;
  display_name: string;
  min_rank_id: string;
  min_rank_display_name?: string;
  sect_requirement?: string | null;
  lineage_requirement?: string | null;
  resource_cost: Record<string, unknown>;
  notes_md?: string;
}

export interface PowerTechniqueListResponse {
  items: PowerTechnique[];
}

export interface PowerTechniqueCreateRequest {
  technique_key: string;
  display_name: string;
  min_rank_id: string;
  sect_requirement?: string;
  lineage_requirement?: string;
  resource_cost?: Record<string, unknown>;
  notes_md?: string;
}

export interface PowerTechniqueUpdateRequest {
  technique_key?: string;
  display_name?: string;
  min_rank_id?: string;
  sect_requirement?: string | null;
  lineage_requirement?: string | null;
  resource_cost?: Record<string, unknown>;
  notes_md?: string;
}

export interface GenreModuleConfig {
  enabled: boolean;
}

export interface GenreRulePack {
  schema_version?: number;
  base_profile?: GenreProfile;
  display_name?: string;
  modules?: {
    power_system?: GenreModuleConfig;
    foreshadow?: GenreModuleConfig;
    psychology?: GenreModuleConfig;
    timeline?: GenreModuleConfig;
  };
  strictness?: {
    foreshadow?: GenreStrictness;
    power?: GenreStrictness;
    psychology?: GenreStrictness;
  };
  promises?: string[];
  forbidden?: string[];
  expected_payoffs?: Record<string, unknown>[];
  thresholds?: Record<string, unknown>;
  tone?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface GenreRulePackResponse {
  project_id: string;
  genre_profile: GenreProfile;
  pack: GenreRulePack;
  updated_at: string;
}

export interface GenreRulePackPatch {
  pack?: GenreRulePack;
}

export interface PromptEditTurn {
  id: string;
  turn_index: number;
  instruction: string;
  proposed_content?: string | null;
  model: string;
  provider: PromptEditProvider;
  latency_ms?: number | null;
  token_usage?: Record<string, unknown>;
  error_code?: string | null;
  created_at: string;
}

export interface PromptEditInstructRequest {
  instruction: string;
  base_prose_version?: number;
  beat_key?: string;
}

export interface PromptEditInstructResponse {
  session_id: string;
  turn: PromptEditTurn;
  base_prose_version: number;
}

export interface PromptEditRegenerateRequest {
  session_id: string;
  turn_id: string;
}

export interface PromptEditApplyRequest {
  session_id: string;
  turn_id: string;
}

export interface PromptEditApplyResponse {
  prose_version: ProseVersionDetail;
  chapter: {
    current_prose_version?: number;
    word_count?: number;
  };
}

export interface PromptEditSessionSummary {
  id: string;
  status: PromptEditSessionStatus;
  base_prose_version: number;
  turns: PromptEditTurn[];
  created_at: string;
}

export interface PromptEditSessionListResponse {
  items: PromptEditSessionSummary[];
}

export interface SceneLintStats {
  fail: number;
  warn: number;
  pass: number;
}

export interface SceneLintResponse {
  chapter_id: string;
  result: ContinuitySeverity;
  issues: ContinuityIssue[];
  stats: SceneLintStats;
}

export interface SceneEngineSettings {
  project_id: string;
  enabled: boolean;
  require_conflict: boolean;
  require_outcome_on_complete: boolean;
  min_goal_length: number;
  llm_auditor_enabled: boolean;
  strictness: GenreStrictness;
  updated_at: string;
}

export type RelationType =
  | "ally"
  | "rival"
  | "mentor"
  | "family"
  | "romantic"
  | "enemy"
  | "custom";

export interface Relationship {
  id: string;
  project_id: string;
  character_a_id: string;
  character_b_id: string;
  character_a_name?: string;
  character_b_name?: string;
  relation_type: RelationType;
  custom_label?: string | null;
  baseline_intensity: number;
  current_intensity: number;
  notes_md?: string;
  event_count?: number;
  created_at: string;
  updated_at: string;
}

export interface RelationshipCreateRequest {
  character_a_id: string;
  character_b_id: string;
  relation_type: RelationType;
  custom_label?: string;
  baseline_intensity?: number;
  notes_md?: string;
}

export interface RelationshipUpdateRequest {
  relation_type?: RelationType;
  custom_label?: string | null;
  baseline_intensity?: number;
  notes_md?: string;
}

export interface RelationshipListResponse {
  items: Relationship[];
  pagination: PaginationMeta;
}

export interface RelationshipGraphNode {
  id: string;
  display_name: string;
  tier: number;
  degree: number;
}

export interface RelationshipGraphEdgeLastEvent {
  chapter_number: number;
  event_type: string;
  intensity_delta: number;
}

export interface RelationshipGraphEdge {
  id: string;
  source_id: string;
  target_id: string;
  relation_type: RelationType;
  intensity: number;
  last_event?: RelationshipGraphEdgeLastEvent;
  event_count: number;
}

export interface RelationshipGraphMeta {
  filtered_character_ids: string[];
  act_number: number | null;
  generated_at: string;
}

export interface RelationshipGraphResponse {
  nodes: RelationshipGraphNode[];
  edges: RelationshipGraphEdge[];
  meta: RelationshipGraphMeta;
}

export interface RelationshipEvent {
  id: string;
  relationship_id: string;
  event_type: string;
  intensity_delta: number;
  intensity_after: number;
  relation_type_after?: RelationType | null;
  chapter_number: number;
  settled_at?: string | null;
  payload?: Record<string, unknown>;
  created_at: string;
}

export interface RelationshipEventListResponse {
  items: RelationshipEvent[];
}

export type StakesEntryStatus = "planned" | "planted" | "resolved" | "abandoned";

export interface StakesLedgerEntry {
  id: string;
  project_id: string;
  act_number: number;
  checkpoint_key: string;
  title: string;
  description_md: string;
  target_level: number;
  status: StakesEntryStatus;
  plant_chapter_id?: string | null;
  resolve_chapter_id?: string | null;
  linked_twist_id?: string | null;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface StakesEntryCreateRequest {
  act_number: number;
  checkpoint_key: string;
  title: string;
  description_md?: string;
  target_level: number;
  sort_order?: number;
  linked_twist_id?: string;
}

export interface StakesEntryUpdateRequest {
  title?: string;
  description_md?: string;
  target_level?: number;
  status?: StakesEntryStatus;
  plant_chapter_id?: string | null;
  resolve_chapter_id?: string | null;
  linked_twist_id?: string | null;
  sort_order?: number;
}

export interface ActChapterBoundary {
  act_number: number;
  start_chapter: number;
  end_chapter: number;
  label?: string;
}

export interface ActStructureSettings {
  project_id: string;
  act_count: number;
  chapters_per_act: ActChapterBoundary[];
  enabled: boolean;
  flat_middle_window_chapters: number;
  updated_at: string;
}

export interface ActStructureSettingsUpdateRequest {
  act_count?: number;
  chapters_per_act?: ActChapterBoundary[];
  enabled?: boolean;
  flat_middle_window_chapters?: number;
}

export interface StakesActColumn {
  act_number: number;
  label?: string;
  start_chapter?: number;
  end_chapter?: number;
  entries: StakesLedgerEntry[];
}

export interface StakesBoardWarnings {
  flat_middle?: boolean;
  open_fail_count?: number;
}

export interface StakesBoardResponse {
  settings: {
    act_count: number;
    enabled: boolean;
  };
  acts: StakesActColumn[];
  warnings?: StakesBoardWarnings;
}
