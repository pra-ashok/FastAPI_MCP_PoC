# Architecture: FastAPI_MCP_PoC

```mermaid
graph TD
    subgraph "Frontend (Python Dashboard)"
        UI[Dashboard / UI]
        Metrics[Metrics Viewer]
        ConfigUI[Config Editor]
    end

    subgraph "Backend (FastAPI Server)"
        API[FastAPI Router]
        MCP[MCP Core Server]
        CM[Config Manager]
        VS[Vector Service]
        DB[(ChromaDB)]
    end

    UI <--> API
    API <--> MCP
    API <--> CM
    MCP <--> VS
    VS <--> DB
    CM <--> ConfigFile[(config.yaml)]

    style DB fill:#f9f,stroke:#333,stroke-width:2px
    style ConfigFile fill:#bbf,stroke:#333,stroke-width:2px
```

## Key Components

1.  **Dashboard (Frontend)**: For monitoring, editing configurations, and visualizing knowledge base queries.
2.  **FastAPI Router (Backend)**: Orchestrates requests between the UI and the MCP/Vector services.
3.  **MCP Core**: Implements the Model Context Protocol, exposing tools to AI clients.
4.  **Vector Service**: Provides RAG (Retrieval-Augmented Generation) capabilities using ChromaDB.
5.  **Config Manager**: Handles dynamic updates to `config.yaml`.
