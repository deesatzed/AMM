# AMM Memory Components: Technical Guide

This guide provides detailed technical information about the three memory components in the AMM system: Fixed Knowledge (Agno Knowledge), Dynamic Context (Agno Context), and Adaptive Memory (Gemini Cache).

## 1. Fixed Knowledge (Agno Knowledge)

### Technical Implementation

Fixed Knowledge is implemented using LanceDB, a vector database that enables semantic search:

```python
# In AMMEngine._initialize_fixed_knowledge
def _initialize_fixed_knowledge(self) -> None:
    """Initializes the fixed knowledge base (LanceDB)."""
    if not self.lancedb_path:
        self.logger.warning("No LanceDB path available. Fixed knowledge will be disabled.")
        return
    
    try:
        # Create LanceDB connection
        self.lancedb_connection = lancedb.connect(self.lancedb_path)
        
        # Create or open the table
        if LANCEDB_TABLE_NAME in self.lancedb_connection.table_names():
            self.lancedb_table = self.lancedb_connection.open_table(LANCEDB_TABLE_NAME)
            self.logger.debug(f"Opened existing LanceDB table '{LANCEDB_TABLE_NAME}'.")
        else:
            # Process knowledge sources to create the table
            self._process_knowledge_sources()
    except Exception as e:
        self.logger.error(f"Error initializing fixed knowledge: {type(e).__name__} - {e}")
```

### Knowledge Source Processing

Knowledge sources are processed during initialization:

1. Files are read and chunked:
   - Text files are processed directly
   - PDF files are processed using the PDF processor (supports both text-based and scanned PDFs)
   - PDF files are automatically chunked into semantically meaningful sections
2. Text is embedded using the Gemini embedding model
3. Embeddings and metadata are stored in LanceDB

### Retrieval Mechanism

Fixed knowledge is retrieved using semantic search:

```python
# In AMMEngine._retrieve_fixed_knowledge
def _retrieve_fixed_knowledge(self, query_text: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Retrieves relevant fixed knowledge chunks from LanceDB based on the query text."""
    # Generate embedding for the query
    query_embedding = self._embed_content(query_text, task_type="RETRIEVAL_QUERY")
    
    # Search LanceDB with the query embedding
    search_results = self.lancedb_table.search(query_embedding).limit(limit).to_list()
    
    return search_results
```

### Optimization Strategies

1. **Chunking Strategy**: Divide knowledge into semantic units (paragraphs, sections) rather than arbitrary chunks
2. **PDF Processing**: Use the PDF processor for automatic chunking and OCR for scanned documents
3. **Embedding Quality**: Use high-quality embeddings with appropriate task types
4. **Metadata Enrichment**: Add metadata to improve filtering and retrieval
5. **Index Optimization**: Configure LanceDB index parameters for your specific use case
6. **File Type Selection**: Choose appropriate file types (text for simple content, PDF for complex documents)

## 2. Dynamic Context (Agno Context)

### Technical Implementation

Dynamic context is implemented through external files or direct text that can be updated programmatically:

```python
# Example of dynamic context injection in news_agent_simulator.py
def update_headlines(self, headlines_file: str, abstracts: Dict[str, str]) -> None:
    """Update the headlines file and abstracts with new content."""
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    
    # Update headlines file
    headlines_content = f"# Top Tech Headlines - {current_date}\n\n"
    for i, (headline, abstract_file) in enumerate(abstracts.items(), 1):
        headlines_content += f"{i}. {headline}\n"
    
    with open(headlines_file, "w") as f:
        f.write(headlines_content)
    
    # Update abstract files
    for headline, abstract in abstracts.items():
        abstract_file = f"knowledge_files/headline{list(abstracts.keys()).index(headline)+1}_abstract.txt"
        with open(abstract_file, "w") as f:
            f.write(f"# {headline}\n\n{abstract}")
```

### Context Integration

Dynamic context is integrated into the AMM through knowledge sources that are frequently updated:

1. Files are updated externally (by scripts, APIs, or manual processes)
2. The AMM reads these files during query processing
3. The content is embedded and retrieved like fixed knowledge

### Optimization Strategies

1. **Update Frequency**: Determine appropriate update intervals based on data volatility
2. **Caching Strategy**: Cache embeddings for frequently accessed but infrequently changed context
3. **Isolation**: Keep dynamic context separate from fixed knowledge for easier updates
4. **Versioning**: Consider versioning dynamic context for reproducibility

## 3. Adaptive Memory (Gemini Cache)

### Technical Implementation

Adaptive Memory is implemented using SQLite with SQLAlchemy ORM:

```python
# In AMMEngine._initialize_adaptive_memory
def _initialize_adaptive_memory(self) -> None:
    """Initializes the SQLite database for adaptive memory using SQLAlchemy."""
    if not self.design.adaptive_memory.enabled:
        self.logger.debug("Adaptive memory is disabled in the design. Skipping initialization.")
        return
    
    if not self.sqlite_path:
        self.logger.warning("No SQLite path available. Adaptive memory will be disabled.")
        return
    
    try:
        # Create the database engine and tables
        self.adaptive_memory_engine, self.db_session_factory = create_db_engine_and_tables(
            f"sqlite:///{self.sqlite_path}"
        )
        self.logger.debug(f"Adaptive memory database initialized with factory at sqlite:///{self.sqlite_path}.")
    except Exception as e:
        self.logger.error(f"Error initializing adaptive memory: {type(e).__name__} - {e}")
        self.adaptive_memory_engine = None
        self.db_session_factory = None
```

### Record Management

Interaction records are stored and retrieved using SQLAlchemy:

```python
# In AMMEngine.add_interaction_record
def add_interaction_record(self, record_data: InteractionRecordPydantic) -> Optional[str]:
    """Adds a new interaction record to the adaptive memory database."""
    if not self.design.adaptive_memory.enabled or not self.db_session_factory:
        self.logger.debug("Adaptive memory disabled or DB session factory not available. Cannot add record.")
        return None
    
    db_session = self.db_session_factory()
    try:
        # Convert Pydantic model to ORM model
        record_orm = InteractionRecordORM(
            query=record_data.query,
            response=record_data.response,
            timestamp=record_data.timestamp,
            metadata_=record_data.additional_metadata
        )
        
        # Add and commit to database
        db_session.add(record_orm)
        db_session.commit()
        db_session.refresh(record_orm)
        
        return str(record_orm.id)
    except Exception as e:
        db_session.rollback()
        self.logger.error(f"Error adding interaction record: {type(e).__name__} - {e}")
        return None
    finally:
        db_session.close()
```

### Retrieval Mechanism

Recent or relevant interactions are retrieved based on configuration:

```python
# In AMMEngine._retrieve_adaptive_memory
def _retrieve_adaptive_memory(self, query_text: str, limit: Optional[int] = None) -> List[InteractionRecordPydantic]:
    """Retrieves recent interactions from the adaptive memory."""
    if not self.design.adaptive_memory.enabled or not self.db_session_factory:
        self.logger.debug("Adaptive memory disabled or DB session factory not available. Cannot retrieve records.")
        return []
    
    # Use the configured limit if none is provided
    if limit is None:
        limit = self.design.adaptive_memory.retrieval_limit
    
    db_session = self.db_session_factory()
    try:
        # Query for the most recent records
        records = db_session.query(InteractionRecordORM).order_by(
            desc(InteractionRecordORM.timestamp)
        ).limit(limit).all()
        
        # Convert ORM models to Pydantic models
        return [InteractionRecordPydantic.model_validate(record) for record in records]
    except Exception as e:
        self.logger.error(f"Error retrieving adaptive memory: {type(e).__name__} - {e}")
        return []
    finally:
        db_session.close()
```

### Optimization Strategies

1. **Retention Policy**: Implement automatic pruning of old records based on `retention_policy_days`
2. **Metadata Enrichment**: Add metadata to records for better filtering and retrieval
3. **Semantic Retrieval**: Consider implementing semantic search for adaptive memory
4. **Privacy Controls**: Add mechanisms for users to control or delete their memory

## Integration Patterns

### 1. Sequential Integration

Process each memory component in sequence:

```
Fixed Knowledge → Dynamic Context → Adaptive Memory → Generate Response
```

This approach is simple but may not optimize for relevance across components.

### 2. Parallel Integration with Ranking

Retrieve from all components in parallel, then rank and combine:

```
┌─ Fixed Knowledge ─┐
│                   │
Query ─ Dynamic Context ─→ Rank & Combine → Generate Response
│                   │
└─ Adaptive Memory ─┘
```

This approach can prioritize the most relevant information regardless of source.

### 3. Hierarchical Integration

Use a tiered approach where each component has a specific role:

```
Query → Adaptive Memory (personalization)
      → Dynamic Context (current situation)
      → Fixed Knowledge (factual foundation)
      → Generate Response
```

This approach respects the different purposes of each component.

## Best Practices for AMM Designers

1. **Component Selection**: Not all AMMs need all three components. Choose based on your use case.
2. **Balance**: Find the right balance between fixed knowledge (consistency) and adaptive memory (personalization).
3. **Update Cycles**: Define clear update cycles for dynamic context based on data volatility.
4. **Memory Limits**: Set appropriate retrieval limits to avoid context overload.
5. **Error Handling**: Implement robust error handling for each component.
6. **Testing**: Test each component individually and in combination.
7. **Monitoring**: Implement logging and monitoring to track component performance.

## Advanced Techniques

1. **Cross-Component Retrieval**: Use information from one component to guide retrieval in another.
2. **Weighted Integration**: Assign weights to different components based on query type.
3. **Feedback Loops**: Use user feedback to improve retrieval mechanisms.
4. **Contextual Pruning**: Dynamically adjust retrieval limits based on query complexity.
5. **Multi-Modal Memory**: Extend memory components to handle images, audio, or other modalities.
6. **PDF Knowledge Enhancement**: Use PDF knowledge sources for complex documents, academic papers, and manuals.
7. **OCR Integration**: Process scanned documents with OCR for knowledge extraction.

## Troubleshooting

### Fixed Knowledge Issues

- **No results**: Check embedding quality and LanceDB connection
- **Irrelevant results**: Adjust chunking strategy or embedding parameters
- **Slow retrieval**: Optimize LanceDB index or reduce vector dimensions
- **PDF extraction issues**: Verify PDF dependencies are installed and PDF processor is working
- **OCR quality problems**: Check Tesseract installation and image quality in scanned PDFs

### Dynamic Context Issues

- **Outdated information**: Check update mechanisms and frequency
- **Missing context**: Verify file paths and read permissions
- **Integration failures**: Check file format and encoding

### Adaptive Memory Issues

- **Database errors**: Check SQLite path and permissions
- **Missing records**: Verify `add_interaction_record` is called after responses
- **Performance issues**: Implement indexing or pruning for large databases
