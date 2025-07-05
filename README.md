# Vira - AI Assistant with Long-Term Memory

This project implements a Python-based AI assistant named Vira with long-term memory capabilities using Azure OpenAI and PostgreSQL with pgvector.

## Features

- Long-term memory storage using vector embeddings in PostgreSQL
- Azure OpenAI integration for chat responses and embeddings
- Similarity-based memory retrieval
- Modular architecture separating concerns

## Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Azure OpenAI API access

### Installation

1. Clone this repository
2. Create a `.env` file with your Azure OpenAI credentials (see `.env` example)
3. Install dependencies:

## Architecture

- `app.py` - Main application with Vira assistant
- `memory_manager.py` - Memory management system
- `embedding_service.py` - Azure OpenAI embedding service
- `chat_service.py` - Azure OpenAI chat service
- `db_connector.py` - PostgreSQL database connector
- `db_init.sql` - Database initialization script

## Usage

After starting the application, you can chat with Vira. The system will:
1. Retrieve relevant memories based on your input
2. Include these memories in the context for generating a response
3. Save the interaction to the long-term memory

Type 'exit' to quit the application.

## Environment Variables

- `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_VERSION` - API version (e.g., 2023-05-15)
- `AZURE_OPENAI_DEPLOYMENT_NAME` - Your chat model deployment name
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME` - Your embedding model deployment name
- Database connection parameters (see `.env` example)