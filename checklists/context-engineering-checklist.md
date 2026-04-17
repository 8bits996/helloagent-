# Context Engineering Checklist

> **Use this checklist to ensure proper context engineering practices**

---

## 📋 Before Starting a Session

### Project Context Setup

- [ ] **CLAUDE.md exists** and is up-to-date
  - Check last modified date
  - Ensure tech stack is current
  - Verify coding standards are accurate

- [ ] **AGENTS.md exists** and points to relevant documentation
  - All links are valid
  - Documentation is organized logically
  - Quick navigation works

- [ ] **.cursorrules/.claude rules** defined
  - Project-specific rules are set
  - Code style guidelines are clear
  - Security rules are defined

- [ ] **Documentation is recent**
  - API docs are current
  - Architecture diagrams reflect reality
  - README is accurate

---

## 🧠 During Session

### Context Management

- [ ] **Model has access to relevant files**
  - Open necessary files in editor
  - Ensure correct working directory
  - Verify file paths are correct

- [ ] **Tools are appropriately scoped**
  - Not too many tools (overwhelms model)
  - Not too few tools (limits capability)
  - Tools match task requirements

- [ ] **Conversation history is managed**
  - Avoid context bloat from long conversations
  - Summarize or compact if needed
  - Keep relevant context, discard noise

- [ ] **Token budget is monitored**
  - Be aware of context window limits
  - Use efficient prompts
  - Consider compacting at 80% usage

---

## 🔍 Context Quality Checks

### Information Density

- [ ] **Each token provides value**
  - No redundant information
  - Clear and concise descriptions
  - Relevant examples included

- [ ] **Noise is minimized**
  - Remove outdated information
  - Avoid unnecessary context
  - Keep focus on task at hand

- [ ] **Signal is maximized**
  - Include critical constraints
  - Specify expected outcomes
  - Provide relevant examples

### Context Structure

- [ ] **Information is organized logically**
  - Start with high-level context
  - Follow with specific details
  - End with task description

- [ ] **Related information is grouped**
  - Similar concepts together
  - Dependencies clearly marked
  - Cross-references included

- [ ] **Priority is clear**
  - Most important information first
  - Secondary information follows
  - Nice-to-have details at end

---

## 📚 After Session

### Knowledge Capture

- [ ] **Update CLAUDE.md with new learnings**
  - New patterns discovered
  - Pitfalls to avoid
  - Best practices identified

- [ ] **Add new patterns to documentation**
  - Update existing docs
  - Create new docs if needed
  - Ensure team can find it

- [ ] **Remove outdated information**
  - Delete deprecated practices
  - Update changed workflows
  - Archive old docs

- [ ] **Share useful context files with team**
  - Commit updated files
  - Notify team of changes
  - Document why changes were made

---

## 🎯 Task-Specific Context

### For New Features

- [ ] **Architecture context provided**
  - System design overview
  - Related components identified
  - Integration points documented

- [ ] **Requirements clearly stated**
  - User stories or specifications
  - Acceptance criteria
  - Constraints and limitations

- [ ] **Examples of similar features**
  - Reference existing code
  - Show desired patterns
  - Highlight anti-patterns

### For Bug Fixes

- [ ] **Error context provided**
  - Stack trace or error message
  - Steps to reproduce
  - Expected vs actual behavior

- [ ] **Related code context**
  - Files where bug occurs
  - Dependencies involved
  - Recent changes that might have caused it

- [ ] **Test context included**
  - Existing tests for the area
  - Test coverage status
  - How to verify the fix

### For Refactoring

- [ ] **Current state documented**
  - What exists now
  - Why it needs refactoring
  - Pain points identified

- [ ] **Desired state defined**
  - Target architecture
  - Expected benefits
  - Migration path

- [ ] **Constraints identified**
  - Cannot break existing functionality
  - Performance requirements
  - Timeline constraints

---

## 🚨 Common Context Mistakes

### Too Much Context

- [ ] **Avoid: Dumping entire codebase**
  - Use targeted file selection
  - Summarize large files
  - Focus on relevant sections

- [ ] **Avoid: Including every detail**
  - Prioritize critical information
  - Use references instead of full content
  - Link to external docs

- [ ] **Avoid: Overwhelming tool descriptions**
  - Keep descriptions concise
  - Use clear naming
  - Provide examples, not just schemas

### Too Little Context

- [ ] **Avoid: Assuming model knows everything**
  - Provide project background
  - Explain conventions
  - Define acronyms and jargon

- [ ] **Avoid: Vague task descriptions**
  - Be specific about requirements
  - Define success criteria
  - Provide examples

- [ ] **Avoid: Missing constraints**
  - State limitations upfront
  - Define what NOT to do
  - Specify security requirements

---

## 📊 Token Budget Management

### Typical 200K Token Budget

| Category | Allocation | Tokens | Description |
|----------|------------|--------|-------------|
| System & Rules | 10% | 20K | CLAUDE.md, .cursorrules, tool descriptions |
| Conversation History | 20% | 40K | Previous messages, context from earlier in session |
| Code Context | 40% | 80K | Active files, related files, dependencies |
| Output Buffer | 30% | 60K | Reserved for model's response generation |

### When to Compact Context

- [ ] **Token usage > 80% of budget**
  - Consider compacting conversation
  - Summarize key points
  - Remove outdated context

- [ ] **Conversation > 20 turns**
  - Review if early context is still relevant
  - Summarize decisions made
  - Archive completed tasks

- [ ] **Multiple tool calls with large outputs**
  - Process and summarize results
  - Extract key information
  - Discard verbose logs

---

## ✅ Context Engineering Best Practices

### Do's ✅

- **Do**: Start with high-level context, then drill down
- **Do**: Use consistent formatting and structure
- **Do**: Provide concrete examples over abstract descriptions
- **Do**: Update context as project evolves
- **Do**: Share learnings with team
- **Do**: Use version control for context files
- **Do**: Review context files regularly

### Don'ts ❌

- **Don't**: Assume model remembers from previous sessions
- **Don't**: Overload context with unnecessary details
- **Don't**: Use context as a substitute for clear communication
- **Don't**: Ignore token limits
- **Don't**: Let context files become outdated
- **Don't**: Duplicate information across multiple files
- **Don't**: Skip context setup to save time

---

## 🔧 Tools & Resources

### Context File Templates

- **CLAUDE.md**: `templates/claude-md-template.md`
- **.cursorrules**: `templates/cursorrules-template.md`
- **AGENTS.md**: `templates/agents-md-template.md`

### Token Counting

```bash
# Estimate token count for a file
wc -w file.txt  # Rough estimate: words / 0.75 = tokens

# Use tiktoken for accurate count
python -c "import tiktoken; print(len(tiktoken.get_encoding('cl100k_base').encode(open('file.txt').read())))"
```

### Context Compact Prompt

```
Summarize the key information from this conversation:
- Main task: [what was being worked on]
- Decisions made: [list decisions]
- Files modified: [list files]
- Next steps: [what's left to do]
- Important patterns: [what was learned]
```

---

## 📝 Quick Reference

### Context Hierarchy

1. **System Level**: Global rules and conventions
2. **Project Level**: CLAUDE.md, architecture, tech stack
3. **Session Level**: Current task, active files, conversation history
4. **Turn Level**: Immediate context, last few messages

### Information Prioritization

1. **Critical**: Must-have for task completion
2. **Important**: Significantly improves output quality
3. **Useful**: Nice to have, but not essential
4. **Optional**: Can be referenced if needed

---

**Remember**: Context engineering is about **quality over quantity**. The goal is to provide the right information at the right time, not to dump everything you know.
