# -*- coding: utf-8 -*-
from db.connection import connect

# الحقول المشتركة في جدول assets
BASE_FIELDS = [
    "asset_tag","device_type","hostname","ip_address","model_vendor","sn","location",
    "owner","department","site","building","floor","room",
    "status","firmware_os_version","notes","data_source",
    "created_at","created_by","updated_at","updated_by",
]

# إنشاء الجداول والفهارس
DDL = [
    """
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_tag TEXT DEFAULT NULL,
        device_type TEXT NOT NULL,
        hostname TEXT NOT NULL,
        ip_address TEXT NOT NULL,
        model_vendor TEXT,
        sn TEXT,
        location TEXT,
        owner TEXT,
        department TEXT,
        site TEXT,
        building TEXT,
        floor TEXT,
        room TEXT,
        status TEXT DEFAULT 'Active',
        firmware_os_version TEXT,
        notes TEXT,
        data_source TEXT DEFAULT 'Unknown',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        created_by TEXT,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_by TEXT,
        
        -- Excel-DB sync metadata
        _excel_path TEXT,
        _sheet_name TEXT,
        _headers TEXT,
        _sync_pending TEXT DEFAULT '0',
        _sync_attempts INTEGER DEFAULT 0,
        _sync_completed_at TEXT,
        _sync_failed TEXT DEFAULT '0',
        
        -- Enhanced data integrity and duplicate prevention
        _device_fingerprint TEXT,
        _collection_quality TEXT DEFAULT 'Standard',
        _validation_errors TEXT,
        _data_version INTEGER DEFAULT 1,
        _last_validation DATETIME DEFAULT CURRENT_TIMESTAMP,
        
        -- Enhanced constraints
        UNIQUE(hostname, ip_address) ON CONFLICT REPLACE,
        CHECK (ip_address GLOB '[0-9]*.[0-9]*.[0-9]*.[0-9]*'),
        CHECK (length(hostname) > 0 AND length(hostname) <= 253),
        CHECK (asset_tag IS NULL OR length(asset_tag) >= 1),
        CHECK (_sync_pending IN ('0', '1')),
        CHECK (_data_version >= 1),
        CHECK (status IN ('Active', 'Inactive', 'Maintenance', 'Retired'))
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_assets_status ON assets(status);",
    "CREATE INDEX IF NOT EXISTS idx_assets_department ON assets(department);",
    "CREATE INDEX IF NOT EXISTS idx_assets_hostname ON assets(hostname);",
    "CREATE INDEX IF NOT EXISTS idx_assets_ip_address ON assets(ip_address);",
    "CREATE INDEX IF NOT EXISTS idx_assets_asset_tag ON assets(asset_tag) WHERE asset_tag IS NOT NULL;",
    "CREATE INDEX IF NOT EXISTS idx_assets_fingerprint ON assets(_device_fingerprint);",
    "CREATE INDEX IF NOT EXISTS idx_assets_sync_pending ON assets(_sync_pending) WHERE _sync_pending = '1';",
    "CREATE INDEX IF NOT EXISTS idx_assets_updated_at ON assets(updated_at);",
    
    # Additional tables for enhanced error prevention
    """
    CREATE TABLE IF NOT EXISTS duplicate_resolutions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_device_id INTEGER,
        duplicate_device_id INTEGER,
        resolution_strategy TEXT NOT NULL,
        resolved_at TEXT DEFAULT CURRENT_TIMESTAMP,
        resolution_details TEXT,
        FOREIGN KEY (original_device_id) REFERENCES assets(id) ON DELETE CASCADE,
        FOREIGN KEY (duplicate_device_id) REFERENCES assets(id) ON DELETE CASCADE
    );
    """,
    
    """
    CREATE TABLE IF NOT EXISTS validation_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id INTEGER,
        field_name TEXT NOT NULL,
        original_value TEXT,
        sanitized_value TEXT,
        validation_error TEXT,
        fixed_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (device_id) REFERENCES assets(id) ON DELETE CASCADE
    );
    """,
    
    """
    CREATE TABLE IF NOT EXISTS sync_errors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id INTEGER,
        error_type TEXT NOT NULL,
        error_message TEXT,
        excel_path TEXT,
        sheet_name TEXT,
        occurred_at TEXT DEFAULT CURRENT_TIMESTAMP,
        resolved INTEGER DEFAULT 0,
        FOREIGN KEY (device_id) REFERENCES assets(id) ON DELETE CASCADE
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_assets_site ON assets(site);",
    "CREATE INDEX IF NOT EXISTS idx_assets_sync_pending ON assets(_sync_pending);",

    """
    CREATE TABLE IF NOT EXISTS hypervisors (
        asset_id INTEGER PRIMARY KEY,
        cluster TEXT, vcenter TEXT,
        cpu_sockets INTEGER, cpu_cores INTEGER, cpu_threads INTEGER,
        total_ram TEXT, total_cpu TEXT, storage TEXT, vm_count INTEGER,
        mgmt_ip TEXT, vmotion_ip TEXT, datastores_info TEXT,
        FOREIGN KEY(asset_id) REFERENCES assets(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS switches (
        asset_id INTEGER PRIMARY KEY,
        firmware_version TEXT, ports_total INTEGER, poe TEXT,
        mgmt_vlan TEXT, uplink_to TEXT, mgmt_mac TEXT,
        FOREIGN KEY(asset_id) REFERENCES assets(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS printers (
        asset_id INTEGER PRIMARY KEY,
        firmware_version TEXT, page_total INTEGER, page_mono INTEGER, page_color INTEGER,
        supplies_status TEXT,
        FOREIGN KEY(asset_id) REFERENCES assets(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS access_points (
        asset_id INTEGER PRIMARY KEY,
        controller TEXT, adopted_by TEXT, ssids TEXT, bands TEXT,
        channel TEXT, tx_power TEXT, poe_port TEXT,
        FOREIGN KEY(asset_id) REFERENCES assets(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS fingerprints (
        asset_id INTEGER PRIMARY KEY,
        controller_ip TEXT, door_area TEXT, user_capacity INTEGER, log_capacity INTEGER,
        firmware_version TEXT,
        FOREIGN KEY(asset_id) REFERENCES assets(id) ON DELETE CASCADE
    );
    """,
]

def bootstrap_schema() -> None:
    """تشغيل DDL مرة واحدة (Idempotent)."""
    from db.connection import init_db
    init_db()
    with connect() as c:
        # Run migrations first
        _migrate_database(c)
        
        # Then run DDL
        for stmt in DDL:
            c.execute(stmt)

def _migrate_database(conn) -> None:
    """Apply database migrations for existing installations"""
    try:
        cursor = conn.cursor()
        
        # Check if sync columns exist
        cursor.execute("PRAGMA table_info(assets)")
        columns = [col[1] for col in cursor.fetchall()]
        
        sync_columns = [
            '_excel_path', '_sheet_name', '_headers', 
            '_sync_pending', '_sync_attempts', '_sync_completed_at', '_sync_failed'
        ]
        
        # Enhanced columns for duplicate prevention and quality tracking
        enhanced_columns = [
            '_device_fingerprint', '_collection_quality', '_duplicate_resolved_at',
            '_validation_status', '_error_count', '_last_collection_attempt'
        ]
        
        # Add missing sync columns
        for col in sync_columns:
            if col not in columns:
                if col == '_sync_pending':
                    cursor.execute(f"ALTER TABLE assets ADD COLUMN {col} TEXT DEFAULT '0'")
                elif col == '_sync_attempts':
                    cursor.execute(f"ALTER TABLE assets ADD COLUMN {col} INTEGER DEFAULT 0")
                elif col == '_sync_failed':
                    cursor.execute(f"ALTER TABLE assets ADD COLUMN {col} TEXT DEFAULT '0'")
                else:
                    cursor.execute(f"ALTER TABLE assets ADD COLUMN {col} TEXT")
        
        # Add missing enhanced columns
        for col in enhanced_columns:
            if col not in columns:
                if col == '_collection_quality':
                    cursor.execute(f"ALTER TABLE assets ADD COLUMN {col} TEXT DEFAULT 'Standard'")
                elif col == '_error_count':
                    cursor.execute(f"ALTER TABLE assets ADD COLUMN {col} INTEGER DEFAULT 0")
                else:
                    cursor.execute(f"ALTER TABLE assets ADD COLUMN {col} TEXT")
                    
        conn.commit()
        
    except Exception as e:
        # Migration failed, but continue - new installs will work
        import logging
        logging.warning(f"Database migration failed (non-fatal): {e}")
