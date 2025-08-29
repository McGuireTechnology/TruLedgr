# Items Module - Entity Relationship Diagram

## Overview

This diagram shows the database schema for the **items** module, including related tables from other modules that have foreign key relationships.

### Core Tables (items module)
- `item`

### Related Tables (from other modules)
No related tables from other modules.

### Total Tables in Diagram
1 tables

## Entity Relationship Diagram

```mermaid
# Items Module ERD\n\nerDiagram\n    ITEM {\n        int id PK "Id"\n        string name "Name"\n        string description "Description"\n        boolean is_active "Is Active"\n    }\n
```

## Table Descriptions

### `item`\n\n| Column | Type | Constraints | Description |\n|--------|------|-------------|-------------|\n| `id` | `INTEGER` | PK, NOT NULL | Id |\n| `name` | `VARCHAR` | NOT NULL | Name |\n| `description` | `VARCHAR` |  | Description |\n| `is_active` | `BOOLEAN` | NOT NULL | Is Active |\n\n## Relationships\n\nNo foreign key relationships found in this module.\n