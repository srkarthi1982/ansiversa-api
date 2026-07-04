MODULE_SLUG = "task-prioritizer"
MODULE_NAME = "Task Prioritizer"
TIMING_LABEL = "task_prioritizer"
VERSION_TABLE = "task_prioritizer_alembic_version"

MANAGED_TABLES = {
    "TaskPrioritizerTasks",
    "TaskPrioritizerTaskPriorities",
    "TaskPrioritizerPriorityRules",
    "TaskPrioritizerPriorityHistory",
}
