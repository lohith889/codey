# 🤖 Coding Agent

A simple, framework-free autonomous coding assistant that can plan and execute coding tasks.

## Features

- **📋 Smart Planning**: Breaks down complex tasks into manageable steps
- **🛠️ File Operations**: Read, write, edit, and list files safely
- **🧪 Testing & Verification**: Automatically runs tests and fixes failures
- **🔒 Sandboxed Execution**: Runs code in a controlled environment
- **📝 Audit Logging**: Tracks all actions for transparency and debugging
- **✨ Beautiful CLI**: Clean, emoji-enhanced command-line interface

## Installation

```bash
# Ensure you have Python 3.8+ installed
pip install openai python-dotenv
```

## Usage

### Interactive Mode

```bash
python -m Agent.cli
```

Or run directly:

```bash
python Agent/cli.py
```

### Commands

- **Task Input**: Describe what you want to accomplish
- **`/test`**: Run test commands to verify code
- **`exit`**: Quit the agent

### Example Session

```
============================================================
       🤖 CODING AGENT - Autonomous Code Assistant
============================================================

🆔 Session ID: a1b2c3d4

----------------------------------------

💬 Task (or 'exit' to quit, '/test' to run tests): Create a Python function that calculates fibonacci numbers

📋 STRUCTURING PLAN...
📋 Generating plan...
✅ Plan generated with 3 steps

📋 PROPOSED PLAN:
----------------------------------------
  1. Create fibonacci.py with the function
     📁 Files: fibonacci.py
  2. Add documentation and type hints
     📁 Files: fibonacci.py
  3. Create test file to verify correctness
     📁 Files: fibonacci.py, test_fibonacci.py

✅ Completion Criteria:
   Function correctly calculates fibonacci numbers and tests pass

✅ Approve plan? [y/n]: y

🚀 EXECUTING TASK...
...
```

## Architecture

```
Agent/
├── __init__.py      # Package exports
├── agent_core.py    # Main agent loop and LLM integration
├── cli.py           # Command-line interface
├── planner.py       # Task planning and breakdown
├── tools.py         # File operation tools
├── sandbox.py       # Safe code execution
├── verifier.py      # Test running and auto-fix
└── audit.py         # Logging and reporting
```

## Configuration

Create a `.env` file in the project root:

```env
API_KEY=your_groq_api_key_here
```

## Safety Features

- **Path Validation**: All file operations are restricted to the `./workspace` directory
- **Timeout Protection**: Sandbox commands timeout after 30 seconds
- **Iteration Limits**: Agent stops after maximum iterations to prevent loops
- **Audit Trail**: Every action is logged for review

## Customization

### Changing the Model

Edit `agent_core.py` to use a different model:

```python
run_agent_loop(task, prompt, model="your-model-name")
```

### Adjusting Iteration Limits

```python
run_agent_loop(task, prompt, max_iter=100)  # Default is 50
```

### Modifying Retry Attempts

```python
verify_and_iterate(cmd, max_retries=5)  # Default is 3
```

## License

MIT License
