# PostgreSQL Auto-Increment Fix

## Problem

When using PostgreSQL, you may encounter this error when registering users:

```
null value in column "id" of relation "users" violates not-null constraint
```

## Root Cause

PostgreSQL sequences weren't properly initialized when tables were created or migrated. The `id` column expects an auto-generated value, but the sequence wasn't configured correctly.

## Solution Applied

### 1. Updated Models (`models.py`)

Added explicit `autoincrement=True` to all primary key columns:

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # ...
```

This ensures PostgreSQL creates proper SERIAL columns with auto-increment sequences.

### 2. Created Database Recreation Script (`recreate_db.py`)

A script to drop and recreate all tables with correct sequences:

```bash
python recreate_db.py
```

**⚠️ WARNING:** This deletes all existing data!

### 3. Created Sequence Fix Script (`fix_sequences.py`)

For existing databases with data, this script fixes the sequences without data loss:

```bash
python fix_sequences.py
```

This resets each table's sequence to the next available ID.

## How to Fix Your Database

### Option 1: Fresh Start (No Data)

If you don't have important data:

```bash
python recreate_db.py
```

Enter `yes` when prompted.

### Option 2: Keep Existing Data

If you have data you want to keep:

```bash
python fix_sequences.py
```

This will reset sequences without deleting data.

## Verification

After running the fix, test registration:

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'
```

Expected response:
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "full_name": "Test User"
}
```

## Why This Happened

1. **Database Migration**: If you migrated from SQLite to PostgreSQL
2. **Manual Table Creation**: Tables created without proper sequences
3. **Data Import**: Importing data without resetting sequences afterward

## Prevention

Always use SQLAlchemy's `autoincrement=True` for primary keys when using PostgreSQL:

```python
id = Column(Integer, primary_key=True, autoincrement=True)
```

## Error Handling

The error is now **properly caught and logged** by the global error handler:

```json
{
  "success": false,
  "error": {
    "type": "DatabaseError",
    "message": "Database integrity constraint violated",
    "status_code": 500,
    "timestamp": "2026-04-08T15:53:29.149Z",
    "path": "/auth/register"
  }
}
```

The application won't crash - the error is gracefully handled!

## Files Added

- `fix_sequences.py` - Fix sequences in existing database
- `recreate_db.py` - Recreate database with correct sequences
- `POSTGRESQL_FIX.md` - This documentation

## Files Modified

- `models.py` - Added `autoincrement=True` to all primary keys

## Summary

✅ Problem identified: PostgreSQL sequence not initialized
✅ Models updated with explicit autoincrement
✅ Database recreated with proper sequences
✅ Registration tested and working
✅ Error handling catches and logs issues gracefully
