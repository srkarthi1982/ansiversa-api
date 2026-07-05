# Formula Finder Market Study

## Document Status

**Status:** Living Document

**Market Version:** 1

**Created:** 2026-07-05

**Last Reviewed:** 2026-07-05

**Next Review:** During the next scheduled product improvement cycle or whenever significant market changes occur.

**Purpose**

This document captures external market intelligence for this solution.

It is intended to help Product discussions and future planning.

This document does **not** define product requirements or implementation commitments.

All product decisions require Partner approval and are reflected separately in `destination.md`.

## Purpose

This document captures market intelligence for Formula Finder so future product
decisions can be grounded in public competitor patterns, user pain points, and
Ansiversa's platform direction.

This is research only. It does not copy competitor wording, formulas, solution
layouts, UI, screenshots, or proprietary workflows, and it does not recommend
immediate implementation.

## Problem Statement

Students and professionals often know the concept they need but cannot quickly
find the right formula, understand each variable, choose the correct unit, or
see when a formula applies. Search engines and math solvers can answer specific
problems, but users still need a clean reference layer for formulas, meanings,
examples, and related concepts.

The market is crowded around problem solving, equation solving, and calculators.
Formula Finder has a different core problem: helping users locate and understand
the right formula before calculation or homework solving begins.

## Target Users

- School and college students studying math, physics, chemistry, finance, or
  statistics.
- Test-prep learners who need quick formula recall.
- Teachers preparing examples and reference material.
- Tutors explaining formulas across subjects.
- Engineers, analysts, and professionals checking formulas.
- Learners who need variable definitions and units, not just answers.
- Users who want a lightweight reference instead of a full symbolic solver.

## Competitor Landscape

### Direct Competitors

- Wolfram Alpha: Broad computational engine for math, science, units, finance,
  and many technical domains. It competes on depth, natural-language queries,
  alternate forms, graphs, and expert-level computation.
- Symbolab: Step-by-step calculator covering algebra, calculus, linear algebra,
  and many math topics. It competes on guided solving and topic-specific
  calculators.
- Mathway: Broad math problem solver with typed and photo input. It competes on
  convenience, topic breadth, and step-by-step explanations.
- Microsoft Math Solver: Math-help workflow with scan, solve, steps, graphing,
  and supplemental learning resources. It competes on accessibility and free
  utility.
- Photomath: Camera-first math solver with step-by-step explanations. It
  competes on instant capture and learner-friendly walkthroughs.
- Desmos: Graphing and calculator ecosystem used widely in classrooms. It
  competes on visualization, interactivity, graph sharing, and free access.
- CalculatorSoup, Omni Calculator, and specialized formula calculators: Compete
  as quick reference/calculator pages for specific formulas and domains.

### Indirect Competitors

- Google Search formula snippets and calculator cards.
- Textbooks, cheat sheets, and printable formula sheets.
- Khan Academy and other education platforms.
- YouTube explainers and worked examples.
- Spreadsheet templates and calculator apps.
- Course notes, class handouts, and exam reference sheets.
- AI assistants that can explain or derive formulas on demand.

### AI-Based Alternatives

- ChatGPT: Can explain formulas, variables, derivations, examples, and unit
  conversions, but can hallucinate or overgeneralize if not checked.
- Claude: Useful for longer conceptual explanation and comparing formulas across
  contexts.
- Gemini: Useful for search-adjacent and Google Workspace workflows.
- AI math tutors and solvers: Increasingly combine photo input, equation
  solving, tutoring, and formula explanation.

AI assistants compete because users can ask "which formula do I need?" in
natural language. Dedicated products win when formulas are structured,
reviewable, source-grounded, and organized for repeated reference.

## Common Market Features

- Search by formula name, topic, variable, or problem type.
- Formula cards with variables and units.
- Worked examples and substitutions.
- Step-by-step solving for equations.
- Graphing and visualization.
- Camera input for written or printed problems.
- Natural-language math queries.
- Topic libraries for algebra, calculus, physics, chemistry, finance, and
  statistics.
- Unit conversion and dimensional analysis.
- Related formulas and alternate forms.
- Favorites, saved formulas, and history.
- Premium steps, advanced explanations, or ad-free access.

## What Users Appear to Love

- Fast answers when stuck.
- Step-by-step explanations that show process, not just final result.
- Camera input for problems copied from textbooks or worksheets.
- Graphs and visuals that make relationships understandable.
- Broad topic coverage in one place.
- Free tools such as Desmos and Microsoft-style solvers.
- Formula and calculator pages that reduce setup work.
- Variable definitions and examples that reduce misapplication.

## Common Complaints / Friction

- Problem solvers can become answer shortcuts instead of learning tools.
- Step-by-step explanations are often behind paywalls.
- Some tools produce correct answers but weak conceptual explanation.
- Users may not know whether a formula applies to their exact situation.
- Math notation input can be frustrating on mobile.
- Camera recognition can fail on handwriting, complex layouts, or poor images.
- Broad solvers may feel too technical for beginner learners.
- Formula sites can be ad-heavy or fragmented.
- AI explanations can be confidently wrong, especially in edge cases.

## Pricing and Paywall Observations

- Wolfram Alpha offers free queries with paid Pro features for richer input,
  steps, and extended computation workflows.
- Symbolab provides free solving with ads and limits, with paid subscriptions
  for deeper steps and premium features.
- Photomath publicly shows paid monthly premium options for deeper
  explanations and visual aids.
- Mathway commonly provides answers freely while detailed steps and broader
  help are tied to paid access.
- Desmos is a strong free competitor for graphing and visual exploration.
- Microsoft Math Solver and browser-integrated math help create free baseline
  expectations.

Users are sensitive to paying just to see steps after entering a problem. A
formula-reference workflow should make clear what is reference, what is
calculation, and what is premium if monetized later.

## AI Capability Trends

- Math tools are moving from calculators toward AI tutoring.
- Camera input and multimodal math recognition are becoming common.
- Step-by-step explanations are being paired with "why" explanations and visual
  aids.
- Natural-language formula search is becoming more realistic.
- AI can translate a word problem into candidate formulas, but verification is
  essential.
- Graphing, simulations, and interactive sliders remain strong non-AI learning
  patterns.

AI should help users identify candidate formulas and explain assumptions, not
silently produce a single answer with no context.

## UX Patterns Worth Studying

- Search-first formula discovery.
- Topic browsing by subject and level.
- Formula cards with clear variable definitions and units.
- Related formula links and alternate forms.
- Worked example below the reference formula.
- Save/favorite for exam preparation.
- Simple calculator attached to a formula without hiding the formula itself.
- Clear mode separation between "find formula" and "solve problem."
- Mobile-friendly math notation display.
- Warnings for assumptions, domains, and unit constraints.

## Opportunities for Ansiversa

- Position Formula Finder as a trusted reference and learning companion rather
  than a homework solver.
- Connect naturally with Concept Explainer, Smart Textbook Scanner, Quiz, Study
  Planner, Course Tracker, and Memory Trainer through approved platform
  boundaries.
- Let users save formulas by course, topic, exam, or project.
- Use AI later to suggest candidate formulas from a problem statement, with
  visible assumptions and user review.
- Emphasize variables, units, applicability, and examples.
- Keep formulas as structured records instead of scattered search results.
- Support review workflows so formulas can become memory practice.

## What Ansiversa Should Avoid

- Do not copy formula libraries, wording, examples, solution layouts, or
  proprietary solver flows.
- Do not present generated formulas as authoritative without source review.
- Do not become a broad symbolic math solver unless explicitly approved.
- Do not encourage answer-only homework bypass.
- Do not hide assumptions, unit constraints, or applicability limits.
- Do not place core learning value behind surprise paywalls.
- Do not overcomplicate math input before the reference workflow is strong.
- Do not add global abstractions or shared components from this research alone.

## Product Questions for Future Review

- Which subjects should Formula Finder cover first: math, physics, finance,
  statistics, chemistry, or mixed?
- What formula data source is acceptable and maintainable?
- Should formulas be curated by Ansiversa, user-created, or both?
- Should the app include calculators attached to formulas in V1?
- How should AI candidate-formula suggestions be verified?
- Should saved formulas sync with Memory Trainer or Quiz?
- What notation renderer and accessibility standard should be used?
- How should the app distinguish formula reference from problem solving?

## Sources

- Wolfram Alpha: https://www.wolframalpha.com/
- Wolfram Alpha equation solver: https://www.wolframalpha.com/calculators/equation-solver-calculator
- Symbolab: https://www.symbolab.com/
- Symbolab Google Play listing: https://play.google.com/store/apps/details?id=com.devsense.symbolab
- Mathway: https://www.mathway.com/
- Mathway App Store listing: https://apps.apple.com/us/app/mathway-math-problem-solver/id467329677
- Microsoft Math Solver announcement: https://news.microsoft.com/en-in/microsoft-math-solver-ai-app/
- Microsoft Edge Math Solver: https://www.microsoft.com/en-us/edge/learning-center/math-solver
- Photomath: https://photomath.com/en
- Photomath App Store listing: https://apps.apple.com/us/app/photomath/id919087726
- Desmos: https://www.desmos.com/
- Desmos Graphing Calculator help: https://help.desmos.com/hc/en-us/articles/4406040715149-Getting-Started-Desmos-Graphing-Calculator
- Desmos Google Play listing: https://play.google.com/store/apps/details?id=com.desmos.calculator

## Review Notes

- Research was limited to public product pages, app listings, help pages,
  pricing pages, and public user-signal sources.
- Formula content sourcing, notation support, and math accuracy require separate
  review before product decisions.
- Pricing, solver availability, and AI math capabilities change frequently.
- This document is market intelligence only. It does not approve new features,
  metadata changes, implementation work, or live promotion.

## Revision History

| Date | Summary |
|------|---------|
| 2026-07-05 | Initial market study created. |
