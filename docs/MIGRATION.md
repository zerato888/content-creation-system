# Migración desde la versión anterior

No hay actualización automática: se instala de nuevo, por proyecto (ver `README.md`). La versión
anterior queda guardada en el tag `legacy-v0`. Esta tabla dice dónde quedó cada ruta.

| antes | ahora |
|---|---|
| `meta-skills/research/` | `skills/web-research/`, `skills/deep-research/`, `skills/trend-research/` |
| `meta-skills/brand-strategy/` | `skills/brand-onboarding/`, `skills/hooks/`, `skills/idea/`, `skills/humanizer/` |
| `meta-skills/content-carousel/` | `skills/carousel-news/` + `engines/carousel/` + `presets/carousel/` |
| `meta-skills/content-video/` | `skills/captions/`, `skills/broll-plan/`, `skills/story-plan/`, `skills/reference-clone/` |
| `meta-skills/content-video/init-project.sh` | eliminado; el instalador arma el proyecto |
| `meta-skills/content-graphics/` | módulos (`catalog.json`, `tier: module`) |
| `meta-skills/image-generation/` | módulo |
| `meta-skills/voice-synthesis/` | módulo |
| `meta-skills/publishing-distribution/` | módulo |
| `meta-skills/analytics-insights/` | módulo |
| `meta-skills/agents-orchestration/` | `skills/kickoff-lite/` + `agents/` |
| `meta-skills/wiki-memory-system/` | `skills/wiki/` |
| `shared/wiki-engine/` | `skills/wiki/references/schema.md` |
| `shared/agents/<rol>.md` | `agents/<rol>.md` |
| `shared/agents/prompt-engineer.md` | eliminado |
| `shared/memory-system/` | eliminado |
| `shared/hooks/` | `hooks/` (opcionales, apagados por defecto) |
| `shared/utils/` | eliminado |
