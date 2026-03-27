# Skill: JDK & Python Environment Setup

## Intent
Automate discovery, installation, and configuration of JDK (Java Development Kit) and Python environments for workspace projects. Supports version selection, validation, and environment variable setup.

## Scope
- Workspace-scoped; stored at `SKILL.md` in the repo root.
- Actions apply to the current user's machine (global or local venv/conda).

## What this skill does
- **JDK operations:**
  - List all installed JDKs with versions using `list_jdks`
  - Install a specific JDK version via `install_jdk` (supported: 8, 11, 17, 21, latest)
  - Validate JDK is in PATH and usable
  
- **Python operations:**
  - Configure Python environment (venv, conda, virtualenv, pipenv, poetry, pyenv, pixi) via `configure_python_environment`
  - Retrieve environment details (type, version, installed packages) via `get_python_environment_details`
  - Get executable path and command prefix via `get_python_executable_details`

- **Orchestration:**
  - Validate both environments are ready before proceeding to build/test
  - Suggest missing tools and provide installation hints
  - Return success/failure with actionable next steps

## Workflow
1. **Detect environment type:**
   - Scan workspace for `pom.xml` (Java/Maven), `build.gradle` (Gradle), `*.java` files → JDK needed
   - Scan for `requirements.txt`, `pyproject.toml`, `poetry.lock`, `Pipfile`, `environment.yml`, `setup.py` → Python needed

2. **For JDK:**
   - Call `list_jdks` (optional: with `additionalSearchPaths`)
   - If JDK missing, call `install_jdk(version=<major_version>)`
   - Validate via `run_in_terminal` with `java -version`

3. **For Python:**
   - Call `configure_python_environment(resourcePath=<file or workspace>)`
   - Call `get_python_environment_details(resourcePath=<path>)` to inspect
   - Call `get_python_executable_details(resourcePath=<path>)` to get run command prefix

4. **Report:**
   - Return all paths, versions, and a summary "Ready to build" or list of missing tools
   - Suggest next command (e.g., "Run Maven build" or "Run pytest")

## Decision points
- **JDK version:** Infer from project metadata (pom.xml `<maven.compiler.source>`) or ask user
- **Python env:** Auto-detect type (conda > venv > system) or ask user
- **Update existing:** If tools exist, skip installation unless user explicitly requests update
- **Search paths:** For JDK, use system defaults first; offer additional search if not found

## Quality criteria
- JDK: verified with `java -version` returning non-empty output
- Python: verified with `get_python_executable_details` returning a valid command prefix
- All package versions and paths logged clearly
- If any tool is missing, suggest exact install command (e.g., `conda install python=3.11`)

## Usage examples
1. "Set up JDK and Python for this workspace."
2. "Install JDK 21 and verify it's in PATH."
3. "Check what Python version and packages are installed."
4. "Get the Python executable command for running scripts."
5. "Validate both Java and Python are ready to build this project."

## Ambiguities to resolve
- Should the skill auto-install missing JDK/Python or only suggest?
- Preferred Python version if not detected from project metadata?
- Should conda/venv environments be created automatically or only configured if they exist?

## Next customization
- Add a paired skill `maven-gradle-build` to build Java projects after JDK is verified.
- Add a `python-test-runner` skill to run tests with the configured Python environment.
