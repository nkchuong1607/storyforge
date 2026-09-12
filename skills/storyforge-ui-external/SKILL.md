---
name: storyforge-ui-external
description: Before StoryForge UI work, ensure taste-skill and ui-ux-pro-max are installed; then follow their guidance for anti-slop design.
---

# StoryForge External UI Skills Wrapper

Use before implementing author-facing UI in `apps/web/`.

## Install (developer machine)

```bash
# Anti-slop frontend / design taste
npx skills add https://github.com/Leonxlnx/taste-skill

# UI/UX patterns for Cursor
npx ui-ux-pro-max-cli init --ai cursor
```

Claude Code: see [ui-ux-pro-max-skill README](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) for alternate init.

## Workflow

1. Confirm external skills installed (or install now)
2. Read the brief / wireframe (`docs/architecture.md` for product context)
3. Apply taste-skill for visual direction — avoid templated "AI slop" layouts
4. Apply ui-ux-pro-max for component patterns and accessibility
5. Implement using `storyforge-web-next` conventions (App Router, API client)

## Scope Note

StoryForge bootstrap does **not** include full Chapter Editor or Continuity Gate UI. When building those screens, combine this skill with domain skills (`storyforge-continuity`, etc.).

## References

- [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)
- [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
- `docs/agent-setup.md`
