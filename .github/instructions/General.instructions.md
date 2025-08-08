---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.

**Important**

Feedback Automation Guideline:
After completing any task, ALWAYS request interactive feedback through the MCP (interactive-feedback-mcp) before ending your session or reply. Do not pause or wait for user confirmation before proceeding to the feedback step—automatically request feedback as the final action for every task.

After you respond to any feedback received through the MCP, you MUST immediately request interactive feedback through the MCP again, and continue this loop after every feedback response. Repeat this process until the user indicates there is no more feedback to provide through the MCP. Only then may you end your session or reply.

**Documentation**
Use Context7 MCP when searching for documentation

**Important**

**Test/Diagnose/Demo Script Location Guideline:**
Before generating any Test/Diagnose/Demo scripts, always check if a `tests` folder exists in the workspace and create a new one if it doesn't. Save all new Test/Diagnose/Demo scripts in that folder.

**Report Location Guideline:**
Before generating any .md files, always check if a `reports` folder exists in the workspace and create a new one if it doesn't. Save all new report files in that folder.

**Logging Location Guideline:**
Before generating any log files, always check if a `logs` folder exists in the workspace and create a new one if it doesn't. Save all new log files in that folder.

**Markdown (.md) Report Guideline:**
Always use Mermaid for diagrams in Markdown reports. Use the `mermaid` code block format for all diagrams.

**Important:** Never attempt to create or manage Python environments (e.g., virtualenv, conda, venv) in any model or automation. Always assume the Python environment is pre-configured and managed externally. Do not include code or instructions for environment creation, activation, or modification.

**PowerShell Python Execution Guideline:**
Do not to run long commands in the terminal, instead write code in a file and run that file.

**Zen MCP Strategic Delegation Guideline:**
ALWAYS leverage Zen MCP tools for enhanced development workflows. Before implementing any complex task, use mcp_zen_chat to get strategic advice on which tools to use:

1. **Start-of-Prompt Protocol:**
   - For any complex task, FIRST ask mcp_zen_chat: "I need to [TASK]. What Zen MCP tools should I use and in what order?"
   - Use `thinking_mode: "high"`
   - Always enable `use_websearch: true` for current best practices

2. **Immediate Delegation Triggers:**
   - Tasks requiring >5 implementation steps
   - Security or performance critical requirements
   - Code analysis >10 files or multiple systems
   - Architecture or technology decisions
   - Complex debugging or root cause analysis

3. **Core Tool Usage Patterns:**
   - **Strategic Planning:** `mcp_zen_chat` → `mcp_zen_planner` → implement
   - **Complex Analysis:** `mcp_zen_analyze` → implement → `mcp_zen_codereview`
   - **Bug Investigation:** `mcp_zen_debug` → `mcp_zen_tracer` → implement fixes
   - **Critical Decisions:** `mcp_zen_consensus` for multi-perspective validation
   - **Security Tasks:** ALWAYS use `mcp_zen_secaudit` for security-critical implementations

4. **Context Window Optimization (1M tokens):**
   - Include entire large files instead of fragments when delegating
   - Provide complete context including business requirements and constraints
   - Use continuation IDs for multi-step workflows
   - Leverage Google integration for real-time information

5. **Quality Assurance Protocol:**
   - Use systematic workflows for comprehensive analysis
   - Validate critical findings with `mcp_zen_challenge` tool
   - Employ confidence tracking (exploring → certain) for completeness
   - Always request expert validation for complex implementations

**Golden Rule:** When in doubt about complexity, start with `mcp_zen_chat` to get strategic advice before implementing. This ensures optimal use of the 1M context window and Google integration.