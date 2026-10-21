# ==============================================================================
# NEXUS-ANALYTICS: Multi-Stage Production Container
# Architecture: Python 3.12-slim / Non-Root Secure Execution
# Services: Streamlit Executive Decision Cockpit & Typer Pipeline CLI
# ==============================================================================

FROM python:3.12-slim AS builder

WORKDIR /build

# Install compilation tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies into wheels
COPY pyproject.toml .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir build && \
    pip wheel --no-cache-dir --wheel-dir /build/wheels -e ".[ui]"

# ==============================================================================
# Final Runtime Stage
# ==============================================================================
FROM python:3.12-slim AS runner

LABEL maintainer="Rohit <rrathod1101@gmail.com>"
LABEL repository="https://github.com/Rohittt619/NEXUS-ANALYTICS"
LABEL description="Enterprise Customer Intelligence, Churn Causality, CLV & Campaign ROI Optimization Engine"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_THEME_BASE=dark \
    STREAMLIT_THEME_PRIMARY_COLOR="#00ADB5" \
    STREAMLIT_THEME_BACKGROUND_COLOR="#0F172A" \
    STREAMLIT_THEME_SECONDARY_BACKGROUND_COLOR="#1E293B" \
    STREAMLIT_THEME_TEXT_COLOR="#F8FAFC"

WORKDIR /app

# Install minimal runtime libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root application user
RUN groupadd -r nexusgroup && useradd -r -g nexusgroup -u 1001 nexususer

# Install pre-built wheels
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Copy application source tree
COPY . /app
RUN pip install --no-cache-dir -e ".[ui]"

# Configure permissions for non-root execution
RUN chown -R nexususer:nexusgroup /app
USER nexususer

# Healthcheck pinging Streamlit endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "src/nexus/ui/app.py"]
