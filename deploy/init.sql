CREATE DATABASE IF NOT EXISTS mydb DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS documents (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    source      VARCHAR(512) NOT NULL,
    file_hash   VARCHAR(64) NOT NULL,
    chunk_count INT NOT NULL DEFAULT 0,
    collection  VARCHAR(64) NOT NULL DEFAULT 'kb1',
    status      VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_source_collection (source, collection),
    INDEX idx_status (status),
    INDEX idx_collection (collection)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;