---
name: autarqui-dockerfiledoc
description: >
  Analyze and optimize Dockerfiles for image size, security, caching, and best practices.
  Use this skill whenever the user shares a Dockerfile, asks to review or improve a
  Dockerfile, mentions Docker image size or build time issues, wants a security audit of
  a container, or says anything like "can you fix my Dockerfile", "is this Dockerfile
  good", "how do I make my image smaller", or "optimize my Docker setup". Also trigger
  for docker-compose files where Dockerfile content is embedded. Apply proactively even
  if the user only pastes the Dockerfile without explicit instructions.
---

# Autarqui Dockerfile Doctor

Analyze Dockerfiles and produce an optimized, safer, production-ready version with
explanations. Cover all of: layer efficiency, security hardening, caching strategy,
base image selection, and MLOps-specific patterns when relevant.

---

## Workflow

1. **Parse and understand** the Dockerfile — identify the language/runtime, package
   managers, build tool, and intended workload (web server, ML inference, CLI tool, etc.)
2. **Detect issues** across all categories below
3. **Produce the optimized Dockerfile** — rewrite, don't just annotate
4. **Explain every change** in plain language, grouped by category
5. **Give a security score** (0–100) and list remaining risks

Always produce a complete, working Dockerfile — never a partial diff the user has to
manually apply.

---

## Analysis Categories

### 1. Base Image

- Prefer slim/alpine variants unless the full image is genuinely needed
- Pin to a specific digest or at minimum a minor version tag (e.g. `python:3.11-slim`,
  not `python:latest`)
- For ML workloads: suggest CUDA-enabled base images when PyTorch/TensorFlow/JAX/vLLM
  are present (`pytorch/pytorch:2.x.x-cuda12.x-cudnn9-runtime`)
- For Go/Rust: suggest scratch or distroless as final stage after build
- Never use `:latest` in production Dockerfiles

### 2. Layer Caching & Order

- Install system dependencies before copying application code
- `COPY requirements.txt .` then `RUN pip install` BEFORE `COPY . .` — this caches
  the dependency install layer and only invalidates it when requirements change
- Group `apt-get update` and `apt-get install` in the same `RUN` — split commands
  break cache and can install stale package lists
- Sort package lists alphabetically for readability and cleaner diffs

### 3. RUN Layer Merging

Merge consecutive `RUN` commands where appropriate. The correct pattern for apt:

```dockerfile
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl \
       git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
```

Always append `apt-get clean && rm -rf /var/lib/apt/lists/*` in the same layer.
Never in a separate `RUN` — a separate layer cannot reduce the size of a prior layer.

For pip:
```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```

### 4. Multi-Stage Builds

Suggest multi-stage builds when:
- Compiled languages are present (Go, Rust, Java, C/C++)
- Build tools are installed that aren't needed at runtime (gcc, make, npm for build)
- The final image would benefit from a minimal runtime base

Pattern:
```dockerfile
FROM python:3.11 AS builder
WORKDIR /app
RUN pip install --no-cache-dir build
COPY . .
RUN python -m build

FROM python:3.11-slim AS runtime
COPY --from=builder /app/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl
```

### 5. Security Hardening

**Non-root user** — always add unless the application explicitly requires root:
```dockerfile
RUN useradd --system --no-create-home --shell /bin/false appuser
USER appuser
```
Place the `USER` directive BEFORE `CMD`/`ENTRYPOINT`, not after.

**Secret detection** — flag any of:
- `ENV SECRET=`, `ENV TOKEN=`, `ENV PASSWORD=`, `ENV KEY=`
- `ARG SECRET`, `ARG TOKEN`, `ARG PASSWORD`
- `COPY .env .`
- Secrets hardcoded in `RUN` commands (e.g. `curl -H "Authorization: Bearer abc123"`)

Suggest build-time secrets (`RUN --mount=type=secret`) or runtime injection via
environment variables from a secrets manager.

**Unsafe instructions** to flag:
- `--privileged` in docker-compose or build args
- `COPY . .` as root without `.dockerignore`
- World-writable directories (`chmod 777`)
- `curl | bash` patterns

**Missing `.dockerignore`** — note when `COPY . .` is present without evidence of
a `.dockerignore`. Suggest excluding: `.git`, `__pycache__`, `*.pyc`, `node_modules`,
`.env`, `*.log`, test directories.

### 6. Build Reproducibility

- Pinned system package versions where stability matters
- `COPY --chown=user:group` instead of a separate `RUN chown`
- `WORKDIR` should always be set explicitly; never rely on default `/`
- Use `EXPOSE` to document ports (informational, doesn't publish)
- Prefer `ENTRYPOINT` + `CMD` over `CMD` alone for the main process:
  ```dockerfile
  ENTRYPOINT ["python", "-m", "uvicorn"]
  CMD ["app:app", "--host", "0.0.0.0", "--port", "8000"]
  ```

### 7. MLOps-Specific Patterns

Trigger when: `torch`, `pytorch`, `tensorflow`, `jax`, `transformers`, `vllm`,
`bentoml`, `sagemaker`, `triton`, `onnx` appear anywhere in the Dockerfile.

- Suggest pinning CUDA/cuDNN versions to match the ML framework
- Heavy model weights should NOT be baked into images — suggest volume mounts or
  model registries (HuggingFace Hub, S3) loaded at startup
- Keep ML dependencies in a separate early layer from application code
- Consider `--platform=linux/amd64` explicitly if building on Apple Silicon

---

## Security Score

Compute a 0–100 score and explain it. Deduct:

| Issue | Deduction |
|---|---|
| Running as root | −30 |
| Hardcoded secret (ENV/ARG/RUN) | −25 |
| `.env` file copied into image | −20 |
| `curl \| bash` or similar | −15 |
| `latest` tag on base image | −10 |
| Missing `.dockerignore` with `COPY . .` | −5 |
| World-writable directory | −10 |

Score 90–100 = production-ready. 70–89 = good but review flagged items.
Below 70 = needs fixes before shipping.

---

## Output Format

Structure the response as:

1. **Summary** — 2–3 sentences: what the Dockerfile does, main issues found
2. **Optimized Dockerfile** — complete, copy-pasteable, with inline comments on
   non-obvious changes
3. **Changes explained** — grouped by category (Security, Caching, Base image, etc.)
   with a one-line rationale per change
4. **Security score** — X/100 with breakdown
5. **Remaining considerations** — things that couldn't be fixed without more context
   (e.g. "if this runs on GPU, switch base image to...")

Keep explanations concise. Developers reading this know Docker — don't over-explain
fundamentals, focus on the *why* of each specific change.

---

## Common Patterns Reference

**Python web service (minimal, correct)**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --system --no-create-home --shell /bin/false appuser
USER appuser

EXPOSE 8000
ENTRYPOINT ["python", "-m", "uvicorn"]
CMD ["app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Node.js (with build step)**
```dockerfile
FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json .
RUN npm ci --only=production

FROM node:20-slim AS runtime
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
RUN useradd --system --no-create-home appuser
USER appuser
EXPOSE 3000
CMD ["node", "server.js"]
```

**Go (distroless final image)**
```dockerfile
FROM golang:1.22 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/server .

FROM gcr.io/distroless/static-debian12
COPY --from=builder /app/server /server
EXPOSE 8080
ENTRYPOINT ["/server"]
```
