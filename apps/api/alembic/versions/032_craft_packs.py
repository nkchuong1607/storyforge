"""Craft packs catalog, project bindings, craft continuity category."""

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "032_craft_packs"
down_revision: Union[str, None] = "031_fact_citations"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

MYSTERY_PACK = {
    "schema_version": 1,
    "id": "mystery.fair_play.v1",
    "display_name": "Mystery — Fair Play",
    "genre_tags": ["mystery"],
    "compat": {
        "requires_genre_profiles": ["mystery", "custom"],
        "min_app_phase": 10,
    },
    "structure": {
        "template_id": "mystery_three_act_fair_play",
        "beats": [
            {"key": "hook", "act": 1, "required": True},
            {"key": "crime_or_puzzle", "act": 1, "required": True},
            {"key": "investigation_loop", "act": 2, "required": True},
            {"key": "midpoint_reversal", "act": 2, "required": True},
            {"key": "fair_clue_cluster", "act": 2, "required": True},
            {"key": "false_solution", "act": 2, "required": False},
            {"key": "reveal", "act": 3, "required": True},
            {"key": "payoff_wrap", "act": 3, "required": True},
        ],
    },
    "checklist": [
        {
            "id": "clue_before_reveal",
            "severity_default": "fail",
            "continuity_category": "foreshadow",
            "code": "craft_mystery_clue_after_reveal",
            "description": (
                "Every reveal claim must map to ≥1 planted clue with earlier chapter_ref"
            ),
        },
        {
            "id": "red_herring_labeled",
            "severity_default": "warn",
            "continuity_category": "craft",
            "code": "craft_mystery_unlabeled_misdirection",
            "description": "Misdirection without TwistPlan misdirection entry",
        },
        {
            "id": "detective_knowledge_ledger",
            "severity_default": "warn",
            "continuity_category": "craft",
            "code": "craft_mystery_reader_spoiler",
            "description": (
                "Reader-known secret appears in detective POV without knowledge ledger event"
            ),
        },
        {
            "id": "fair_play_min_clues",
            "severity_default": "fail",
            "continuity_category": "foreshadow",
            "code": "craft_mystery_insufficient_plants",
            "description": "Payoff requires ≥2 plants (align with mystery rule-pack threshold)",
        },
    ],
    "prompt_hooks": {
        "context_pack_extra_keys": [
            "craft_checklist_open",
            "active_clues",
            "active_misdirections",
        ],
        "prompt_edit_skills": [
            "mystery_clue_plant",
            "mystery_reveal_align",
            "mystery_red_herring",
        ],
    },
    "golden": {
        "fixture_project_slug": "golden-mystery-fair-play",
        "min_seeded_flags": 3,
        "fakellm_coverage_target": 0.9,
    },
}


def upgrade() -> None:
    op.execute("ALTER TYPE continuity_category ADD VALUE IF NOT EXISTS 'craft'")

    op.create_table(
        "craft_packs",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False),
        sa.Column("pack_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "installed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "project_craft_packs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("craft_pack_id", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), server_default="false", nullable=False),
        sa.Column(
            "bound_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["craft_pack_id"], ["craft_packs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "craft_pack_id", name="project_craft_packs_project_pack_uq"),
    )
    op.create_index(
        "project_craft_packs_project_active_idx",
        "project_craft_packs",
        ["project_id", "active"],
    )

    pack_json = json.dumps(MYSTERY_PACK)
    op.execute(
        sa.text(
            "INSERT INTO craft_packs (id, schema_version, pack_json) "
            "VALUES ('mystery.fair_play.v1', 1, CAST(:pack AS jsonb))"
        ).bindparams(pack=pack_json)
    )


def downgrade() -> None:
    op.drop_index("project_craft_packs_project_active_idx", table_name="project_craft_packs")
    op.drop_table("project_craft_packs")
    op.drop_table("craft_packs")
