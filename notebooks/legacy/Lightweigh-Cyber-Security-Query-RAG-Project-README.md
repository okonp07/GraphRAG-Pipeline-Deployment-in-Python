# The Simple Cyber-Security Query Assistant

### **A Simple AI-Powered Cyber-Security Query Assistant in Python**

This project presents an implementation of an interactive system designed to answer cybersecurity-related queries using a fine-tuned language model. The system integrates document parsing, chunking, semantic embeddings, and model fine-tuning to provide contextually relevant and accurate responses. 

The system uses a lightweight transformer-based model to ensure fast deployment and experimentation. It also provides an interactive interface using **ipywidgets** for easy exploration.

## Project Objective

- Fine-tune a pre-trained language model on cybersecurity-related text data.
- Enable querying of the fine-tuned model to generate relevant answers.
- Provide an easy-to-use interface for practical exploration of the model's capabilities.

## Model Used

The model used in this project is [`TinyLlama/TinyLlama-1.1B-Chat-v1.0`](https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0), a small and efficient transformer-based model. It is fine-tuned to respond effectively to cybersecurity-related queries.

### Why TinyLlama?

- It is lightweight and can be run on CPUs or modest GPUs.
- Requires less memory and computation, enabling easier development and deployment.
- Suitable for fast experimentation and domain-specific fine-tuning.

### Domain Specialization

This model was fine-tuned using the `zeroshot/cybersecurity-corpus`, which provides a specialized dataset for cybersecurity topics. The fine-tuning process makes the model capable of understanding and answering questions related to cybersecurity, ideal for security analysts, enterprise systems, and educational applications.

## Dataset

This implementation is designed to work with a corpus of text documents related to cybersecurity. The dataset is split into chunks, embedded, and used to fine-tune the language model. While the current dataset used is the `zeroshot/cybersecurity-corpus`, it is flexible and can be adapted to other related datasets.

## Installation

To get started, install the required dependencies:

```bash
pip install langchain openai gradio networkx sentence-transformers python-dotenv transformers accelerate tqdm matplotlib
```

## Optional Dependencies

For additional functionality, install:

```bash
pip install faiss-cpu
pip install huggingface_hub
```

## API Key Configuration

If you are using OpenAI services for embeddings or language models, create a `.env` file in your project root directory with the following content:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```
## How to Run

1. Clone this repository or download the notebook.
2. Install all dependencies listed above.
3. Set up your `.env` file with API keys if applicable.
4. Run the notebook step-by-step in a Jupyter environment.
5. Interact with the model via the ipywidgets interface for answering cybersecurity queries.


## Key Libraries and Tools

| Library/Tool           | Description                                                         |
|------------------------|---------------------------------------------------------------------|
| **TinyLlama**          | Pre-trained transformer model fine-tuned for cybersecurity queries  |
| **OpenAI / HuggingFace**| For loading and fine-tuning the TinyLlama model                     |
| **Sentence-Transformers**| Alternative for local embedding generation                           |
| **ipywidgets**         | Interactive widgets for building a user interface in Jupyter notebooks |
| **Gradio**             | UI framework (optional) for creating a user-friendly interface      |
| **Transformers**       | For loading and using the TinyLlama model                           |
| **FAISS (optional)**   | Fast Approximate Nearest Neighbor search (for future integration)   |
| **dotenv**             | For securely loading API keys                                      |


## Model License

- **Model License**: Apache License 2.0  
- **Frameworks and Dependencies**: Open-source (MIT/BSD/Apache licenses)  

Please ensure you comply with the individual licenses of all libraries and models used in this project.

## Possible Future Improvements

- Integrate an external graph database (e.g., Neo4j or Weaviate) for scalable knowledge graph management.
- Support additional file types such as PDF, Word, or HTML using parsers like PyMuPDF or BeautifulSoup.
- Enhance the querying system with vector databases like FAISS for more efficient search.
- Expand the model's domain-specific knowledge by fine-tuning with additional datasets.

## Author

**Okon Prince**  
*Data Scientist and AI Researcher  
Developer; Simple Cyber-Security Query Assistant  
Specialized in AI applications for cybersecurity, environmental intelligence, and education.*
