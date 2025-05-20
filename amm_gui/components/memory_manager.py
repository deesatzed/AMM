"""
Adaptive Memory Manager Component
-------------------------------
Component for configuring adaptive memory settings in the AMM Design GUI.
"""
import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path to import utils
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

def memory_manager(amm_design):
    """
    Component for configuring adaptive memory settings in the AMM Design GUI.
    
    Args:
        amm_design: The current AMM design dictionary
    
    Returns:
        Updated AMM design dictionary
    """
    st.header("Adaptive Memory Configuration")
    
    # Memory configuration descriptions
    st.info("""
    **Adaptive Memory** allows the AMM to remember past interactions and use them as context for future responses.
    
    - **Enable/Disable**: Turn adaptive memory on or off
    - **Retrieval Limit**: How many past interactions to include in context
    - **Retention Policy**: How long to keep interaction records
    
    See the Knowledge & Memory Guide for detailed recommendations on memory configuration.
    """)
    
    # Create columns for layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Enable/disable toggle
        amm_design["adaptive_memory"]["enabled"] = st.toggle(
            "Enable Adaptive Memory",
            value=amm_design["adaptive_memory"].get("enabled", True),
            help="Enable or disable adaptive memory functionality",
            key="memory_enabled_toggle"
        )
    
    with col2:
        if amm_design["adaptive_memory"]["enabled"]:
            st.success("✓ Adaptive Memory is enabled")
            st.markdown("""
            The AMM will remember past interactions and use them as context for future responses.
            This is useful for maintaining conversation continuity and personalization.
            """)
        else:
            st.warning("⚠ Adaptive Memory is disabled")
            st.markdown("""
            The AMM will not remember past interactions. Each query will be processed independently.
            This may be preferred for stateless applications or when privacy is a concern.
            """)
    
    # Only show configuration if memory is enabled
    if amm_design["adaptive_memory"]["enabled"]:
        st.subheader("Memory Configuration")
        
        # Create tabs for different memory configuration aspects
        memory_tabs = st.tabs(["Retrieval Settings", "Retention Policy", "Advanced (Coming Soon)"])
        
        # Retrieval Settings tab
        with memory_tabs[0]:
            st.markdown("**Configure how past interactions are retrieved and used**")
            
            # Retrieval limit with guidance
            retrieval_limit = st.slider(
                "Retrieval Limit",
                min_value=1,
                max_value=20,
                value=amm_design["adaptive_memory"].get("retrieval_limit", 5),
                help="Maximum number of past interactions to include in context",
                key="retrieval_limit_slider"
            )
            
            amm_design["adaptive_memory"]["retrieval_limit"] = retrieval_limit
            
            # Guidance based on selected value
            if retrieval_limit <= 3:
                st.info("**Light Context**: Only the most recent interactions will be included. Good for simple, short conversations.")
            elif retrieval_limit <= 8:
                st.success("**Balanced Context**: A moderate amount of conversation history. Suitable for most use cases.")
            else:
                st.warning("**Heavy Context**: Extensive conversation history will be included. May consume more tokens but provides deeper context.")
            
            # Example of context usage
            st.markdown("### Context Usage Example")
            st.markdown(f"""
            With a retrieval limit of **{retrieval_limit}**, if a user has had 10 interactions with the AMM:
            - The AMM will include the **{retrieval_limit} most relevant** past interactions in the context
            - This helps the AMM understand the conversation history and provide more relevant responses
            - Higher values provide more context but use more tokens in the prompt
            """)
        
        # Retention Policy tab
        with memory_tabs[1]:
            st.markdown("**Configure how long interaction records are kept**")
            
            # Retention policy with guidance
            retention_days = st.number_input(
                "Retention Policy (days)",
                min_value=1,
                max_value=365,
                value=amm_design["adaptive_memory"].get("retention_policy_days", 30),
                help="Number of days to retain interaction history",
                key="retention_days_input"
            )
            
            amm_design["adaptive_memory"]["retention_policy_days"] = retention_days
            
            # Guidance based on selected value
            if retention_days <= 7:
                st.info("**Short-term Memory**: Records will be kept for a short period. Good for temporary or session-based interactions.")
            elif retention_days <= 30:
                st.success("**Standard Retention**: Records will be kept for a moderate period. Suitable for most use cases.")
            else:
                st.warning("**Long-term Memory**: Records will be kept for an extended period. Good for ongoing relationships but consider privacy implications.")
            
            # Example of retention policy
            st.markdown("### Retention Policy Example")
            st.markdown(f"""
            With a retention policy of **{retention_days} days**:
            - Interaction records older than {retention_days} days will be automatically deleted
            - This helps manage database size and respect privacy considerations
            - Longer retention periods allow for more persistent relationships with users
            """)
        
        # Advanced tab (coming soon)
        with memory_tabs[2]:
            st.markdown("**Advanced memory configuration options**")
            st.info("Advanced memory configuration options will be available in a future update. Stay tuned!")
            
            # Placeholder UI
            st.selectbox(
                "Memory Retrieval Strategy",
                ["Recency", "Relevance", "Hybrid"],
                disabled=True,
                help="How to select which past interactions to include in context",
                key="retrieval_strategy_select"
            )
            
            st.slider(
                "Recency Weight",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.1,
                disabled=True,
                help="Weight given to recency vs. relevance in hybrid retrieval",
                key="recency_weight_slider"
            )
            
            st.checkbox(
                "Enable Memory Summarization",
                disabled=True,
                help="Summarize older interactions to save context space",
                key="memory_summarization_checkbox"
            )
    
    # Memory usage recommendations
    st.subheader("Recommended Memory Settings")
    
    # Create columns for different use cases
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Simple Q&A Bot**")
        st.markdown("""
        - **Enabled**: Optional
        - **Retrieval Limit**: 2-3
        - **Retention**: 7 days
        """)
        if st.button("Apply Q&A Settings", key="apply_qa_settings"):
            amm_design["adaptive_memory"]["enabled"] = True
            amm_design["adaptive_memory"]["retrieval_limit"] = 3
            amm_design["adaptive_memory"]["retention_policy_days"] = 7
            st.success("Applied Q&A memory settings")
            st.rerun()
    
    with col2:
        st.markdown("**Conversational Assistant**")
        st.markdown("""
        - **Enabled**: Yes
        - **Retrieval Limit**: 5-8
        - **Retention**: 30 days
        """)
        if st.button("Apply Conversational Settings", key="apply_conversational_settings"):
            amm_design["adaptive_memory"]["enabled"] = True
            amm_design["adaptive_memory"]["retrieval_limit"] = 6
            amm_design["adaptive_memory"]["retention_policy_days"] = 30
            st.success("Applied conversational memory settings")
            st.rerun()
    
    with col3:
        st.markdown("**Personal Assistant**")
        st.markdown("""
        - **Enabled**: Yes
        - **Retrieval Limit**: 8-12
        - **Retention**: 90 days
        """)
        if st.button("Apply Personal Assistant Settings", key="apply_personal_assistant_settings"):
            amm_design["adaptive_memory"]["enabled"] = True
            amm_design["adaptive_memory"]["retrieval_limit"] = 10
            amm_design["adaptive_memory"]["retention_policy_days"] = 90
            st.success("Applied personal assistant memory settings")
            st.rerun()
    
    return amm_design
