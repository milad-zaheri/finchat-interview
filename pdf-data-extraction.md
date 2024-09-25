# How to Retrieve data from PDF accurately

I believe the best solution to retrieve data from a PDF document is to leverage Retrieval-Augmented Generation (RAG). 
- RAG represents a model architecture blending features of both retrieval-based and generation-based approaches in natural language processing (NLP). 
- The fundamental concept underlying RAG is to amalgamate the advantages of retrieval-based methods, proficient at leveraging pre-existing knowledge from extensive text corpora, with the adaptability and inventiveness of generation-based methods, capable of crafting novel and coherent text.
- Within the RAG architecture, a retriever module initially fetches pertinent documents or passages from a vast corpus of text, based on an input query or prompt. These retrieved passages function as context or knowledge for the generation model. Subsequently, a generation model, often rooted in transformers like GPT (Generative Pre-trained Transformer) or BERT (Bidirectional Encoder Representations from Transformers), employs this retrieved context to produce responses or outputs.


## Step 1 - Load
First we need to load our data. This is done with Document Loaders.
To extract data from PDF document, we can use Langchain loader to load text in a format usable by an LLM:
  - The loader reads the PDF at the specified path into memory.
  - It then extracts text data using the python package.
  - Finally, it creates a LangChain Document for each page of the PDF with the page's content and some metadata about where in the document the text came from.

## Step 2 - Split
Text splitters break large Documents into smaller chunks. This is useful both for indexing data and for passing it in to a model, since large chunks are harder to search over and won't fit in a model's finite context window.
Our loaded documents are usually long. This is too long to fit in the context window of many models. Even for those models that could fit the full post in their context window, models can struggle to find information in very long inputs.
To handle this we’ll split the Document into chunks for embedding and vector storage. This should help us retrieve only the most relevant bits of the blog post at run time.

## Step 3 - Store
We need somewhere to store and index our splits, so that they can later be searched over. This is often done using a VectorStore and Embeddings model.
A good solution would be using OpenAI embeddings and ChromaDB library to build a vector store and then use one of the five Langchain retrievers:
- Build a vector store - The vector store will store the embeddings of the source documents and these embeddings are used in a similarity search of the question to find the texts that are similar to the question being asked.


## Step 4 - Retrieve
Given a user input, relevant splits are retrieved from storage using a Retriever.
First we need to define our logic for searching over documents. LangChain defines a Retriever interface which wraps an index that can return relevant Documents given a string query.
- Choose on of the five different retrievers of Langchain: MultiQueryRetriever, SelfQueryRetriever, ContextualCompressionRetriever, Vectordb standard retriever, depending on the accuracy.
- The accuracy of each retriever could be tested using OpenAI to answer questions based on information provided.

## Step 5 - Generate
A ChatModel / LLM produces an answer using a prompt that includes the question and the retrieved data
