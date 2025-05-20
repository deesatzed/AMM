"""
Knowledge Source Manager Component
---------------------------------
Component for managing knowledge sources in the AMM Design GUI.
"""
import streamlit as st
from pathlib import Path
import os
import sys
import uuid
import shutil

# Add parent directory to path to import utils
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

from amm_gui.utils.file_handling import is_valid_knowledge_file, get_file_preview

def knowledge_source_manager(amm_design):
    """
    Component for managing knowledge sources in the AMM Design GUI.
    
    Args:
        amm_design: The current AMM design dictionary
    
    Returns:
        Updated AMM design dictionary
    """
    st.header("Knowledge Sources")
    
    # Knowledge source type descriptions
    st.info("""
    **Knowledge Source Types:**
    
    - **File**: Text or PDF files containing reference material, documentation, or specialized knowledge
    - **Text**: Directly entered text for rules, guidelines, or specific instructions
    - **URL** *(coming soon)*: Web content from specified URLs
    - **Database** *(coming soon)*: Structured data from database connections
    
    See the Knowledge & Memory Guide and PDF Knowledge Guide for detailed recommendations on when to use each type.
    """)
    
    # Add new knowledge source
    st.subheader("Add Knowledge Source")
    
    # Create tabs for different knowledge source types
    ks_tabs = st.tabs(["File", "Text", "URL (Coming Soon)", "Database (Coming Soon)"])
    
    # File tab
    with ks_tabs[0]:
        st.markdown("**Upload a file to use as a knowledge source**")
        st.markdown("*Best for: Documentation, manuals, articles, reports, and other structured information*")
        
        # Info about PDF support
        with st.expander("Using PDF Files"):
            st.markdown("""
            **PDF Knowledge Sources** are now supported! You can upload PDF documents to use as knowledge sources.
            
            The system will:
            - Extract text from both text-based and scanned PDFs
            - Split the content into optimal chunks
            - Use OCR for scanned documents (if available)
            
            See the [PDF Knowledge Guide](../docs/pdf_knowledge_guide.md) for more details.
            """)
        
        uploaded_file = st.file_uploader(
            "Select File",
            type=["txt", "md", "pdf"],
            help="Upload a text or PDF file to use as a knowledge source"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            ks_id = st.text_input(
                "Knowledge Source ID", 
                value=f"file_{len([ks for ks in amm_design['knowledge_sources'] if ks['type'] == 'file'])}",
                key="file_ks_id_input"
            )
        
        with col2:
            ks_description = st.text_input(
                "Description",
                value="",
                help="Brief description of this knowledge source",
                key="file_ks_description_input"
            )
            
        if uploaded_file is not None:
            # Create temp directory if it doesn't exist
            temp_dir = parent_dir / "temp"
            temp_dir.mkdir(exist_ok=True)
            
            # Generate a unique filename
            unique_filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
            file_path = temp_dir / unique_filename
            
            # Save the file
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Show file preview
            st.markdown("**File Preview:**")
            success, content = get_file_preview(str(file_path), max_chars=500)
            if success:
                st.text_area("Content", value=content, height=150, disabled=True)
            else:
                st.warning(content)
            
            if st.button("Add File Knowledge Source"):
                # Validate ID
                if not ks_id:
                    st.error("Please provide a Knowledge Source ID")
                else:
                    # Check for duplicate ID
                    if any(ks["id"] == ks_id for ks in amm_design["knowledge_sources"]):
                        st.error(f"Knowledge Source ID '{ks_id}' already exists. Please choose a different ID.")
                    else:
                        # Add the knowledge source
                        new_ks = {
                            "id": ks_id,
                            "name": ks_description or f"File: {uploaded_file.name}",
                            "type": "file",
                            "path": str(file_path),
                            "description": ks_description or f"File: {uploaded_file.name}"
                        }
                        amm_design["knowledge_sources"].append(new_ks)
                        st.success(f"Added file knowledge source: {uploaded_file.name}")
                        st.rerun()
    
    # Text tab
    with ks_tabs[1]:
        st.markdown("**Enter text directly as a knowledge source**")
        st.markdown("*Best for: Rules, guidelines, specific instructions, or small pieces of focused information*")
        
        col1, col2 = st.columns(2)
        with col1:
            ks_id = st.text_input(
                "Knowledge Source ID", 
                value=f"text_{len([ks for ks in amm_design['knowledge_sources'] if ks['type'] == 'text'])}",
                key="text_ks_id_input"
            )
        
        with col2:
            ks_description = st.text_input(
                "Description",
                value="",
                help="Brief description of this knowledge source",
                key="text_ks_description_input"
            )
        
        ks_text = st.text_area(
            "Knowledge Text", 
            height=200,
            help="Enter the text content for this knowledge source"
        )
        
        if st.button("Add Text Knowledge Source"):
            # Validate ID and content
            if not ks_id:
                st.error("Please provide a Knowledge Source ID")
            elif not ks_text:
                st.error("Please provide some text content")
            else:
                # Check for duplicate ID
                if any(ks["id"] == ks_id for ks in amm_design["knowledge_sources"]):
                    st.error(f"Knowledge Source ID '{ks_id}' already exists. Please choose a different ID.")
                else:
                    # Add the knowledge source
                    new_ks = {
                        "id": ks_id,
                        "name": ks_description or f"Text Source {ks_id}",
                        "type": "text",
                        "content": ks_text,
                        "description": ks_description or f"Text: {ks_text[:50]}..." if len(ks_text) > 50 else f"Text: {ks_text}"
                    }
                    amm_design["knowledge_sources"].append(new_ks)
                    st.success("Added text knowledge source")
                    st.rerun()
    
    # URL tab (coming soon)
    with ks_tabs[2]:
        st.markdown("**Add a URL as a knowledge source**")
        st.markdown("*Best for: External, frequently updated information like API docs, specifications, current data*")
        st.info("This feature is coming soon. Stay tuned!")
        
        # Placeholder UI
        st.text_input("URL", disabled=True, key="url_input")
        st.text_input("Knowledge Source ID", disabled=True, key="url_ks_id")
        st.text_input("Description", disabled=True, key="url_description")
        st.button("Add URL Knowledge Source", disabled=True, key="add_url_ks")
    
    # Database tab (coming soon)
    with ks_tabs[3]:
        st.markdown("**Connect to a database as a knowledge source**")
        st.markdown("*Best for: Highly structured, queryable information like product catalogs, user data, statistics*")
        st.info("This feature is coming soon. Stay tuned!")
        
        # Placeholder UI
        st.text_input("Connection String", disabled=True, key="db_connection_string")
        st.text_input("Query", disabled=True, key="db_query")
        st.text_input("Knowledge Source ID", disabled=True, key="db_ks_id")
        st.text_input("Description", disabled=True, key="db_description")
        st.button("Add Database Knowledge Source", disabled=True, key="add_db_ks")
    
    # Display existing knowledge sources
    st.subheader("Current Knowledge Sources")
    
    if not amm_design["knowledge_sources"]:
        st.info("No knowledge sources added yet.")
    else:
        # Group knowledge sources by type
        file_sources = [ks for ks in amm_design["knowledge_sources"] if ks["type"] == "file"]
        text_sources = [ks for ks in amm_design["knowledge_sources"] if ks["type"] == "text"]
        other_sources = [ks for ks in amm_design["knowledge_sources"] if ks["type"] not in ["file", "text"]]
        
        # Display file sources
        if file_sources:
            st.markdown("**File Knowledge Sources:**")
            for i, ks in enumerate(file_sources):
                with st.expander(f"{ks['id']} - {Path(ks['path']).name}"):
                    st.write(f"**Type:** File")
                    st.write(f"**Path:** {ks['path']}")
                    st.write(f"**Description:** {ks.get('description', 'No description')}")
                    
                    # Preview button
                    if st.button(f"Preview Content", key=f"preview_file_{i}"):
                        success, content = get_file_preview(ks['path'], max_chars=1000)
                        if success:
                            st.text_area("Content Preview", value=content, height=200, disabled=True)
                        else:
                            st.warning(content)
                    
                    # Remove button
                    if st.button(f"Remove", key=f"remove_file_{i}"):
                        amm_design["knowledge_sources"].remove(ks)
                        st.success(f"Removed knowledge source: {ks['id']}")
                        st.rerun()
        
        # Display text sources
        if text_sources:
            st.markdown("**Text Knowledge Sources:**")
            for i, ks in enumerate(text_sources):
                with st.expander(f"{ks['id']} - {ks.get('description', 'Text Source')}"):
                    st.write(f"**Type:** Text")
                    st.write(f"**Description:** {ks.get('description', 'No description')}")
                    st.text_area(
                        "Content", 
                        value=ks['content'], 
                        height=150, 
                        disabled=True,
                        key=f"text_content_{i}"
                    )
                    
                    # Remove button
                    if st.button(f"Remove", key=f"remove_text_{i}"):
                        amm_design["knowledge_sources"].remove(ks)
                        st.success(f"Removed knowledge source: {ks['id']}")
                        st.rerun()
        
        # Display other sources
        if other_sources:
            st.markdown("**Other Knowledge Sources:**")
            for i, ks in enumerate(other_sources):
                with st.expander(f"{ks['id']} - {ks['type']}"):
                    st.write(f"**Type:** {ks['type']}")
                    st.write(f"**Description:** {ks.get('description', 'No description')}")
                    
                    # Display other properties
                    for key, value in ks.items():
                        if key not in ["id", "type", "description"]:
                            st.write(f"**{key}:** {value}")
                    
                    # Remove button
                    if st.button(f"Remove", key=f"remove_other_{i}"):
                        amm_design["knowledge_sources"].remove(ks)
                        st.success(f"Removed knowledge source: {ks['id']}")
                        st.rerun()
    
    return amm_design
