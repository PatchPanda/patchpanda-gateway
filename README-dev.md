# PatchPanda Gateway - Development Guide

Welcome to the PatchPanda Gateway development environment! This guide will walk you through setting up and running the application step by step, even if you're completely new to app development.

## 🎯 What is This?

The PatchPanda Gateway is a **GitHub App** that automatically generates tests for your code and analyzes test coverage. It's built using modern Python web technologies and provides a REST API for managing test generation jobs.

## 🚀 Quick Start (5 minutes)

If you want to get the app running quickly, follow these steps:

1. **Install dependencies**: `make install`
2. **Run the app**: `make run`
3. **Open your browser**: Go to `http://localhost:8000/docs`

That's it! You should see the FastAPI interactive documentation.

## 📋 Prerequisites

Before you start, make sure you have these installed on your computer:

### Required Software

- **Python 3.12+** - Download from [python.org](https://python.org)
- **Git** - Download from [git-scm.com](https://git-scm.com)
- **Poetry** - Python package manager (we'll install this)

### Check Your Setup

Open a terminal/command prompt and run these commands to verify:

```bash
# Check Python version (should be 3.12 or higher)
python --version

# Check Git
git --version

# Check if Poetry is installed
poetry --version
```

If any of these fail, you'll need to install the missing software first.

## 🛠️ Step-by-Step Setup

### Step 1: Install Poetry

Poetry is a modern Python package manager that makes dependency management easy.

**On macOS/Linux:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**On Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

**Alternative (using pip):**
```bash
pip install poetry
```

After installation, restart your terminal and verify:
```bash
poetry --version
```

### Step 2: Navigate to the Project

Open a terminal and navigate to the project directory:

```bash
cd /path/to/patchpanda-gateway
```

Replace `/path/to/` with the actual path to your project folder.

### Step 3: Install Dependencies

This will download and install all the Python packages the app needs:

```bash
make install
```

Or manually:
```bash
poetry install
```

**What this does:** Downloads all required libraries like FastAPI, SQLAlchemy, etc.

**Expected output:** You'll see a list of packages being installed. This might take a few minutes the first time.

### Step 4: Verify Installation

Check that everything installed correctly:

```bash
# Test if the app can be imported
poetry run python -c "from patchpanda.gateway.main import app; print('✅ Success!')"

# Run the test suite
make test
```

You should see "✅ Success!" and then tests running with "PASSED" results.

## 🚀 Running the Application

### Development Mode (Recommended for beginners)

This mode automatically reloads the app when you make changes:

```bash
make run
```

**What happens:**
1. The server starts up
2. You'll see messages like "INFO: Application startup complete"
3. The app will be available at `http://localhost:8000`

**To stop the server:** Press `Ctrl+C` in the terminal

### Production Mode

For production deployment:

```bash
make run-prod
```

## 🌐 Using the Application

### 1. Health Check

Once the server is running, test if it's working:

```bash
curl http://localhost:8000/health
```

Or open your browser and go to: `http://localhost:8000/health`

You should see: `{"status": "healthy"}`

### 2. Interactive API Documentation

The best way to explore the API is through the built-in documentation:

1. Open your browser
2. Go to: `http://localhost:8000/docs`
3. You'll see a beautiful, interactive API documentation page
4. Click on any endpoint to see details and test it

### 3. Available Endpoints

The app provides these main API endpoints:

- **`/health`** - Health check (GET)
- **`/webhooks/github`** - GitHub webhook receiver (POST)
- **`/api/coverage`** - Coverage data management (GET/POST)
- **`/api/jobs`** - Job management (GET/POST)
- **`/api/admin`** - Administrative functions (GET/POST)

## 🧪 Testing

### Run All Tests

```bash
make test
```

### Run Tests with Coverage

```bash
make test-coverage
```

This will show you how much of your code is covered by tests.

### Run Specific Tests

```bash
# Run only tests in a specific file
poetry run pytest tests/test_main.py -v

# Run tests matching a pattern
poetry run pytest -k "health" -v
```

## 🔧 Development Tools

### Code Formatting and Linting

The project uses several tools to keep code clean and consistent:

```bash
# Format code automatically
make lint

# Check code quality without making changes
make lint-check
```

**What these do:**
- **Black**: Formats Python code to be consistent
- **isort**: Organizes import statements
- **flake8**: Checks for code style issues
- **mypy**: Checks for type errors

### Database Operations

The app uses a database to store jobs, coverage data, and other information:

```bash
# Initialize database tables
make db-init

# Run database migrations
make migrate

# Create a new migration
make migrate-create name=add_new_feature

# View migration history
make migrate-history
```

## 📁 Project Structure Explained

Here's what each folder and file does:

```
patchpanda-gateway/
├─ src/patchpanda/gateway/          # Main application code
│  ├─ api/                          # API endpoints (what users call)
│  ├─ services/                     # Business logic
│  ├─ models/                       # Data structures
│  ├─ db/                          # Database code
│  ├─ security/                     # Authentication & security
│  ├─ settings.py                   # Configuration
│  └─ main.py                      # Application entry point
├─ tests/                           # Test files
├─ Makefile                         # Development commands
├─ pyproject.toml                   # Project configuration
└─ README.md                        # Project overview
```

## 🔑 Configuration

### Environment Variables

The app uses environment variables for configuration. Copy the example file:

```bash
cp env.example .env
```

Then edit `.env` with your actual values:

```bash
# Basic settings
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database (for now, use the default)
DATABASE_URL=postgresql://user:pass@localhost/patchpanda_gateway

# GitHub App (you'll get these when you create a GitHub App)
GITHUB_APP_ID=your_app_id_here
GITHUB_APP_PRIVATE_KEY=your_private_key_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
```

### Database Setup

For development, you can use SQLite (simpler) or PostgreSQL (production-like):

**SQLite (Easier for beginners):**
```bash
# Edit .env file
DATABASE_URL=sqlite:///./dev.db
```

**PostgreSQL (More realistic):**
1. Install PostgreSQL
2. Create a database: `createdb patchpanda_gateway`
3. Update `DATABASE_URL` in `.env`

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. "Command not found: poetry"

**Solution:** Poetry isn't installed or isn't in your PATH
```bash
# Reinstall Poetry
curl -sSL https://install.python-poetry.org | python3 -
# Restart your terminal
```

#### 2. "Module not found" errors

**Solution:** Dependencies aren't installed
```bash
poetry install
```

#### 3. "Port already in use" error

**Solution:** Another app is using port 8000
```bash
# Kill the process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
poetry run uvicorn patchpanda.gateway.main:app --port 8001
```

#### 4. Database connection errors

**Solution:** Check your `DATABASE_URL` in `.env`
```bash
# For SQLite (simplest)
DATABASE_URL=sqlite:///./dev.db

# For PostgreSQL
DATABASE_URL=postgresql://username:password@localhost/patchpanda_gateway
```

#### 5. Import errors in tests

**Solution:** Make sure you're running commands from the project root directory
```bash
pwd  # Should show /path/to/patchpanda-gateway
```

### Getting Help

If you're stuck:

1. **Check the error message** - It usually tells you what's wrong
2. **Verify your setup** - Make sure all prerequisites are installed
3. **Check the logs** - Look at the terminal output for clues
4. **Google the error** - Most Python errors have solutions online

## 🚀 Next Steps

Once you have the basic app running:

1. **Explore the API** - Use the interactive docs at `/docs`
2. **Read the code** - Start with `main.py` and work your way through
3. **Make changes** - Try modifying a simple endpoint
4. **Add features** - Implement one of the TODO items in the code
5. **Write tests** - Add tests for new functionality

## 📚 Learning Resources

- **FastAPI Tutorial**: [fastapi.tiangolo.com/tutorial](https://fastapi.tiangolo.com/tutorial/)
- **Python Async**: [docs.python.org/3/library/asyncio.html](https://docs.python.org/3/library/asyncio.html)
- **SQLAlchemy**: [docs.sqlalchemy.org](https://docs.sqlalchemy.org/)
- **Pydantic**: [docs.pydantic.dev](https://docs.pydantic.dev/)

## 🤝 Contributing

When you're ready to contribute:

1. **Make a small change** - Fix a typo, add a comment
2. **Test your changes** - Run `make test` to ensure nothing breaks
3. **Format your code** - Run `make lint` to keep it clean
4. **Commit your changes** - Use descriptive commit messages

## 📞 Support

If you're still having trouble:

1. **Check this guide** - Make sure you followed all steps
2. **Look at the error logs** - They often contain the solution
3. **Ask for help** - Don't hesitate to reach out to the team

Remember: **Everyone starts as a beginner!** Don't worry if something doesn't work the first time. Development is all about iteration and learning from mistakes.

---

**Happy coding! 🎉**
