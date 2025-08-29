#!/usr/bin/env python3
"""
ERD Generator for TruLedgr

This script generates Entity Relationship Diagrams from SQLModel definitions.
It can output in various formats including:
- Mermaid ERD syntax
- PlantUML format
- Graphviz DOT format
- SQL DDL with relationships

Usage:
    python scripts/generate_erd.py --format mermaid --output docs/erd.md
    python scripts/generate_erd.py --format plantuml --output docs/erd.puml
    python scripts/generate_erd.py --format graphviz --output docs/erd.dot
"""

import argparse
import inspect
import sys
from pathlib import Path
from typing import Dict, List, Any, Set, Optional
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import SQLModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.inspection import inspect as sqlalchemy_inspect
from api.db.base import import_all_models


class ERDGenerator:
    """Generate ERD diagrams from SQLModel definitions."""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.relationships: List[Dict[str, Any]] = []
        self.tables: Dict[str, Dict[str, Any]] = {}
        self.module_mapping: Dict[str, str] = {}
        
    def get_table_module(self, table_name: str) -> str:
        """Determine which module a table belongs to based on naming conventions."""
        # Define module mappings based on table names
        module_mappings = {
            'users': 'users',
            'user_sessions': 'users',
            'session_activities': 'users',
            'sessionanalytics': 'users',
            'oauth_accounts': 'authentication',
            'oauth2account': 'authentication',
            'password_reset_tokens': 'authentication',
            'passwordresettoken': 'authentication',
            'roles': 'authorization',
            'permissions': 'authorization',
            'role_permissions': 'authorization',
            'user_roles': 'authorization',
            'groups': 'groups',
            'user_groups': 'groups',
            'activities': 'activities',
            'institutions': 'institutions',
            'accounts': 'accounts',
            'transactions': 'transactions',
            'items': 'items',
            'item': 'items',
            # Plaid-related tables
            'plaid_': 'plaid',
        }
        
        # Check exact matches first
        if table_name in module_mappings:
            return module_mappings[table_name]
        
        # Check prefix matches
        for prefix, module in module_mappings.items():
            if table_name.startswith(prefix):
                return module
        
        # Default to 'common' for unmatched tables
        return 'common'
    
    def get_related_tables(self, module_tables: Set[str]) -> Set[str]:
        """Get all tables that have relationships with the given module tables."""
        related_tables = set(module_tables)
        
        # Find tables that reference module tables (foreign key relationships)
        for table_name, table_info in self.tables.items():
            if table_name in module_tables:
                continue
                
            has_relationship = False
            
            # Check if this table has foreign keys to module tables
            for fk in table_info['foreign_keys']:
                if fk['references_table'] in module_tables:
                    has_relationship = True
                    break
            
            # Check if module tables have foreign keys to this table
            if not has_relationship:
                for mod_table in module_tables:
                    if mod_table in self.tables:
                        for fk in self.tables[mod_table]['foreign_keys']:
                            if fk['references_table'] == table_name:
                                has_relationship = True
                                break
                    if has_relationship:
                        break
            
            if has_relationship:
                related_tables.add(table_name)
        
        return related_tables
        
    def discover_models(self):
        """Discover all SQLModel models in the application."""
        # Import all models to register them
        import_all_models()
        
        # Get all registered tables from SQLModel metadata
        for table in SQLModel.metadata.tables.values():
            self.tables[table.name] = {
                'name': table.name,
                'columns': [],
                'primary_keys': [],
                'foreign_keys': [],
                'indexes': [],
                'constraints': []
            }
            
            # Process columns
            for column in table.columns:
                col_info = {
                    'name': column.name,
                    'type': str(column.type),
                    'nullable': column.nullable,
                    'primary_key': column.primary_key,
                    'foreign_key': None,
                    'unique': column.unique if hasattr(column, 'unique') else False,
                    'default': str(column.default) if column.default else None
                }
                
                # Check for foreign keys
                if column.foreign_keys:
                    fk = list(column.foreign_keys)[0]
                    col_info['foreign_key'] = {
                        'table': fk.column.table.name,
                        'column': fk.column.name
                    }
                    self.tables[table.name]['foreign_keys'].append({
                        'column': column.name,
                        'references_table': fk.column.table.name,
                        'references_column': fk.column.name
                    })
                
                if column.primary_key:
                    self.tables[table.name]['primary_keys'].append(column.name)
                
                self.tables[table.name]['columns'].append(col_info)
            
            # Process indexes
            for index in table.indexes:
                self.tables[table.name]['indexes'].append({
                    'name': index.name,
                    'columns': [col.name for col in index.columns],
                    'unique': index.unique
                })
    
    def generate_mermaid_erd(self, tables_to_include: Optional[Set[str]] = None, module_name: Optional[str] = None) -> str:
        """Generate Mermaid ERD syntax for specific tables or all tables."""
        if tables_to_include is None:
            tables_to_include = set(self.tables.keys())
        
        output = ["erDiagram"]
        
        if module_name:
            output.insert(0, f"# {module_name.title()} Module ERD")
            output.insert(1, "")
        
        # Generate table definitions
        for table_name, table_info in self.tables.items():
            if table_name == 'alembic_version' or table_name not in tables_to_include:
                continue
                
            output.append(f"    {table_name.upper()} {{")
            
            for col in table_info['columns']:
                # Determine column attributes
                attrs = []
                if col['primary_key']:
                    attrs.append("PK")
                if col['foreign_key']:
                    attrs.append("FK")
                if col['unique'] and not col['primary_key']:
                    attrs.append("UK")
                
                attr_str = " ".join(attrs)
                if attr_str:
                    attr_str = f" {attr_str}"
                
                # Format type
                col_type = col['type'].replace('VARCHAR', 'string').replace('TEXT', 'string')
                col_type = col_type.replace('INTEGER', 'int').replace('BOOLEAN', 'boolean')
                col_type = col_type.replace('DATETIME', 'datetime').replace('NUMERIC', 'decimal')
                
                description = f'"{col["name"].replace("_", " ").title()}"'
                
                output.append(f'        {col_type} {col["name"]}{attr_str} {description}')
            
            output.append("    }")
            output.append("")
        
        # Generate relationships (only for included tables)
        relationships_added = set()
        for table_name in tables_to_include:
            if table_name == 'alembic_version' or table_name not in self.tables:
                continue
                
            table_info = self.tables[table_name]
            for fk in table_info['foreign_keys']:
                ref_table = fk['references_table']
                if ref_table == 'alembic_version' or ref_table not in tables_to_include:
                    continue
                    
                # Determine relationship type
                relationship_key = f"{ref_table}-{table_name}"
                reverse_key = f"{table_name}-{ref_table}"
                
                if relationship_key not in relationships_added and reverse_key not in relationships_added:
                    # Check if it's a many-to-many junction table
                    if len(table_info['foreign_keys']) >= 2 and len(table_info['columns']) <= 4:
                        # Junction table - create many-to-many
                        fks = table_info['foreign_keys']
                        if len(fks) >= 2:
                            table1 = fks[0]['references_table']
                            table2 = fks[1]['references_table']
                            if table1 in tables_to_include and table2 in tables_to_include:
                                output.append(f"    {table1.upper()} ||--o{{ {table2.upper()} : \"{table_name}\"")
                    else:
                        # Regular one-to-many relationship
                        rel_name = fk['column'].replace('_id', '').replace('_', ' ')
                        output.append(f"    {ref_table.upper()} ||--o{{ {table_name.upper()} : \"{rel_name}\"")
                    
                    relationships_added.add(relationship_key)
        
        return "\\n".join(output)
    
    def generate_plantuml_erd(self) -> str:
        """Generate PlantUML ERD syntax."""
        output = ["@startuml", "!define ENTITY class", ""]
        
        # Generate entities
        for table_name, table_info in self.tables.items():
            if table_name == 'alembic_version':
                continue
                
            output.append(f"ENTITY {table_name} {{")
            
            for col in table_info['columns']:
                col_type = col['type']
                markers = []
                
                if col['primary_key']:
                    markers.append("PK")
                if col['foreign_key']:
                    markers.append("FK")
                if not col['nullable']:
                    markers.append("NOT NULL")
                
                marker_str = f" {{{', '.join(markers)}}}" if markers else ""
                output.append(f"  {col['name']} : {col_type}{marker_str}")
            
            output.append("}")
            output.append("")
        
        # Generate relationships
        for table_name, table_info in self.tables.items():
            if table_name == 'alembic_version':
                continue
                
            for fk in table_info['foreign_keys']:
                ref_table = fk['references_table']
                if ref_table != 'alembic_version':
                    output.append(f"{ref_table} ||--o{{ {table_name}")
        
        output.append("@enduml")
        return "\\n".join(output)
    
    def generate_graphviz_dot(self) -> str:
        """Generate Graphviz DOT format."""
        output = [
            "digraph ERD {",
            "  rankdir=TB;",
            "  node [shape=record, style=filled, fillcolor=lightblue];",
            ""
        ]
        
        # Generate table nodes
        for table_name, table_info in self.tables.items():
            if table_name == 'alembic_version':
                continue
                
            columns = []
            for col in table_info['columns']:
                col_str = col['name']
                if col['primary_key']:
                    col_str = f"<PK>{col_str}"
                elif col['foreign_key']:
                    col_str = f"<FK>{col_str}"
                
                col_str += f" : {col['type']}"
                columns.append(col_str)
            
            columns_str = "|".join(columns)
            output.append(f'  {table_name} [label="{{<table>{table_name}|{columns_str}}}"];')
        
        output.append("")
        
        # Generate relationships
        for table_name, table_info in self.tables.items():
            if table_name == 'alembic_version':
                continue
                
            for fk in table_info['foreign_keys']:
                ref_table = fk['references_table']
                if ref_table != 'alembic_version':
                    output.append(f"  {ref_table} -> {table_name};")
        
        output.append("}")
        return "\\n".join(output)
    
    def generate_sql_ddl(self) -> str:
        """Generate SQL DDL with documentation."""
        output = [
            "-- TruLedgr Database Schema",
            f"-- Generated on {datetime.now().isoformat()}",
            "-- This file contains the complete database schema with relationships",
            ""
        ]
        
        # Generate CREATE TABLE statements
        for table_name, table_info in self.tables.items():
            if table_name == 'alembic_version':
                continue
                
            output.append(f"-- Table: {table_name}")
            output.append(f"CREATE TABLE {table_name} (")
            
            column_defs = []
            for col in table_info['columns']:
                col_def = f"  {col['name']} {col['type']}"
                
                if not col['nullable']:
                    col_def += " NOT NULL"
                
                if col['default']:
                    col_def += f" DEFAULT {col['default']}"
                
                column_defs.append(col_def)
            
            # Add primary key constraint
            if table_info['primary_keys']:
                pk_cols = ", ".join(table_info['primary_keys'])
                column_defs.append(f"  PRIMARY KEY ({pk_cols})")
            
            # Add foreign key constraints
            for fk in table_info['foreign_keys']:
                fk_def = f"  FOREIGN KEY ({fk['column']}) REFERENCES {fk['references_table']}({fk['references_column']})"
                column_defs.append(fk_def)
            
            output.append(",\\n".join(column_defs))
            output.append(");")
            output.append("")
            
            # Add indexes
            for index in table_info['indexes']:
                unique_str = "UNIQUE " if index['unique'] else ""
                cols = ", ".join(index['columns'])
                output.append(f"CREATE {unique_str}INDEX {index['name']} ON {table_name}({cols});")
            
            output.append("")
        
        return "\\n".join(output)
    
    def get_modules(self) -> Dict[str, Set[str]]:
        """Get all modules and their associated tables."""
        modules = {}
        
        for table_name in self.tables.keys():
            if table_name == 'alembic_version':
                continue
                
            module = self.get_table_module(table_name)
            if module not in modules:
                modules[module] = set()
            modules[module].add(table_name)
        
        return modules
    
    def generate_module_erd(self, module_name: str) -> str:
        """Generate ERD for a specific module including related tables."""
        modules = self.get_modules()
        
        if module_name not in modules:
            raise ValueError(f"Module '{module_name}' not found. Available modules: {list(modules.keys())}")
        
        # Get core tables for this module
        module_tables = modules[module_name]
        
        # Get related tables from other modules
        all_related_tables = self.get_related_tables(module_tables)
        
        return self.generate_mermaid_erd(all_related_tables, module_name)
    
    def generate_all_module_erds(self, output_dir: Path):
        """Generate ERD files for all modules."""
        modules = self.get_modules()
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        
        for module_name in modules.keys():
            if module_name == 'common':
                continue  # Skip common module for now
                
            try:
                erd_content = self.generate_module_erd(module_name)
                
                # Create comprehensive module documentation
                module_tables = modules[module_name]
                all_tables = self.get_related_tables(module_tables)
                related_tables = all_tables - module_tables
                
                # Build complete markdown file
                markdown_content = f"""# {module_name.title()} Module - Entity Relationship Diagram

## Overview

This diagram shows the database schema for the **{module_name}** module, including related tables from other modules that have foreign key relationships.

### Core Tables ({module_name} module)
{chr(10).join(f"- `{table}`" for table in sorted(module_tables))}

### Related Tables (from other modules)
{chr(10).join(f"- `{table}` (from {self.get_table_module(table)} module)" for table in sorted(related_tables)) if related_tables else "No related tables from other modules."}

### Total Tables in Diagram
{len(all_tables)} tables

## Entity Relationship Diagram

```mermaid
{erd_content}
```

## Table Descriptions

"""
                
                # Add table descriptions
                for table_name in sorted(all_tables):
                    if table_name == 'alembic_version':
                        continue
                        
                    table_info = self.tables[table_name]
                    table_module = self.get_table_module(table_name)
                    module_indicator = f" ({table_module} module)" if table_module != module_name else ""
                    
                    markdown_content += f"### `{table_name}`{module_indicator}\\n\\n"
                    
                    # Add column information
                    markdown_content += "| Column | Type | Constraints | Description |\\n"
                    markdown_content += "|--------|------|-------------|-------------|\\n"
                    
                    for col in table_info['columns']:
                        constraints = []
                        if col['primary_key']:
                            constraints.append("PK")
                        if col['foreign_key']:
                            fk = col['foreign_key']
                            constraints.append(f"FK → {fk['table']}.{fk['column']}")
                        if col['unique'] and not col['primary_key']:
                            constraints.append("UNIQUE")
                        if not col['nullable']:
                            constraints.append("NOT NULL")
                        
                        constraint_str = ", ".join(constraints) if constraints else ""
                        desc = col['name'].replace('_', ' ').title()
                        
                        markdown_content += f"| `{col['name']}` | `{col['type']}` | {constraint_str} | {desc} |\\n"
                    
                    markdown_content += "\\n"
                
                # Add relationships section
                markdown_content += "## Relationships\\n\\n"
                
                relationships_found = False
                for table_name in sorted(all_tables):
                    if table_name == 'alembic_version' or table_name not in self.tables:
                        continue
                        
                    table_info = self.tables[table_name]
                    if table_info['foreign_keys']:
                        relationships_found = True
                        for fk in table_info['foreign_keys']:
                            if fk['references_table'] in all_tables:
                                markdown_content += f"- `{table_name}.{fk['column']}` → `{fk['references_table']}.{fk['references_column']}`\\n"
                
                if not relationships_found:
                    markdown_content += "No foreign key relationships found in this module.\\n"
                
                # Write to file
                output_file = output_dir / f"{module_name}-erd.md"
                with open(output_file, 'w') as f:
                    f.write(markdown_content)
                
                generated_files.append(output_file)
                print(f"✅ Generated {module_name} module ERD: {output_file}")
                
            except Exception as e:
                print(f"❌ Failed to generate ERD for {module_name}: {e}")
        
        # Generate index file
        index_content = f"""# TruLedgr Database Module ERDs

This directory contains Entity Relationship Diagrams for each module in the TruLedgr application.

## Generated ERD Files

{chr(10).join(f"- [{module.title()} Module](./{module}-erd.md)" for module in sorted(modules.keys()) if module != 'common')}

## Module Overview

| Module | Tables | Description |
|--------|--------|-------------|
{chr(10).join(f"| {module} | {len(tables)} | {self._get_module_description(module)} |" for module, tables in sorted(modules.items()) if module != 'common')}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        index_file = output_dir / "README.md"
        with open(index_file, 'w') as f:
            f.write(index_content)
        
        print(f"📋 Generated index file: {index_file}")
        return generated_files
    
    def _get_module_description(self, module_name: str) -> str:
        """Get a description for each module."""
        descriptions = {
            'users': 'User management, sessions, and profile data',
            'authentication': 'Authentication, OAuth, and security tokens',
            'authorization': 'Role-based access control (RBAC)',
            'groups': 'User groups and team management',
            'activities': 'Audit trails and activity logging',
            'institutions': 'Financial institutions and bank data',
            'accounts': 'User financial accounts',
            'transactions': 'Financial transactions and history',
            'items': 'General items and entities',
            'plaid': 'Plaid API integration data',
            'common': 'Shared utilities and common data'
        }
        return descriptions.get(module_name, 'Module functionality')
    
    def generate_documentation(self) -> Dict[str, Any]:
        """Generate complete documentation data."""
        return {
            'tables': self.tables,
            'relationships': self.relationships,
            'modules': self.get_modules(),
            'total_tables': len(self.tables),
            'total_relationships': len(self.relationships)
        }


def main():
    """Main function to generate ERD documentation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate ERD documentation for TruLedgr database')
    parser.add_argument('--output-dir', '-o', type=str, default='docs/developer/database',
                        help='Output directory for generated ERD files')
    parser.add_argument('--module', '-m', type=str, 
                        help='Generate ERD for specific module only')
    parser.add_argument('--format', '-f', choices=['mermaid', 'full'], default='full',
                        help='Output format: mermaid (diagram only) or full (complete markdown)')
    
    args = parser.parse_args()
    
    print("🔍 Analyzing TruLedgr database schema...")
    
    try:
        # Initialize generator
        generator = ERDGenerator()
        generator.discover_models()
        
        output_dir = Path(args.output_dir)
        
        if args.module:
            # Generate single module ERD
            print(f"📊 Generating ERD for {args.module} module...")
            
            if args.format == 'mermaid':
                erd_content = generator.generate_module_erd(args.module)
                print(erd_content)
            else:
                output_dir.mkdir(parents=True, exist_ok=True)
                modules = generator.get_modules()
                
                if args.module not in modules:
                    print(f"❌ Module '{args.module}' not found. Available modules: {list(modules.keys())}")
                    return
                
                # Create single module file
                erd_content = generator.generate_module_erd(args.module)
                module_tables = modules[args.module]
                all_tables = generator.get_related_tables(module_tables)
                related_tables = all_tables - module_tables
                
                markdown_content = f"""# {args.module.title()} Module - Entity Relationship Diagram

## Overview

This diagram shows the database schema for the **{args.module}** module.

### Core Tables
{chr(10).join(f"- `{table}`" for table in sorted(module_tables))}

### Related Tables
{chr(10).join(f"- `{table}` (from {generator.get_table_module(table)} module)" for table in sorted(related_tables)) if related_tables else "No related tables."}

## Entity Relationship Diagram

```mermaid
{erd_content}
```
"""
                
                output_file = output_dir / f"{args.module}-erd.md"
                with open(output_file, 'w') as f:
                    f.write(markdown_content)
                
                print(f"✅ Generated {args.module} module ERD: {output_file}")
        else:
            # Generate all module ERDs
            print("📊 Generating ERDs for all modules...")
            generated_files = generator.generate_all_module_erds(output_dir)
            
            print(f"\\n🎉 Successfully generated {len(generated_files)} ERD files!")
            print("📁 Files created:")
            for file_path in generated_files:
                print(f"   - {file_path}")
    
    except Exception as e:
        print(f"❌ Error generating ERD documentation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
