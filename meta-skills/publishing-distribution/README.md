# publishing-distribution

Schedule or publish finished content via Metricool or Zernio.

## Setup

```bash
cp .env.example .env
# configure at least one backend
../../setup-env.sh .env METRICOOL_TOKEN
```

## Usage

```
/publishing-distribution
```

**Note:** this skill always asks for explicit confirmation before
publishing or scheduling anything, even if you already approved the
content itself — see `SKILL.md`'s confirmation gate.
