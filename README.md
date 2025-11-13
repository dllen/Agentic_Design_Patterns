# Agentic Design Patterns: A Hands-On Guide to Building Intelligent Systems

This repository contains comprehensive resources for understanding and implementing agentic design patterns - architectural approaches for building intelligent, autonomous systems that can operate effectively in complex environments. The project includes practical code examples, tutorials, and a complete smart customer service system demonstrating these patterns in action.

## 📚 Project Overview

This repository accompanies the book "Agentic Design Patterns: A Hands-On Guide to Building Intelligent Systems" by Antonio Gulli. It provides:

- **21+ chapters** of practical code examples and tutorials covering essential agentic design patterns
- **Complete implementation** of a smart customer service system showcasing multiple patterns
- **Jupyter notebooks** with hands-on examples using popular frameworks like LangChain, LangGraph, CrewAI, and Google ADK
- **Tutorial materials** in Chinese with detailed explanations and code samples

## 🗂️ Repository Structure

```
Agentic_Design_Patterns/
├── notebooks/              # Chapter-wise Jupyter notebooks with code examples
├── tutorial/               # Tutorial materials organized by chapter
├── smart_customer_service/ # Complete customer service system implementation
├── README.md              # This file
└── Agentic_Design_Patterns.pdf # Book content
```

### Notebooks Directory
Contains practical implementations of agentic design patterns organized by chapter:

- **Chapter 1**: Prompt Chaining - Breaking complex tasks into sequential steps
- **Chapter 2**: Routing - Directing requests to appropriate handlers
- **Chapter 3**: Parallelization - Executing multiple operations concurrently
- **Chapter 4**: Reflection - Self-assessment and improvement mechanisms
- **Chapter 5**: Tool Use - Integrating external tools and APIs
- **Chapter 6**: Planning - Creating and executing action plans
- **Chapter 7**: Multi-Agent Collaboration - Coordinating multiple agents
- **Chapter 8**: Memory Management - State and context persistence
- **Chapter 9**: Adaptation - Learning and adjusting to new situations
- **Chapter 10**: Model Context Protocol (MCP) - Standardized communication
- **Chapter 12**: Exception Handling and Recovery - Error management strategies
- **Chapter 13**: Human-in-the-Loop - Integrating human oversight and intervention
- **Chapter 14**: Knowledge Retrieval (RAG) - Retrieval-Augmented Generation systems
- **Chapter 15**: Inter-Agent Communication - Communication protocols
- **Chapter 16**: Resource-Aware Optimization - Efficient resource utilization
- **Chapter 17**: Reasoning Techniques - Advanced reasoning patterns
- **Chapter 18**: Guardrails & Safety Patterns - Safety and security measures
- **Chapter 19**: Evaluation and Monitoring - Performance tracking
- **Chapter 20**: Prioritization - Task and request prioritization
- **Chapter 21**: Exploration and Discovery - Agent laboratory and experimentation

### Tutorial Directory
Contains detailed Chinese tutorials for each chapter, providing:

- Conceptual explanations of design patterns
- Step-by-step implementation guides
- Code examples with detailed comments
- Best practices and use cases

### Smart Customer Service System
A complete, production-ready implementation demonstrating multiple agentic patterns working together:

- **Multi-agent architecture** with specialized agents
- **Knowledge management** with RAG system
- **Goal management** for tracking customer requests
- **Exception handling** with fallback strategies
- **Human-in-the-loop** escalation mechanisms
- **Communication hub** for inter-agent coordination

## 🧠 Agentic Design Patterns Overview

### Core Patterns

1. **Prompt Chaining**: Breaking complex tasks into sequential, manageable steps where the output of one step becomes the input for the next.

2. **Routing**: Intelligent request distribution to appropriate specialized handlers based on content analysis.

3. **Parallelization**: Executing multiple operations concurrently to improve performance and throughput.

4. **Reflection**: Self-assessment mechanisms allowing agents to evaluate and improve their performance.

5. **Tool Use**: Integration of external tools, APIs, and services to extend agent capabilities.

6. **Planning**: Strategic planning and execution of multi-step tasks with goal management.

7. **Multi-Agent Collaboration**: Coordination between multiple specialized agents to solve complex problems.

8. **Memory Management**: State persistence and context management across interactions.

9. **Adaptation**: Learning and adjustment mechanisms for changing environments and requirements.

### Advanced Patterns

10. **Model Context Protocol (MCP)**: Standardized communication protocols between agents and external systems.

11. **Exception Handling & Recovery**: Robust error handling with multiple recovery strategies.

12. **Human-in-the-Loop**: Seamless integration of human expertise and oversight.

13. **Knowledge Retrieval (RAG)**: Integration of external knowledge sources for enhanced responses.

14. **Inter-Agent Communication**: Protocols for communication between agents.

15. **Resource-Aware Optimization**: Efficient utilization of computational and API resources.

16. **Reasoning Techniques**: Advanced reasoning patterns including chain-of-thought and self-correction.

17. **Guardrails & Safety**: Safety mechanisms to prevent harmful outputs and ensure compliance.

18. **Evaluation & Monitoring**: Performance tracking and quality assurance mechanisms.

19. **Prioritization**: Intelligent task and request prioritization strategies.

20. **Exploration & Discovery**: Experimentation and learning frameworks for agent improvement.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Access to LLM APIs (OpenAI, Google Gemini, etc.)

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd Agentic_Design_Patterns
```

2. Install dependencies for the smart customer service system:
```bash
cd smart_customer_service
pip install -r requirements.txt
```

3. Set up environment variables for API keys:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Running the Smart Customer Service System
```bash
cd smart_customer_service
python main.py
```

### Exploring Jupyter Notebooks
Most notebooks are self-contained examples that demonstrate specific patterns. You can run them directly in Jupyter:

```bash
jupyter notebook
```

## 🏗️ Smart Customer Service System Architecture

The smart customer service system demonstrates how multiple agentic patterns work together:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Customer     │    │  Communication  │    │   Knowledge     │
│   Interface    │◄──►│      Hub        │◄──►│    Base &       │
│                │    │                 │    │     RAG         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌───────▼────────┐
│Customer Service│   │  Specialized    │   │  Goal &         │
│    Agent       │   │   Agents        │   │ Exception       │
│                │   │                 │   │   Manager       │
│ • Coordination │   │ • Tech Support  │   │                 │
│ • Routing      │   │ • Billing       │   │ • Goal Tracking │
│ • Escalation   │   │ • Escalation    │   │ • Error Recovery│
└────────────────┘   └─────────────────┘   └─────────────────┘
```

### Key Components:
- **Customer Service Agent**: Main orchestrator that routes requests and coordinates with other agents
- **Specialized Agents**: Domain-specific agents (tech support, billing, escalation)
- **Knowledge Base & RAG**: Information retrieval and contextual response generation
- **Goal Manager**: Tracks customer request lifecycle and completion status
- **Exception Handler**: Manages errors and provides fallback strategies
- **Communication Hub**: Facilitates inter-agent communication

## 🎯 Key Benefits of Agentic Design Patterns

1. **Scalability**: Modular patterns allow for easy expansion and modification
2. **Resilience**: Built-in error handling and recovery mechanisms
3. **Flexibility**: Patterns can be combined and adapted to specific use cases
4. **Maintainability**: Clear separation of concerns and modular architecture
5. **Intelligence**: Advanced reasoning and decision-making capabilities
6. **Safety**: Comprehensive guardrails and safety mechanisms

## 📖 Learning Path

1. **Start with fundamentals**: Chapters 1-6 cover basic patterns
2. **Explore advanced patterns**: Chapters 7-11 introduce more complex designs
3. **Master safety and monitoring**: Chapters 18-19 ensure robust implementations
4. **Practice with the complete system**: Study the smart customer service implementation
5. **Experiment with patterns**: Use Chapter 21's agent laboratory for experimentation

## 🤝 Contributing

This repository is a living resource for the agentic design patterns community. Contributions are welcome in the form of:
- Bug reports and fixes
- Additional examples and tutorials
- Performance improvements
- New pattern implementations
- Documentation enhancements

## 📄 License

This repository contains code examples and materials related to the "Agentic Design Patterns" book. Please refer to the LICENSE file for specific licensing terms.

## 🙏 Acknowledgments

This repository is based on the work of Antonio Gulli in "Agentic Design Patterns: A Hands-On Guide to Building Intelligent Systems". The examples demonstrate practical implementations of the patterns described in the book using modern frameworks and tools.

---

*For more detailed information about each pattern, refer to the specific chapter notebooks and tutorials in this repository.*