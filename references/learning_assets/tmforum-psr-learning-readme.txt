TM FORUM PSR MODEL LEARNING ENVIRONMENT
=======================================

Purpose
-------

This folder is a hands-on learning environment for understanding and
experimenting with the TM Forum Product-Service-Resource (PSR) model
through Python code.

The goal is to bridge the gap between abstract telecom standards and
practical implementation by:

  1. Understanding the PSR layered architecture
  2. Mapping TM Forum schemas to Python data classes
  3. Building simple simulations that demonstrate the relationships
  4. Learning how real BSS/OSS systems are structured


Folder Structure
----------------

  tmforum_psr_learning/
  │
  ├── 00_README.txt                    <- You are here
  ├── 01_standards_location.txt        <- Where to find TM Forum specs
  ├── 02_essential_files.txt           <- Key files for PSR learning
  ├── 03_psr_code_mapping.txt          <- How PSR maps to Python code
  ├── 04_project_structure.txt         <- Recommended code organization
  │
  ├── src/                             <- Python source code (to create)
  │   ├── models/                      <- Data models (Product, Service, Resource)
  │   ├── catalogs/                    <- Catalog implementations
  │   ├── inventory/                   <- Inventory implementations
  │   └── orders/                      <- Order processing
  │
  ├── examples/                        <- Working examples (to create)
  │   ├── 01_basic_psr.py              <- Simple PSR relationships
  │   ├── 02_catalog_demo.py           <- Catalog operations
  │   └── 03_order_flow.py             <- End-to-end order simulation
  │
  └── tests/                           <- Unit tests (to create)


Related Resources
-----------------

TM Forum Standards Location:
  <USER_HOME>/Documents/Git_Offline/active/
  21_Networking_Public_Data/49_TMForum_Standards/

Key subdirectories there:
  - schemas/                   JSON Schema definitions
  - Open_Api_And_Data_Model-latest/   OpenAPI specifications
  - ig1353-api-developers-guide/      Developer documentation


Learning Path
-------------

1. READ: Start with 01_standards_location.txt to understand where
   the specifications live and how they're organized.

2. STUDY: Review 02_essential_files.txt to identify which specific
   files are most important for understanding PSR.

3. MAP: Use 03_psr_code_mapping.txt to see how the abstract model
   translates into concrete Python code patterns.

4. BUILD: Follow 04_project_structure.txt to organize your own
   implementation experiments.

5. EXPERIMENT: Create and run examples in the examples/ folder.
