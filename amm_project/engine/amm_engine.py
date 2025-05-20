import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Tuple
from datetime import datetime, timezone
import uuid # For unique engine instance ID
import json
import logging # Add logging import
import pathlib

import google.generativeai as genai
import lancedb
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, desc
from sqlalchemy.orm import declarative_base, sessionmaker, Session # For type hinting
from dotenv import load_dotenv

from amm_project.models.amm_models import AMMDesign, KnowledgeSourceType, KnowledgeSourceConfig, AdaptiveMemoryConfig, GeminiConfig, AgentPrompts, GeminiModelType
from amm_project.models.memory_models import create_db_engine_and_tables, get_session_local, InteractionRecordORM, InteractionRecordPydantic, InteractionRecordUpdatePydantic # Added InteractionRecordUpdatePydantic

# Try to import PDF processor for PDF knowledge sources
try:
    from amm_project.utils.pdf_processor import PDFProcessor
    PDF_PROCESSOR_AVAILABLE = True
except ImportError:
    print("PDF processor not available. PDF knowledge sources will be skipped.")
    PDF_PROCESSOR_AVAILABLE = False

LANCEDB_TABLE_NAME = "fixed_knowledge_table"

class AMMEngine:
    """
    The core engine for an AG-Mem-Module (AMM).
    This class is responsible for loading an AMM design, initializing necessary components
    (like knowledge bases and AI models), processing user queries, and managing memory.
    """
    def __init__(self, design: AMMDesign, base_data_path: Optional[str] = None):
        """Initialize the AMMEngine with a given design and optional base data path."""
        self.design = design
        self.engine_instance_id = uuid.uuid4().hex[:8] # Short ID for this engine instance

        # Initialize logger for this instance
        self.logger = logging.getLogger(f"{self.__class__.__name__}_{self.engine_instance_id}")
        if not self.logger.handlers: # Configure if not already configured by a higher-level setup
            # Basic configuration for console output during development/testing
            # For production, logging would typically be configured externally
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG) # Default to DEBUG for this class

        self.logger.debug(f"AMMEngine __init__ STARTED.")

        self.base_data_path_str = base_data_path
        self.instance_data_path: Optional[Path] = None
        self.lancedb_path: Optional[Path] = None
        self.sqlite_path: Optional[Path] = None
        self.ai_model_client = None
        self.lancedb_connection = None
        self.lancedb_table = None
        self.adaptive_memory_engine = None
        self.db_session_factory = None

        self.embedding_model_name: Optional[str] = None # For storing the configured embedding model

        self._initialize_paths()
        self._initialize_gemini_client()
        
        print(f"DEBUG_INIT (Engine ID: {self.engine_instance_id}): About to call _initialize_fixed_knowledge.")
        self._initialize_fixed_knowledge()
        print(f"DEBUG_INIT (Engine ID: {self.engine_instance_id}): Finished _initialize_fixed_knowledge call.")
        print(f"DEBUG_INIT (Engine ID: {self.engine_instance_id}): About to call _initialize_adaptive_memory.")
        self._initialize_adaptive_memory()
        print(f"DEBUG_INIT (Engine ID: {self.engine_instance_id}): Finished _initialize_adaptive_memory call.")
        print(f"DEBUG_INIT (Engine ID: {self.engine_instance_id}): Final check before __init__ exits try block. AI Client is None: {self.ai_model_client is None}")
        print(f"DEBUG_INIT (Engine ID: {self.engine_instance_id}): AMMEngine initialized for design '{self.design.name}' (ID: {self.design.design_id}). __init__ ENDED.")

    def _initialize_paths(self) -> None:
        """Initializes and creates necessary directory paths based on the design and base_data_path."""
        print(f"DEBUG_PATHS (Engine ID: {self.engine_instance_id}): _initialize_paths called.")

        # Ensure the amm_instances directory exists at the root level
        root_amm_instances = Path("amm_instances")
        try:
            root_amm_instances.mkdir(parents=True, exist_ok=True)
            print(f"DEBUG_PATHS (Engine ID: {self.engine_instance_id}): Ensured root amm_instances directory exists: {root_amm_instances.resolve()}")
        except Exception as e:
            print(f"DEBUG_PATHS (Engine ID: {self.engine_instance_id}): Error creating root amm_instances directory: {e}")
            # Continue despite error, we'll try to use the path anyway

        # Determine and create the main instance data path FIRST
        if self.base_data_path_str:
            self.instance_data_path = Path(self.base_data_path_str)
        else:
            self.instance_data_path = root_amm_instances / self.design.design_id
        
        print(f"DEBUG_PATHS (Engine ID: {self.engine_instance_id}): Determined instance_data_path: {self.instance_data_path}")
        
        try:
            self.instance_data_path.mkdir(parents=True, exist_ok=True)
            print(f"DEBUG_PATHS (Engine ID: {self.engine_instance_id}): Ensured instance_data_path exists: {self.instance_data_path.resolve()}")
        except Exception as e:
            print(f"DEBUG_PATHS (Engine ID: {self.engine_instance_id}): Error creating instance_data_path {self.instance_data_path}: {e}")
            # Don't raise here, try to continue even if there's an error
            # We'll handle missing paths in the specific initialization methods

        # NOW define lancedb_path and sqlite_path using the initialized instance_data_path
        self.lancedb_path = self.instance_data_path / "lancedb_fixed_knowledge"
        print(f"DEBUG_PATHS (Engine ID: {self.engine_instance_id}): LanceDB path set to: {self.lancedb_path}")

        if self.design.adaptive_memory.enabled:
            db_name = f"{self.design.adaptive_memory.db_name_prefix}_{self.design.design_id}.sqlite"
            self.sqlite_path = self.instance_data_path / db_name
            print(f"DEBUG_PATHS (Engine ID: {self.engine_instance_id}): SQLite path set to: {self.sqlite_path}")
        else:
            self.sqlite_path = None
            print(f"DEBUG_PATHS (Engine ID: {self.engine_instance_id}): Adaptive memory disabled, SQLite path set to None.")

        print(f"DEBUG_PATHS (Engine ID: {self.engine_instance_id}): _initialize_paths completed.")

    def _initialize_gemini_client(self) -> None:
        """Initializes the Gemini AI model client if an API key is provided."""
        print(f"DEBUG_GEMINI (Engine ID: {self.engine_instance_id}): _initialize_gemini_client called.")
        
        # Load environment variables if not already loaded
        load_dotenv()
        
        # Get API key from environment variable
        api_key_var_name = self.design.gemini_config.api_key_env_var
        api_key = os.environ.get(api_key_var_name) or os.environ.get('API_KEY')
        
        if not api_key:
            print(f"DEBUG_GEMINI (Engine ID: {self.engine_instance_id}): No API key found in environment variable '{api_key_var_name}' or 'API_KEY'. AI functionality will be disabled.")
            return
        
        try:
            # Initialize the Gemini client
            genai.configure(api_key=api_key)
            self.ai_model_client = genai
            
            # Use the embedding model from environment if available, otherwise use the one from design
            env_embedding_model = os.environ.get('EMBEDDING')
            if env_embedding_model:
                print(f"DEBUG_GEMINI (Engine ID: {self.engine_instance_id}): Using embedding model from environment: {env_embedding_model}")
                self.embedding_model_name = env_embedding_model
            else:
                self.embedding_model_name = self.design.gemini_config.embedding_model_name
                print(f"DEBUG_GEMINI (Engine ID: {self.engine_instance_id}): Using embedding model from design: {self.embedding_model_name}")
            
            print(f"DEBUG_GEMINI (Engine ID: {self.engine_instance_id}): Gemini client initialized successfully.")
        except Exception as e:
            print(f"DEBUG_GEMINI (Engine ID: {self.engine_instance_id}): Error initializing Gemini client: {type(e).__name__} - {e}")
            self.ai_model_client = None
            self.embedding_model_name = None
            print(f"DEBUG_GEMINI (Engine ID: {self.engine_instance_id}): Gemini API key from env var '{api_key_env_var}' not found. AI model client and embedding model set to None.")
        print(f"DEBUG_GEMINI (Engine ID: {self.engine_instance_id}): _initialize_gemini_client completed. AI Client is None: {self.ai_model_client is None}, Embedding model: {self.embedding_model_name}")

    def _embed_content(self, text_to_embed: str, task_type: str = "RETRIEVAL_DOCUMENT") -> Optional[List[float]]:
        """Generates an embedding for the given text using the configured Gemini model."""
        print(f"DEBUG_EMBED (Engine ID: {self.engine_instance_id}): _embed_content called for task_type '{task_type}'. Text length: {len(text_to_embed)}.")
        if not self.ai_model_client or not self.embedding_model_name:
            # This case should ideally be caught before calling _embed_content by checking ai_client_available_for_embedding
            self.logger.warning(f"Embedding not attempted: AI model client or embedding model name not set.")
            return None
        try:
            # Ensure the task_type is valid if the model requires it (some embedding models are task-specific)
            result = genai.embed_content(
                model=self.embedding_model_name, # e.g., "models/text-embedding-004"
                content=text_to_embed,
                task_type=task_type # e.g., "RETRIEVAL_DOCUMENT", "SEMANTIC_SIMILARITY"
            )
            return result['embedding']
        except Exception as e:
            self.logger.error(f"ERROR generating embedding: {type(e).__name__} - {e}")
            # import traceback
            # traceback.print_exc() # Consider if full traceback is needed in prod logs
            return None

    def _get_embedding_function(self):
        """Returns the Gemini embedding function for LanceDB if an AI client is available."""
        pass

    def _initialize_fixed_knowledge(self) -> None:
        """Initializes the fixed knowledge base (LanceDB)."""
        print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): _initialize_fixed_knowledge CALLED.")
        if not self.design.knowledge_sources:
            print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): No knowledge sources defined. Skipping LanceDB initialization. self.lancedb_table remains None.")
            self.lancedb_table = None
            return

        if not self.lancedb_path:
            print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): LanceDB path is not set. Cannot initialize fixed knowledge. self.lancedb_table remains None.")
            self.lancedb_table = None
            return
        
        # Check if AI client is available for embeddings
        ai_client_available_for_embedding = self.ai_model_client is not None and self.embedding_model_name is not None
        print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): AI client configured for embedding: {ai_client_available_for_embedding}. Embedding model: {self.embedding_model_name}")

        knowledge_data_for_db: List[Dict[str, Any]] = []
        table_name = LANCEDB_TABLE_NAME # Using defined constant

        print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Processing {len(self.design.knowledge_sources)} knowledge sources.")
        for ks_config in self.design.knowledge_sources:
            text_to_embed: Optional[str] = None
            source_identifier = f"KS ID {ks_config.id} ({ks_config.name})"

            if ks_config.type == KnowledgeSourceType.TEXT:
                text_to_embed = ks_config.content
                print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Processing TEXT source: {source_identifier}")
            
            elif ks_config.type == KnowledgeSourceType.FILE:
                print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Processing FILE source: {source_identifier}, Path: {ks_config.path}")
                if not ks_config.path:
                    self.logger.warning(f"Path not provided for FILE source {source_identifier}. Skipping.")
                    continue
                try:
                    # Attempt to resolve the path. If relative, it's against CWD.
                    # For robustness, consider making paths relative to design file or a content root.
                    file_path = Path(ks_config.path).resolve()
                    print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Resolved file path for {source_identifier} to {file_path}")
                    if not file_path.is_file():
                        self.logger.warning(f"File path {file_path} for {source_identifier} is not a file or does not exist. Skipping.")
                        continue
                    
                    # Check if the file is a PDF
                    if file_path.suffix.lower() == '.pdf':
                        if PDF_PROCESSOR_AVAILABLE:
                            from amm_project.utils.pdf_processor import process_pdf
                            print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Processing PDF file {file_path} for {source_identifier}")
                            # Process the PDF file and get chunks
                            pdf_chunks = process_pdf(str(file_path))
                            if not pdf_chunks:
                                self.logger.warning(f"No text extracted from PDF {file_path} for {source_identifier}")
                                continue
                                
                            # For each chunk, create an embedding and add to knowledge data
                            for chunk in pdf_chunks:
                                chunk_text = chunk['text']
                                if chunk_text and ai_client_available_for_embedding:
                                    print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Embedding PDF chunk {chunk['id']} from {source_identifier}")
                                    embedding_vector = self._embed_content(text_to_embed=chunk_text, task_type="RETRIEVAL_DOCUMENT")
                                    
                                    if embedding_vector:
                                        # Create a unique ID for each chunk
                                        chunk_id = f"{ks_config.id}_{chunk['id']}"
                                        # Merge the metadata dictionaries properly
                                        merged_metadata = {}
                                        if ks_config.metadata:
                                            merged_metadata.update(ks_config.metadata)
                                        merged_metadata.update(chunk['metadata'])
                                        
                                        knowledge_data_for_db.append({
                                            "id": chunk_id,
                                            "text": chunk_text,
                                            "vector": embedding_vector,
                                            "source_name": f"{ks_config.name} (PDF chunk {chunk['metadata']['chunk_index'] + 1}/{chunk['metadata']['total_chunks']})",
                                            "metadata": merged_metadata
                                        })
                                        print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Successfully embedded PDF chunk {chunk_id} from {source_identifier}")
                            continue  # Skip the standard text processing below since we've handled the PDF
                        else:
                            self.logger.warning(f"PDF processor not available for {source_identifier}. Attempting to read as text.")
                    
                    # Standard text file processing for non-PDF files or if PDF processor is not available
                    text_to_embed = file_path.read_text(encoding=ks_config.encoding or 'utf-8')
                    print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Successfully read content from file {file_path} for {source_identifier}. Length: {len(text_to_embed)}")
                except FileNotFoundError:
                    self.logger.warning(f"FileNotFoundError for {source_identifier} at path {ks_config.path}. Skipping.")
                    continue
                except Exception as e:
                    self.logger.error(f"ERROR reading file {ks_config.path} for {source_identifier}: {type(e).__name__} - {e}. Skipping.")
                    continue
            else:
                self.logger.warning(f"Skipping {source_identifier} due to unhandled type: {ks_config.type.value}")
                continue # Skip to next knowledge source

            if text_to_embed and ai_client_available_for_embedding:
                print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Attempting to embed content from {source_identifier}: '{text_to_embed[:100]}...' using model {self.embedding_model_name}")
                embedding_vector = self._embed_content(text_to_embed=text_to_embed, task_type="RETRIEVAL_DOCUMENT")
                
                if embedding_vector:
                    knowledge_data_for_db.append({
                        "id": ks_config.id, # Ensure this is a unique string for LanceDB
                        "text": text_to_embed,
                        "vector": embedding_vector,
                        "source_name": ks_config.name,
                        "metadata": ks_config.metadata or {}
                    })
                    print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Successfully embedded and prepared data for {source_identifier}.")
                else:
                    self.logger.warning(f"Failed to get embedding for {source_identifier}. Skipping addition to DB.")
            elif not text_to_embed:
                print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Skipping {source_identifier} due to empty or unreadable content.")
            elif not ai_client_available_for_embedding:
                self.logger.warning(f"Skipping {source_identifier} because AI client for embeddings is not available.")


        print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Populated {len(knowledge_data_for_db)} items for LanceDB table.")
        # Check if table exists, if so, open it. Otherwise, lancedb_table remains None.
        try:
            self.lancedb_connection = lancedb.connect(self.lancedb_path)
            print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Successfully connected to LanceDB at '{self.lancedb_path}'.")
            table_name = LANCEDB_TABLE_NAME
            
            if table_name in self.lancedb_connection.table_names():
                self.lancedb_table = self.lancedb_connection.open_table(table_name)
                print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Successfully opened existing LanceDB table '{table_name}'.")
                
                # If we have new knowledge data, add it to the existing table
                if knowledge_data_for_db:
                    print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Adding {len(knowledge_data_for_db)} items to existing LanceDB table '{table_name}'.")
                    self.lancedb_table.add(knowledge_data_for_db)
                    print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Successfully added items to existing table.")
            else:
                # Create the table if we have knowledge data
                if knowledge_data_for_db:
                    print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Creating new LanceDB table '{table_name}' with {len(knowledge_data_for_db)} items.")
                    
                    # Drop the existing table if it exists to avoid schema conflicts
                    if table_name in self.lancedb_connection.table_names():
                        print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Dropping existing table '{table_name}' due to schema mismatch.")
                        self.lancedb_connection.drop_table(table_name)
                    
                    # Create a new table with the current schema
                    try:
                        # Create a list of dictionaries with just the essential fields
                        essential_data = []
                        for item in knowledge_data_for_db:
                            essential_item = {
                                "id": str(item["id"]),  # Ensure id is a string
                                "text": str(item["text"]),  # Ensure text is a string
                                "vector": item["vector"],  # Keep vector as is
                                "source": str(item["source_name"])  # Rename to 'source' for simplicity
                            }
                            essential_data.append(essential_item)
                        
                        # Create the table with a simple schema
                        print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Attempting to create table with {len(essential_data)} items using simplified approach")
                        
                        # Create a pandas DataFrame first
                        import pandas as pd
                        df = pd.DataFrame(essential_data)
                        
                        # Create the table from the DataFrame
                        self.lancedb_table = self.lancedb_connection.create_table(table_name, data=df)
                        print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Successfully created LanceDB table using pandas DataFrame approach")
                    except Exception as e:
                        print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Error creating table: {e}")
                        
                        # Last resort: try to create an empty table and add data later
                        try:
                            print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Attempting to create empty table as last resort")
                            schema = {
                                "id": "string",
                                "text": "string",
                                "vector": "float[]",
                                "source": "string"
                            }
                            self.lancedb_table = self.lancedb_connection.create_table(table_name, schema=schema)
                            print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Successfully created empty LanceDB table")
                            
                            # Now try to add data one by one
                            for item in essential_data:
                                try:
                                    self.lancedb_table.add([item])
                                    print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Added item {item['id']} to table")
                                except Exception as item_e:
                                    print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Failed to add item {item['id']}: {item_e}")
                        except Exception as e2:
                            print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Failed to create empty table: {e2}")
                            self.lancedb_table = None
                    
                    # Only print overall success if we actually have a table
                    if self.lancedb_table is not None:
                        print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): Successfully created new LanceDB table '{table_name}'.")
                else:
                    print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): No knowledge data to add. LanceDB table '{table_name}' not created.")
                    self.lancedb_table = None
        except Exception as e:
             print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): ERROR interacting with LanceDB at '{self.lancedb_path}': {type(e).__name__} - {e}. self.lancedb_table set to None.")
             self.lancedb_table = None
        
        # Log the final state of the LanceDB table
        print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): _initialize_fixed_knowledge finished. LanceDB table is {'set' if self.lancedb_table else 'None'}.")
        return

        # If fixed knowledge is disabled or no sources, lancedb_table might remain None
        print(f"DEBUG_FK (Engine ID: {self.engine_instance_id}): _initialize_fixed_knowledge finished. LanceDB table is {'set' if self.lancedb_table else 'None'}.")

    def _format_fixed_knowledge_for_prompt(self, fixed_knowledge_chunks: List[Dict[str, Any]]) -> str:
        """Formats fixed knowledge chunks into a string for the prompt."""
        if not fixed_knowledge_chunks:
            self.logger.debug("FORMAT_FK: No fixed knowledge chunks to format.")
            return "No relevant fixed knowledge found."

        formatted_chunks = []
        for i, chunk_dict in enumerate(fixed_knowledge_chunks):
            text_content = chunk_dict.get('text', 'Error: Text content not found in chunk.')
            source_name = chunk_dict.get('source_name', 'Unknown Source')
            formatted_chunks.append(f"Chunk {i+1} (Source: {source_name}):\n{text_content}")
        
        result_str = "\n\n".join(formatted_chunks)
        self.logger.debug(f"FORMAT_FK: Formatted {len(fixed_knowledge_chunks)} fixed knowledge chunks. Result length: {len(result_str)}")
        return result_str

    def _initialize_adaptive_memory(self) -> None:
        """Initializes the SQLite database for adaptive memory using SQLAlchemy."""
        print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): _initialize_adaptive_memory called.")
        if not self.design.adaptive_memory.enabled:
            print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): Adaptive memory is disabled in the design.")
            self.adaptive_memory_engine = None
            self.db_session_factory = None
            return

        if not self.sqlite_path:
            print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): SQLite path not initialized. Cannot set up adaptive memory.")
            self.adaptive_memory_engine = None
            self.db_session_factory = None
            return

        try:
            # Construct the full SQLite URL
            sqlite_url = f"sqlite:///" + str(self.sqlite_path.resolve()) # Use resolved absolute path
            self.adaptive_memory_engine = create_db_engine_and_tables(sqlite_url)
            self.db_session_factory = get_session_local(self.adaptive_memory_engine)
            print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): Adaptive memory database initialized with factory at {sqlite_url}.")
        except Exception as e:
            print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): Error initializing adaptive memory database: {e}")
            self.adaptive_memory_engine = None
            self.db_session_factory = None

    def _retrieve_adaptive_memory(self, query_text: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieves recent interactions from the adaptive memory."""
        if not self.design.adaptive_memory.enabled or not self.db_session_factory:
            print(f"DEBUG_RETRIEVE_AM (Engine ID: {self.engine_instance_id}): Adaptive memory disabled or session factory not available. Returning empty list.")
            return []

        db_session = self.db_session_factory()
        try:
            actual_limit = limit if limit is not None else self.design.adaptive_memory.retrieval_limit
            print(f"DEBUG_RETRIEVE_AM (Engine ID: {self.engine_instance_id}): Retrieving last {actual_limit} interactions.")
            
            recent_records_orm = (
                db_session.query(InteractionRecordORM)
                .order_by(desc(InteractionRecordORM.timestamp))
                .limit(actual_limit)
                .all()
            )
            
            recent_records_pydantic = [
                InteractionRecordPydantic.model_validate(record) for record in recent_records_orm
            ]
            print(f"DEBUG_RETRIEVE_AM (Engine ID: {self.engine_instance_id}): Retrieved {len(recent_records_pydantic)} records.")
            # Format for prompt - this format might need adjustment based on how it's used in the prompt
            return [
                {
                    "text": f"User: {record.query}\nAI: {record.response}",
                    "query_text": record.query,
                    "response_text": record.response,
                    "timestamp": record.timestamp,
                    "metadata": record.additional_metadata
                }
                for record in recent_records_pydantic
            ]
        except Exception as e:
            print(f"DEBUG_RETRIEVE_AM (Engine ID: {self.engine_instance_id}): Error retrieving adaptive memory: {type(e).__name__} - {e}")
            return []
        finally:
            db_session.close()

    def _retrieve_fixed_knowledge(self, query_text: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Retrieves relevant fixed knowledge chunks from LanceDB based on the query text."""
        print(f"DEBUG_RETRIEVE_FK (Engine ID: {self.engine_instance_id}): _retrieve_fixed_knowledge called. Query: '{query_text[:100]}...', Limit: {limit}")

        if not self.lancedb_table:
            print(f"DEBUG_RETRIEVE_FK (Engine ID: {self.engine_instance_id}): LanceDB table not available. Returning empty list.")
            return []
        
        if not self.ai_model_client:
            print(f"DEBUG_RETRIEVE_FK (Engine ID: {self.engine_instance_id}): AI model client not initialized. Cannot generate query embedding. Returning empty list.")
            return []

        query_embedding = self._embed_content(query_text, task_type="RETRIEVAL_QUERY")
        if not query_embedding:
            print(f"DEBUG_RETRIEVE_FK (Engine ID: {self.engine_instance_id}): Failed to generate query embedding. Returning empty list.")
            return []

        try:
            print(f"DEBUG_RETRIEVE_FK (Engine ID: {self.engine_instance_id}): Searching LanceDB table '{LANCEDB_TABLE_NAME}' with query embedding. Limit: {limit}")
            search_results = self.lancedb_table.search(query_embedding).limit(limit).to_list()
            print(f"DEBUG_RETRIEVE_FK (Engine ID: {self.engine_instance_id}): Found {len(search_results)} results from LanceDB.")
            # Each result is a dict, e.g., {'id': '...', 'text': '...', 'vector': [...], 'source_name': '...', 'metadata': {...}, '_distance': ...}
            return search_results
        except Exception as e:
            print(f"DEBUG_RETRIEVE_FK (Engine ID: {self.engine_instance_id}): ERROR searching LanceDB: {type(e).__name__} - {e}")
            return []

    def process_query(self, query_text: str) -> str:
        """Processes a user query by retrieving context, forming a prompt, and querying the AI model."""
        print(f"DEBUG_PROCESS (Engine ID: {self.engine_instance_id}): process_query received query: '{query_text}'")

        # 1. Retrieve Fixed Knowledge Context
        fixed_knowledge_chunks: List[Dict[str, Any]] = []
        print(f"DEBUG_PROCESS (Engine ID: {self.engine_instance_id}): LanceDB table exists: {self.lancedb_table is not None}")
        if hasattr(self, 'lancedb_table_name'):
            print(f"DEBUG_PROCESS (Engine ID: {self.engine_instance_id}): LanceDB table name: {self.lancedb_table_name}")
        if hasattr(self.lancedb_table, 'name') and self.lancedb_table is not None:
            print(f"DEBUG_PROCESS (Engine ID: {self.engine_instance_id}): LanceDB table object name: {self.lancedb_table.name}")
        
        if self.lancedb_table: # Check if fixed knowledge is usable
            print(f"DEBUG_PROCESS (Engine ID: {self.engine_instance_id}): About to call _retrieve_fixed_knowledge with query: '{query_text[:50]}...'")
            # Use a default limit, e.g., 3. This could be made configurable later.
            fixed_knowledge_chunks = self._retrieve_fixed_knowledge(query_text, limit=3)
            print(f"DEBUG_PROCESS (Engine ID: {self.engine_instance_id}): _retrieve_fixed_knowledge returned {len(fixed_knowledge_chunks)} chunks")
        else:
            print(f"DEBUG_PROCESS (Engine ID: {self.engine_instance_id}): Skipping fixed knowledge retrieval because lancedb_table is None")
        
        fixed_knowledge_context_str = self._format_fixed_knowledge_for_prompt(fixed_knowledge_chunks)
        if fixed_knowledge_context_str == "No relevant fixed knowledge found.":
            # This print statement is for the test assertion
            print(f"DEBUG_PROCESS (Engine ID: {self.engine_instance_id}): No fixed knowledge chunks retrieved or fixed knowledge not enabled/usable.")

        # 2. Retrieve Adaptive Memory Context
        self.logger.debug(f"PROCESS_QUERY_ADAPTIVE_CHECK: Design Adaptive Memory Enabled: {self.design.adaptive_memory.enabled}")
        self.logger.debug(f"PROCESS_QUERY_ADAPTIVE_CHECK: DB Session factory available (is not None): {self.db_session_factory is not None}")
        # The isinstance(MagicMock) check was removed as MagicMock is not available in engine code.
        if self.db_session_factory is not None:
            self.logger.debug(f"PROCESS_QUERY_ADAPTIVE_CHECK: DB Session factory is of type {type(self.db_session_factory)}.")

        adaptive_context_chunks: List[Dict[str, Any]] = []
        if self.design.adaptive_memory.enabled and self.db_session_factory: # Use self.db_session_factory
            self.logger.debug("PROCESS_QUERY_ADAPTIVE_LOGIC: Condition was TRUE. Attempting to retrieve adaptive memory.")
            adaptive_context_chunks = self._retrieve_adaptive_memory(
                query_text=query_text, # Pass query_text
                limit=self.design.adaptive_memory.retrieval_limit
            )
            self.logger.debug(f"PROCESS_QUERY_ADAPTIVE_LOGIC: Retrieved {len(adaptive_context_chunks)} adaptive memory chunks.")
        else:
            self.logger.debug(
                f"PROCESS_QUERY_ADAPTIVE_LOGIC: Condition was FALSE. Adaptive memory retrieval skipped. Enabled: {self.design.adaptive_memory.enabled}, DB Session factory valid: {self.db_session_factory is not None}"
            )
            # adaptive_context_chunks remains empty list
        
        adaptive_memory_context_str = "No conversation history available."
        if adaptive_context_chunks:
            # _retrieve_adaptive_memory returns List[Dict[str, Any]] where each dict has a 'text' key
            # The 'text' is already formatted like "User: ...\nAI: ..."
            # To match existing test logic of newest last / oldest first in prompt, reverse if needed.
            # Let's assume _retrieve_adaptive_memory returns newest first (chronological) or by relevance (semantic).
            # For prompt construction, oldest user/AI turn first is typical.
            formatted_interactions = [
                chunk['text'] 
                for chunk in reversed(adaptive_context_chunks) # Reverse to show oldest first in prompt
            ]
            adaptive_memory_context_str = "\n\n".join(formatted_interactions) # Use double newline for better separation
            self.logger.debug(f"PROCESS_QUERY: Retrieved {len(adaptive_context_chunks)} adaptive memory records. Context length: {len(adaptive_memory_context_str)}")
        else:
            self.logger.debug("PROCESS_QUERY: No adaptive memory records retrieved or adaptive memory disabled.")

        # 3. Construct the full prompt
        system_instruction = self.design.agent_prompts.system_instruction
        full_prompt = f"{system_instruction}\n\n--- Fixed Knowledge Context ---\n{fixed_knowledge_context_str}\n\n--- Conversation History (Adaptive Memory) ---\n{adaptive_memory_context_str}\n\n--- Current Query ---\nUser: {query_text}\nAI:"

        print(f"DEBUG_PROCESS (Engine ID: {self.engine_instance_id}): Constructed full prompt. Length: {len(full_prompt)}. Preview: {full_prompt[:300]}...")

        if not self.ai_model_client:
            print(f"DEBUG_PROCESS (Engine ID: {self.engine_instance_id}): AI model client not initialized. Cannot generate response.")
            return "Error: AI model client not initialized."

        try:
            # Get model name from environment variable if available, otherwise use the one from design
            model_name = os.environ.get('MODEL') or self.design.gemini_config.model_name
            print(f"DEBUG_PROCESS (Engine ID: {self.engine_instance_id}): Sending request to Gemini model '{model_name}'.")
            
            # Configure generation parameters from AMMDesign
            generation_config = genai.types.GenerationConfig(
                temperature=self.design.gemini_config.temperature,
                top_p=self.design.gemini_config.top_p if self.design.gemini_config.top_p is not None else 0.9,
                top_k=self.design.gemini_config.top_k if self.design.gemini_config.top_k is not None else 40,
                max_output_tokens=self.design.gemini_config.max_output_tokens
            )
            
            # Create a GenerativeModel instance with the model name from environment or design
            model = self.ai_model_client.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config
            )
            
            # Generate content using the model
            response = model.generate_content(full_prompt)
            ai_response_text = response.text
            print(f"DEBUG_PROCESS (Engine ID: {self.engine_instance_id}): Received response from Gemini. Length: {len(ai_response_text)}. Preview: {ai_response_text[:100]}...")
        except Exception as e:
            print(f"DEBUG_PROCESS (Engine ID: {self.engine_instance_id}): ERROR during Gemini API call: {type(e).__name__} - {e}")
            ai_response_text = f"Error processing query: {e}"

        # Store interaction in adaptive memory if enabled
        try:
            if self.design.adaptive_memory.enabled and self.db_session_factory:
                interaction_to_store = InteractionRecordPydantic(
                    query=query_text, 
                    response=ai_response_text, 
                    timestamp=datetime.now(timezone.utc), 
                    additional_metadata={"engine_instance_id": self.engine_instance_id, "source": "amm_engine_process_query"}
                )
                record_id = self.add_interaction_record(interaction_to_store)
                if record_id:
                    print(f"DEBUG_PROCESS (Engine ID: {self.engine_instance_id}): Stored interaction in adaptive memory with ID: {record_id}.")
                else:
                    print(f"DEBUG_PROCESS (Engine ID: {self.engine_instance_id}): Failed to store interaction in adaptive memory.")
            else:
                print(f"DEBUG_PROCESS (Engine ID: {self.engine_instance_id}): Adaptive memory disabled or not properly initialized, skipping storage.")
        except Exception as e:
            print(f"DEBUG_PROCESS (Engine ID: {self.engine_instance_id}): Error storing interaction in adaptive memory: {e}")
            # Continue despite error - we don't want to lose the response if memory storage fails

        return ai_response_text

    def add_interaction_record(self, record_data: InteractionRecordPydantic) -> Optional[str]:
        """Adds a new interaction record to the adaptive memory database."""
        print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): add_interaction_record called.")
        if not self.design.adaptive_memory.enabled or not self.db_session_factory:
            print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): Adaptive memory disabled or DB session factory not available. Skipping add.")
            return None

        db_session = self.db_session_factory()
        try:
            # Convert Pydantic model to ORM model instance
            orm_record = InteractionRecordORM(
                session_id=record_data.session_id, 
                user_id=record_data.user_id, 
                query=record_data.query, 
                response=record_data.response,
                timestamp=record_data.timestamp, 
                additional_metadata=record_data.additional_metadata
            )
            db_session.add(orm_record)
            db_session.commit()
            db_session.refresh(orm_record)
            print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): Interaction record {orm_record.id} added successfully.")
            return orm_record.id
        except Exception as e:
            db_session.rollback()
            print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): Error adding interaction record: {type(e).__name__} - {e}")
            # Consider logging the full stack trace for debugging
            import traceback
            traceback.print_exc()
            return None
        finally:
            db_session.close()

    def get_recent_interaction_records(self, limit: int = 10) -> List[InteractionRecordPydantic]:
        """Retrieves a list of the most recent interaction records as Pydantic objects."""
        print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): get_recent_interaction_records called with limit {limit}.")
        if not self.design.adaptive_memory.enabled or not self.db_session_factory:
            print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): Adaptive memory disabled or DB session factory not available. Returning empty list.")
            return []

        db_session = self.db_session_factory()
        try:
            # Retrieve records ordered by timestamp descending to get the most recent ones
            recent_records_orm = (
                db_session.query(InteractionRecordORM)
                .order_by(desc(InteractionRecordORM.timestamp))
                .limit(limit)
                .all()
            )
            # The records are currently most recent first. Reverse to have oldest first if needed by consumer, 
            # or adjust consumer. For now, returning most recent first.
            # To match previous behavior where tests expected oldest first after a reverse:
            recent_records_orm.reverse() # Oldest first

            # Convert ORM objects to Pydantic objects
            pydantic_records = [InteractionRecordPydantic.model_validate(record) for record in recent_records_orm]
            print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): Retrieved {len(pydantic_records)} interaction records.")
            return pydantic_records
        except Exception as e:
            print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): Error retrieving interaction records: {type(e).__name__} - {e}")
            # Log full traceback for detailed debugging
            import traceback
            traceback.print_exc()
            return []
        finally:
            db_session.close()

    def update_interaction_record(self, record_id: str, updates: InteractionRecordUpdatePydantic) -> Optional[InteractionRecordPydantic]:
        """Updates an existing interaction record in the adaptive memory database."""
        print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): update_interaction_record called for ID {record_id}.")
        if not self.design.adaptive_memory.enabled or not self.db_session_factory:
            print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): Adaptive memory disabled or DB session factory not available. Cannot update record.")
            return None

        db_session = self.db_session_factory()
        try:
            record_orm = db_session.query(InteractionRecordORM).filter(InteractionRecordORM.id == record_id).first()
            if not record_orm:
                print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): Record with ID {record_id} not found for update.")
                return None

            update_data = updates.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                # Ensure 'metadata' is correctly handled if it's part of InteractionRecordUpdatePydantic
                # and needs to be merged with existing metadata or replaced.
                # The ORM model uses 'metadata_' (with a trailing underscore).
                if key == "metadata":
                    # Example: deep merge or replace. Current Pydantic model might not have metadata in Update.
                    # If it did, you'd do: record_orm.metadata_ = {**record_orm.metadata_, **value} or record_orm.metadata_ = value
                    # For now, assuming direct attribute setting if 'metadata' field is directly on ORM and in Pydantic Update model.
                    # This part needs alignment with how InteractionRecordUpdatePydantic and InteractionRecordORM handle metadata updates.
                    # Let's assume for now 'metadata' in Pydantic maps to 'metadata_' in ORM.
                    setattr(record_orm, "metadata_", value) 
                else:
                    setattr(record_orm, key, value)
            
            db_session.commit()
            db_session.refresh(record_orm)
            print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): Record {record_id} updated successfully.")
            return InteractionRecordPydantic.model_validate(record_orm)
        except Exception as e:
            db_session.rollback()
            print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): Error updating interaction record {record_id}: {type(e).__name__} - {e}")
            return None
        finally:
            db_session.close()

    def delete_interaction_record(self, record_id: str) -> bool:
        """Deletes an interaction record from the adaptive memory database."""
        print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): delete_interaction_record called for ID {record_id}.")
        if not self.design.adaptive_memory.enabled or not self.db_session_factory:
            print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): Adaptive memory disabled or DB session factory not available. Cannot delete record.")
            return False

        db_session = self.db_session_factory()
        try:
            record_to_delete = db_session.query(InteractionRecordORM).filter(InteractionRecordORM.id == record_id).first()
            if record_to_delete:
                db_session.delete(record_to_delete)
                db_session.commit()
                print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): Record {record_id} deleted successfully.")
                return True
            else:
                print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): Record with ID {record_id} not found for deletion.")
                return False
        except Exception as e:
            db_session.rollback()
            print(f"DEBUG_ADAPTIVE_MEM (Engine ID: {self.engine_instance_id}): Error deleting interaction record {record_id}: {type(e).__name__} - {e}")
            return False
        finally:
            db_session.close()

    # --- Getter methods for commonly accessed design properties --- #
    def get_welcome_message(self) -> str:
        """Returns the welcome message defined in the AMM design."""
        return self.design.agent_prompts.welcome_message

    def get_system_instruction(self) -> str:
        """Returns the system instruction defined in the AMM design."""
        return self.design.agent_prompts.system_instruction

# Example usage (for testing or running directly):
if __name__ == '__main__':
    # Example usage code here
    pass
