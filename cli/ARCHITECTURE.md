## Architecture Diagram

```
┌─────────────┐
│ LLMClient   │ ← Facade Pattern
│ (Facade)    │
└─────┬───────┘
      │ coordinates
      ▼
┌─────────────┐  ┌─────────────┐  ┌──────────────┐
│CLIExecutor  │  │PromptBuilder│  │ResponseParser│
│             │  │             │  │              │
└─────────────┘  └─────────────┘  └──────────────┘
      │                │                │
      │                │                │
┌─────────────┐  ┌─────────────┐────────┘
│ToolFormatter│  │ToolSelector │
│             │  │             │
└─────────────┘  └─────────────┘
```

This architecture follows the **Facade Pattern** where `LLMClient` provides a simple interface to a complex subsystem of specialized components.