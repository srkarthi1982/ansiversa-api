# Concept Explainer Destination

## App Name

Concept Explainer

## Destination Status

Approved v1.0

## Final Product Vision

Concept Explainer should mature into a focused learning workspace that helps
users turn difficult ideas into structured explanations, ordered steps,
self-check questions, and reviewed understanding.

The product should help users build comprehension without becoming a full
tutoring platform, curriculum system, quiz engine, answer generator, or
authority on what the user truly understands.

At its destination, Concept Explainer should give learners a calm place to
break down concepts, test themselves, revisit explanations, and hand reviewed
learning material to adjacent study tools.

## Target Users

- Students breaking down difficult course concepts.
- Self-learners studying unfamiliar topics.
- Professionals learning work-related terminology, systems, or methods.
- Teachers and tutors preparing simple explanations.
- Users who want concept-level understanding before memorization or testing.
- Parents or mentors helping learners understand homework without turning the tool into an answer shortcut.
- Non-native English speakers who need difficult topics explained in simpler language.

## Core User Problems

- Difficult concepts often stay vague because users do not break them into
  smaller steps.
- Learners may collect definitions without checking whether they can explain
  the idea.
- Notes can become passive instead of reviewable.
- Users need self-checks that support understanding without becoming a formal
  assessment engine.
- AI explanations can mislead if they are accepted without user review.
- Learners often need hints, examples, and prerequisite reminders before seeing a full explanation.
- Users need ways to verify understanding so explanations do not become passive notes.

## Final Capabilities

- Create owner-scoped concept records with title, topic, and description.
- Add ordered explanation steps.
- Add ordered self-check questions with expected answers.
- Edit and delete concepts, steps, and checks.
- Mark concepts reviewed when the user has studied the explanation.
- Load concept lists as summaries with counts and details only when opened.
- Support simple concept collections or topic groupings.
- Preserve explanation order so concepts can be revisited consistently.
- Hand reviewed concepts to Memory Trainer, Quiz, or Study Planner.
- Keep the user responsible for accepting and reviewing explanations.

## Advanced Capabilities

- AI explanation drafts with user review before saving.
- Multiple explanation styles such as beginner, analogy, technical, or visual.
- Hint-first flows that help the learner try before revealing a complete explanation.
- Adaptive self-check suggestions based on explanation steps.
- Short "prove I understand" loops using restatement, examples, and checks.
- Spaced review scheduling through Memory Trainer or Study Planner.
- Topic collections for related concepts.
- Concept maps showing relationships between saved concepts.
- Export to study sheets or lesson material.
- Confidence indicators based on user review history, not hidden scoring.

## AI Opportunities

AI may help draft explanations and self-checks, but it must not become an
unquestioned answer authority.

Potential AI support includes:

- Suggesting plain-language explanations from user-provided context.
- Breaking a concept into ordered steps.
- Generating self-check questions from approved steps.
- Offering analogies with caveats and user review.
- Highlighting vague steps that need clarification.
- Suggesting related concepts for optional exploration.

AI must not mark a concept understood, guarantee correctness, replace user
review, provide high-stakes academic or professional advice as authority, or
hide uncertainty.

## Ecosystem Connections

- Study Planner can schedule concept review tasks.
- Course Tracker can link concepts to course modules.
- Smart Textbook Scanner can hand off extracted concepts.
- AI Notes Summarizer can send summarized concepts for explanation.
- Memory Trainer can receive reviewed facts or steps for recall practice.
- Quiz can receive user-approved checks as quiz material.
- Lesson Builder can reuse reviewed explanations for teaching plans.

Concept Explainer owns explanation and self-check structure. It should not
absorb course tracking, study scheduling, flashcard practice, quiz delivery, or
lesson publishing.

## Weekly Return Value

Users return when they encounter new difficult ideas, refine explanations,
review saved concepts, add self-checks, and prepare related study or practice
workflows.

The weekly value is deeper understanding: making complex ideas easier to
revisit and explain.

## Success Criteria

- Users can create concepts, steps, checks, and review status in one focused
  workflow.
- Explanations remain ordered, editable, and connected to self-checks.
- Review status supports reflection without claiming mastery.
- Self-checks help users verify understanding without encouraging answer-copying.
- Any AI assistance remains draft-based, transparent, and user-approved.
- Ecosystem handoffs send reviewed concept material without taking over
  adjacent app responsibilities.
- The app remains useful for manual learning and not dependent on AI.

## Journey Progress

Current Position: 63 / 100
Destination: 100 / 100
Remaining Journey: 37 / 100

This estimate describes product maturity, not feature completion.

Concept Explainer already has a live concept, step, check, and review workflow.
The remaining journey is about AI-assisted explanation drafts, adaptive checks,
spaced review handoffs, topic collections, and richer learning connections.

## Future Version Ideas

- V1.1: Add topic collections and concept grouping.
- V1.2: Add Study Planner and Memory Trainer handoffs.
- V1.3: Add export to lesson or study-sheet formats.
- V1.4: Add AI explanation drafts with review controls.
- V2: Add concept maps and adaptive self-check generation.

## Non Goals

- Do not become a full tutoring platform.
- Do not become an LMS or curriculum manager.
- Do not become a quiz engine.
- Do not become a homework answer machine.
- Do not market the tool as a way to bypass homework or assignments.
- Do not guarantee mastery or understanding.
- Do not replace Study Planner, Course Tracker, Memory Trainer, Quiz, or Lesson
  Builder.
- Do not treat AI explanations as authoritative without review.
- Do not deliver high-stakes medical, legal, financial, or safety instruction
  as truth.

## Guiding Principles

- Improve understanding by breaking concepts into steps.
- Treat self-checks as learning aids, not formal assessment.
- Keep user review central to every explanation.
- Prefer guided learning, hints, and verification before direct answers.
- Preserve manual usefulness before adding AI complexity.
- Make AI drafts explainable, editable, and optional.
- Support adjacent learning apps through explicit handoffs.
- Favor comprehension over performance claims.

## Governance Notes

This document is aspirational and does not authorize immediate implementation.
Future work must be reviewed by Product Owner and Astra before development.

Any feature involving AI explanation generation, adaptive checks, concept maps,
spaced review automation, quiz generation, or high-stakes instructional content
requires explicit governance review before implementation.

## Last Governance Review

Product Owner: Approved on 2026-07-03 for live-app Destination Framework rollout.
Astra: Approved on 2026-07-03. Journey Progress 63 / 100 accepted.
Codex: Drafted destination v1.0 from current backend story, frontend story, and overview metadata.

Status: Approved
