#!/usr/bin/env bash
set -e
set -o pipefail

# -----------------------
# Step 0: Clone repository
# -----------------------
REPO_URL="https://github.com/rueedlinger/antplus-metrics"
REPO_DIR="antplus-metrics"

echo "📥 Cloning repository..."
if [ ! -d "$REPO_DIR" ]; then
    git clone "$REPO_URL"
else
    echo "⚠️ Repository already exists. Pulling latest changes..."
    cd "$REPO_DIR" && git pull && cd ..
fi

# Work in parent directory
cd "$REPO_DIR"

# -----------------------
# Step 1: Build frontend
# -----------------------


echo "📦 Building frontend..."
cd frontend

# Ensure Node.js is installed
if ! command -v node >/dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js v20+."
    exit 1
fi

echo "Node version: $(node -v)"
echo "npm version: $(npm -v)"

npm install --include=dev
npm install @tailwindcss/vite

npm run build
echo "✅ Frontend build complete."
cd ..

# -----------------------
# Step 2: Setup backend
# -----------------------
echo "🐍 Setting up backend..."

# Ensure Python 3.14+ is installed
if ! command -v python3 >/dev/null; then
    echo "❌ Python3 is not installed."
    exit 1
fi

# python3 -m pip install --upgrade pip

# Install uv if not installed
if ! command -v uv >/dev/null; then
    pip install uv
fi

echo "Python version: $(python3 --version)"

# Sync all dependencies via uv (Poetry alternative)
uv sync --all-groups

# Copy frontend build into backend dist folder
mkdir -p app/dist
cp -r frontend/dist/* app/dist/

echo "✅ Backend setup complete."

# -----------------------
# Step 3: Create start script
# -----------------------
START_SCRIPT="start.sh"
cat > "$START_SCRIPT" << 'EOF'
#!/usr/bin/env bash
echo "🚀 Starting server on port 8000..."
uv run uvicorn app.api:app --reload --host 0.0.0.0 --port 8000 --timeout-graceful-shutdown 1  --log-config logging.conf
EOF

chmod +x "$START_SCRIPT"
echo "✅ Start script created: $START_SCRIPT"
echo "You can now run the server with ./$START_SCRIPT"