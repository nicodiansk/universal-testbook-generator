# ABOUTME: Default glossary content for the Specifications Hub Application.
# ABOUTME: Pre-populated in the UI for domain-specific test case generation.

DEFAULT_GLOSSARY = """## Specifications Hub Application Glossary

### Specification/Tender Specification
A "Specification" (or "Tender Specification") is a pdf/word document with detailed description of the Product/Service required for a contract. In the Specifications Hub ecosystem, a Specification is also the entity instantiated to define the configuration (basically answers to questions) needed to generate the Specification document content.

### Project
A "Project" is a container of multiple "Specifications". It often refers to a construction that is to be built and for which Specifications need to be defined.

### Application Areas

**Public Area**: Accessible to all Users without authentication. Consists of one page ("Landing Page") providing information about the platform and sign-up features.

**Specifications Area (SA)**: Available to all Authenticated Users. Users can manage "Projects" and add "Specifications" to Projects by selecting Products/Services (Sections) and answering configuration questions.

**Content Management System Area (CMS)**: Restricted area for admin users for configuration management, including Application Settings, Country Settings, User Management, Countries, Scopes, and Content Definition.

### User Types

**End User**: Application user (ABB or External) that accesses the Specifications Area to create Projects and manage Specifications.

**ABB User**: User whose email ends with "abb.com".

**External User**: User whose email does NOT end with "abb.com".

**CMS User**: Application user that accesses the CMS Area with an eligible role.

### Admin Roles (Hierarchical)

**Super Admin**: Highest-level technical administrator with full control over the system.

**Global Admin**: Business administrator at global level, can activate countries and manage Global/Country Admins and Content Owners.

**Country Admin**: Administrator for a specific country, manages Scopes and assigns Sections to Content Owners.

**Content Owner**: User responsible for content creation within a specific Section.

### Scope Hierarchy

**Country**: Geographical unit of work to which Scopes are linked.

**Global Country**: Fake country (ISO code "XX") that works as a template holder for Scopes. Not shown in Specifications Area.

**Scope**: Multi-level framework to organize Sections (Products/Services). Defined by Country/Language combination. Assigned a Standard (CSI or Generic).

**Folders**: Organizational units within a Scope (Division/Category, Sub-division/Sub-category).

**Section**: Lowest level of Scope Hierarchy, represents Products/Services that are target elements of a Specification.

### Content Management

**Content**: Hierarchical structure associated to a Section defining document structure (Parts, Clauses) and Technical Contents.

**Content Version**: Versioned instance of Content. Only the last published version is used. Statuses: Draft, Waiting for Approval, Approved, Published, Rejected.

**Technical Content Types**:
- Static Content: Text shown unconditionally
- Multi Selection Options: Multiple choice questions
- Single Selection Options: Single choice questions

### Standards

**CSI Standard**: Uses terminology Division/Sub-division/Section. Codes mandatory, content grouped by Parts.

**Generic Standard**: Uses terminology Category/Sub-category/Tender Specification. Codes optional, no Part grouping.

### Terminology Mapping

| Element | CSI Name | Generic Name |
|---------|----------|--------------|
| First level | Division | Category |
| Second level | Sub-division | Sub-category |
| Last level | Section | Tender Specification |
"""
