---
description: Deep code review for Python and TypeScript code focusing on architecture, design principles, and code quality
handoffs: 
  - label: Fix Code Issues
    agent: speckit.implement
    prompt: Fix the code quality issues identified in the review
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/codereview` in the triggering message specifies the scope of the code review (file paths, directories, or entire project). If empty, review all backend and frontend code.

Given the scope, perform a comprehensive code review following these steps:

1. **Determine Review Scope**:
   - Parse the user input to identify target files or directories
   - If no specific files provided, default to:
     - Backend: `backend/src/**/*.py`
     - Frontend: `frontend/src/**/*.{ts,tsx}`
   - List all files to be reviewed
   - Show file count and estimated review time

2. **Architecture & Design Analysis**:

   a. **Python Backend Architecture**:
      - ✅ **Service Layer Pattern**: Services are properly separated (db_connection, metadata_extractor, query_executor, nl_converter, storage)
      - ✅ **Dependency Injection**: Check if services use DI or global instances
      - ✅ **Interface Design**: Verify clear service interfaces and abstractions
      - ✅ **Separation of Concerns**: API layer, service layer, data access layer properly separated
      - ✅ **Design Patterns**: Identify and validate use of appropriate patterns (Factory, Strategy, Repository, etc.)
      - ⚠️ **Extensibility**: Can new database types be added without modifying existing code? (Open-Closed Principle)
      - ⚠️ **Coupling**: Are services tightly coupled or properly decoupled?

   b. **TypeScript Frontend Architecture**:
      - ✅ **Component Structure**: Smart vs. presentational component separation
      - ✅ **State Management**: Appropriate use of hooks, context, or external state management
      - ✅ **Custom Hooks**: Reusable logic extracted to custom hooks
      - ✅ **Type Safety**: Proper TypeScript types, interfaces, no `any` types
      - ✅ **API Layer**: Centralized API calls in service layer
      - ⚠️ **Props Drilling**: Excessive prop drilling indicates poor architecture
      - ⚠️ **Component Size**: Components should be focused and under 300 lines

   c. **Cross-Cutting Concerns**:
      - Error handling strategy (consistent across codebase)
      - Logging and monitoring approach
      - Configuration management
      - Security considerations (SQL injection prevention, XSS, CSRF)

3. **KISS Principle (Keep It Simple, Stupid)**:

   a. **Complexity Analysis**:
      - ✅ **Cyclomatic Complexity**: Functions/methods should have low cyclomatic complexity (< 10)
      - ✅ **Nested Conditionals**: Max 3 levels of nesting
      - ✅ **Function Length**: Functions should be under 150 lines
      - ⚠️ **Over-Engineering**: Are there simpler solutions to the same problem?
      - ⚠️ **Premature Optimization**: Code optimized before proven necessary
      - ⚠️ **Clever Code**: Code that's "clever" but hard to understand

   b. **Redundancy Detection**:
      - Duplicate code blocks (DRY violation)
      - Similar functions/methods that could be refactored
      - Repeated logic in multiple files
      - Unused imports, variables, functions
      - Dead code that's never executed

   c. **Unnecessary Complexity Examples**:
      - Complex list comprehensions that could be simple loops
      - Nested ternary operators
      - Over-abstraction (too many layers)
      - Unnecessary class hierarchies
      - Complex regex when simple string operations suffice

4. **Code Quality Principles**:

   a. **DRY (Don't Repeat Yourself)**:
      - Scan for duplicate code blocks (3+ lines)
      - Identify repeated logic that should be extracted to functions
      - Check for copy-paste code across files
      - Suggest refactoring opportunities

   b. **YAGNI (You Aren't Gonna Need It)**:
      - Unused functions, classes, or modules
      - Over-generalized code for hypothetical future needs
      - Features that aren't currently being used
      - Placeholder code marked with TODO but never implemented

   c. **SOLID Principles**:
      - **S**ingle Responsibility: Does each class/function have one clear purpose?
      - **O**pen-Closed: Can behavior be extended without modifying existing code?
      - **L**iskov Substitution: Are subclasses truly substitutable?
      - **I**nterface Segregation: Are interfaces focused and minimal?
      - **D**ependency Inversion: Do high-level modules depend on abstractions?

   d. **Naming Conventions**:
      
      **Python**:
      - ✅ `snake_case` for functions, variables, methods
      - ✅ `PascalCase` for classes
      - ✅ `UPPER_CASE` for constants
      - ✅ Descriptive names (avoid `x`, `tmp`, `data` unless loop counters)
      - ✅ Boolean variables start with `is_`, `has_`, `can_`, `should_`
      - ⚠️ Abbreviations: Use sparingly, prefer readability
      
      **TypeScript**:
      - ✅ `camelCase` for functions, variables, methods
      - ✅ `PascalCase` for classes, interfaces, type aliases, components
      - ✅ `UPPER_CASE` for constants
      - ✅ Interface names: `IUser` or `User` (consistent project-wide)
      - ✅ Component filenames: `PascalCase.tsx`
      - ✅ Boolean variables: `isLoading`, `hasError`, `canSubmit`

   e. **Documentation & Comments**:
      
      **Python**:
      - ✅ Docstrings for all public functions/classes (Google or NumPy style)
      - ✅ Type hints on all function signatures
      - ✅ Module-level docstrings
      - ⚠️ Comments explain "why", not "what"
      - ❌ No commented-out code
      - ❌ No misleading or outdated comments
      
      **TypeScript**:
      - ✅ JSDoc for complex functions and public APIs
      - ✅ Inline comments for non-obvious logic
      - ✅ README for component usage (if library/shared)
      - ⚠️ Comments explain "why", not "what"
      - ❌ No commented-out code

   f. **Function Constraints**:
      - ✅ **Max 150 lines** per function (excluding docstrings)
      - ✅ **Max 6 parameters** per function
      - ⚠️ Use objects/dicts for functions needing more parameters
      - ⚠️ Functions with default parameters: defaults at the end

5. **Generate Review Report**:

   Create a comprehensive markdown report with this structure:

   ```markdown
   # Code Review Report: [Scope]
   
   **Date**: [Current Date]
   **Reviewer**: AI Code Review Agent
   **Files Reviewed**: [Count]
   **Lines of Code**: [Total]
   
   ## Executive Summary
   
   - **Overall Grade**: [A/B/C/D/F]
   - **Critical Issues**: [Count]
   - **Major Issues**: [Count]
   - **Minor Issues**: [Count]
   - **Suggestions**: [Count]
   
   ### Top 3 Concerns
   
   1. [Most critical issue with impact]
   2. [Second most critical issue]
   3. [Third most critical issue]
   
   ## Architecture Review
   
   ### Python Backend
   
   #### ✅ Strengths
   - [List architectural strengths]
   
   #### ⚠️ Issues
   - [List architectural issues with severity]
   
   #### 💡 Recommendations
   - [Specific actionable recommendations]
   
   ### TypeScript Frontend
   
   #### ✅ Strengths
   - [List architectural strengths]
   
   #### ⚠️ Issues
   - [List architectural issues with severity]
   
   #### 💡 Recommendations
   - [Specific actionable recommendations]
   
   ## KISS Principle Analysis
   
   ### Complexity Hotspots
   
   | File | Function | Complexity | Issue |
   |------|----------|------------|-------|
   | [file] | [function] | [score] | [description] |
   
   ### Redundancy Report
   
   - **Duplicate Code Blocks**: [Count and locations]
   - **Similar Functions**: [List with refactoring suggestions]
   - **Unused Code**: [List for removal]
   
   ## Code Quality Assessment
   
   ### DRY Violations
   
   #### Critical Duplications
   
   **[File1:LineX] and [File2:LineY]**
   ```language
   [Duplicate code block]
   ```
   
   **Recommendation**: Extract to [suggested location and name]
   
   ### YAGNI Violations
   
   - [List unused code with removal recommendations]
   
   ### SOLID Principle Violations
   
   #### Single Responsibility Violations
   
   **File**: [path]
   **Issue**: [Description]
   **Recommendation**: [How to fix]
   
   #### Open-Closed Violations
   
   [Similar format]
   
   ### Naming Convention Issues
   
   | File | Line | Current Name | Suggested Name | Reason |
   |------|------|--------------|----------------|--------|
   | [file] | [line] | [name] | [better_name] | [explanation] |
   
   ### Documentation Issues
   
   #### Missing Docstrings
   
   - [List of functions missing docstrings]
   
   #### Misleading Comments
   
   - [File:Line] - [Comment vs actual behavior]
   
   ### Function Constraint Violations
   
   #### Functions > 150 Lines
   
   | File | Function | Lines | Recommendation |
   |------|----------|-------|----------------|
   | [file] | [func] | [count] | [how to split] |
   
   #### Functions > 6 Parameters
   
   | File | Function | Params | Recommendation |
   |------|----------|--------|----------------|
   | [file] | [func] | [count] | [use object/dict] |
   
   ## Detailed Findings
   
   ### Critical Issues (Fix Immediately)
   
   #### [Issue Type]: [Title]
   
   **File**: [path:line]
   **Severity**: Critical
   **Impact**: [Security/Performance/Correctness]
   
   **Current Code**:
   ```language
   [problematic code]
   ```
   
   **Issue**: [Detailed explanation]
   
   **Recommended Fix**:
   ```language
   [suggested code]
   ```
   
   **Rationale**: [Why this is better]
   
   ### Major Issues (Fix Soon)
   
   [Same format as Critical]
   
   ### Minor Issues (Consider Fixing)
   
   [Same format, less detail]
   
   ### Suggestions (Nice to Have)
   
   [Brief list with quick wins]
   
   ## Security Concerns
   
   - SQL Injection risks: [List with locations]
   - XSS vulnerabilities: [List with locations]
   - Sensitive data exposure: [List with locations]
   - Authentication/Authorization gaps: [List]
   
   ## Performance Concerns
   
   - N+1 query patterns: [List with locations]
   - Inefficient algorithms: [List with complexity]
   - Memory leaks: [Potential issues]
   - Unnecessary re-renders (React): [List]
   
   ## Testing Gaps
   
   - Files without tests: [Count and list]
   - Low coverage areas: [List functions/modules]
   - Missing edge case tests: [List]
   
   ## Positive Highlights
   
   - [List excellent code examples worth praising]
   - [Design patterns used well]
   - [Clean, maintainable code sections]
   
   ## Action Plan
   
   ### Immediate (This Week)
   
   1. [Fix critical issue 1]
   2. [Fix critical issue 2]
   
   ### Short Term (This Month)
   
   1. [Fix major issues]
   2. [Refactor duplicate code]
   
   ### Long Term (This Quarter)
   
   1. [Architectural improvements]
   2. [Documentation updates]
   
   ## Metrics
   
   - **Code Quality Score**: [0-100]
   - **Maintainability Index**: [0-100]
   - **Technical Debt Ratio**: [X hours/Y LOC]
   - **Estimated Refactoring Effort**: [hours]
   
   ## Conclusion
   
   [Overall assessment and key takeaways]
   ```

6. **Review Execution Flow**:

   a. **Load All Target Files**:
      - Read each file into memory
      - Parse Python files to extract AST (Abstract Syntax Tree)
      - Parse TypeScript files to extract type information
      - Calculate metrics (LOC, complexity, etc.)

   b. **Run Analysis Passes**:
      
      **Pass 1: Architecture Review**
      - Map dependencies between modules
      - Identify design patterns
      - Check layer separation
      - Validate interfaces and abstractions
      
      **Pass 2: KISS Analysis**
      - Calculate cyclomatic complexity per function
      - Find duplicate code blocks (fuzzy matching)
      - Identify nested conditionals > 3 levels
      - Find functions > 150 lines
      
      **Pass 3: Principle Validation**
      - Check DRY violations
      - Find YAGNI violations (unused code)
      - Validate SOLID principles
      - Check naming conventions against rules
      - Verify documentation completeness
      - Find functions with > 6 parameters
      
      **Pass 4: Security & Performance**
      - SQL injection patterns (raw SQL concatenation)
      - XSS vulnerabilities (dangerouslySetInnerHTML without sanitization)
      - Authentication bypasses
      - N+1 query patterns
      - Inefficient algorithms (O(n²) when O(n) possible)

   c. **Aggregate Results**:
      - Categorize findings by severity
      - Calculate metrics
      - Generate recommendations
      - Create action plan

7. **Save Review Report**:
   - Write report to `.github/code-reviews/review-[timestamp].md`
   - Create index entry in `.github/code-reviews/index.md`
   - Update metrics dashboard (if exists)

8. **Present Summary**:
   - Show top 3 critical issues
   - Display overall grade
   - Provide link to full report
   - Suggest immediate actions

## General Guidelines

### Review Tone

- **Constructive**: Focus on improvement, not criticism
- **Specific**: Provide exact locations and concrete examples
- **Actionable**: Every issue should have a clear fix
- **Balanced**: Highlight both problems and good practices
- **Educational**: Explain *why* something is an issue

### False Positive Handling

- **Context Matters**: Consider the specific use case before flagging
- **Framework Conventions**: Some patterns are framework-specific and correct
- **Performance Trade-offs**: Sometimes complexity is justified for performance
- **Legacy Code**: Document issues but be realistic about refactoring scope

### Severity Definitions

- **Critical**: Security vulnerabilities, data corruption risks, crashes
- **Major**: Performance issues, poor architecture, significant maintainability problems
- **Minor**: Style issues, minor DRY violations, missing comments
- **Suggestion**: Potential improvements, alternative approaches

### Python-Specific Checks

- Type hints on all function signatures (PEP 484)
- f-strings over `.format()` or `%` (Python 3.6+)
- List/dict comprehensions used appropriately (not over-complex)
- Context managers (`with` statements) for resources
- Proper exception handling (specific exceptions, not bare `except:`)
- Async/await used correctly (if applicable)
- Pydantic models properly validated

### TypeScript-Specific Checks

- No `any` types (use `unknown` or proper types)
- Proper null/undefined handling with optional chaining
- React hooks rules followed (dependencies array, custom hooks)
- Props properly typed with interfaces
- Async operations properly handled (loading states, errors)
- Memoization used appropriately (useMemo, useCallback, React.memo)
- Key prop on list items

### Code Examples in Report

- Show both problematic code and suggested fix
- Include line numbers and file paths
- Syntax highlight code blocks
- Keep examples concise (< 20 lines)
- Add comments explaining the issue

### Metrics Calculation

**Code Quality Score** (0-100):
- Architecture: 30%
- KISS adherence: 20%
- SOLID principles: 20%
- Documentation: 15%
- Security: 15%

**Maintainability Index**:
- Based on cyclomatic complexity, LOC, and documentation
- Formula: `171 - 5.2 * ln(avg_complexity) - 0.23 * avg_loc - 16.2 * ln(comment_ratio)`

**Technical Debt Ratio**:
- Estimated hours to fix all issues / Total LOC * 1000
- < 5: Excellent
- 5-10: Good
- 10-20: Fair
- > 20: Poor

### Output Format

- Use markdown tables for structured data
- Use code fences with language tags
- Use emojis for visual scanning (✅ ⚠️ ❌ 💡)
- Link to relevant files with line numbers
- Include collapsible sections for long details

## Special Considerations

### Current Codebase Context

Based on `instructions.md`, this project:
- Backend: Python/FastAPI with Pydantic models
- Frontend: React/TypeScript with Ant Design
- Uses SQLite for metadata storage
- Supports PostgreSQL and MySQL databases
- Uses OpenAI SDK for natural language queries
- All backend data uses camelCase
- No authentication required

**Key Architecture Points to Validate**:
1. Database type abstraction (PostgreSQL vs MySQL)
2. Metadata extraction strategy
3. SQL query validation and safety
4. Natural language to SQL conversion
5. Frontend/backend type alignment

### Common Pitfalls in This Stack

**Python/FastAPI**:
- Missing async/await on database operations
- Not using dependency injection for services
- Pydantic models not using `ConfigDict` (deprecated `Config` class)
- SQL injection via string concatenation
- Missing error handling on external API calls (OpenAI)

**React/TypeScript**:
- `any` types leaking from API responses
- Not memoizing expensive computations
- Missing loading/error states
- Props drilling instead of context
- Inline styles instead of styled components/CSS modules

### Review Scope Guidelines

- **Small changes** (1-5 files): Detailed line-by-line review
- **Medium changes** (5-20 files): Focus on architecture and major issues
- **Large changes** (20+ files): High-level architecture review, sample detailed review

### Follow-up Actions

After presenting the review:

1. **If critical issues found**:
   - Offer to fix them immediately
   - Create GitHub issues for tracking
   - Block merge/deployment

2. **If only minor issues**:
   - Provide quick fix suggestions
   - Offer to create a refactoring plan
   - Allow merge with follow-up tasks

3. **If excellent code**:
   - Praise specific examples
   - Document good patterns for team reference
   - Suggest sharing as code examples
