MODULE_NAME = "Digital Document Vault"
MODULE_SLUG = "digital-document-vault"
TIMING_LABEL = "digital_document_vault"
VERSION_TABLE = "digital_document_vault_alembic_version"
MANAGED_TABLES = {"Categories", "Documents"}

ALLOWED_FILE_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
