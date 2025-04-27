# Use the official Python 3.13 image as the base image
FROM python:3.13-slim-bookworm

# Set the working directory in the container
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=camp_app/uv.lock,target=uv.lock \
    --mount=type=bind,source=camp_app/pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Copy the contents of Camp_app to the working directory
COPY camp_app/ /app/

# Expose the default Streamlit port
EXPOSE 8501

# Set Streamlit environment variables
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Command to run the Streamlit app
CMD ["streamlit", "run", "camp_app.py", "--server.address=0.0.0.0", "--server.port=8501"]