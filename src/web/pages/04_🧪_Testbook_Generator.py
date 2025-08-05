"""
Testbook Generator page for the Universal Testbook Generator.
Provides interface for generating comprehensive manual test procedures.
"""

import streamlit as st
from datetime import datetime
from loguru import logger

# Import core components
from ...core.testbook_generator import TestbookGenerator
from ...core.vector_database import VectorDatabase
from ...utils.excel_exporter import ExcelExporter
from ...models.testbook_models import TestCategory, Priority

# Page configuration
st.set_page_config(
    page_title="Testbook Generator - Universal Testbook Generator",
    page_icon="🧪",
    layout="wide"
)

def main():
    """Main function for testbook generator page."""
    
    st.title("🧪 Testbook Generator")
    st.markdown("Generate comprehensive manual test procedures from your documentation")
    
    # Initialize session state
    if 'testbooks' not in st.session_state:
        st.session_state.testbooks = {}
    if 'testbook_generator' not in st.session_state:
        st.session_state.testbook_generator = None
    
    # Check if documents are available
    if 'documents' not in st.session_state or not st.session_state.documents:
        st.warning("⚠️ No documents uploaded yet. Please upload a document first.")
        if st.button("📄 Go to Document Upload"):
            st.switch_page("pages/01_📄_Document_Upload.py")
        return
    
    # Initialize testbook generator
    if st.session_state.testbook_generator is None:
        with st.spinner("Initializing testbook generator..."):
            try:
                st.session_state.testbook_generator = TestbookGenerator()
                logger.info("Testbook generator initialized successfully")
            except Exception as e:
                st.error(f"❌ Error initializing testbook generator: {str(e)}")
                return
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🛠️ Generate Testbook", "📋 Generated Testbooks", "📊 Testbook Analysis"])
    
    with tab1:
        generation_interface()
    
    with tab2:
        testbook_management_interface()
    
    with tab3:
        testbook_analysis_interface()

def generation_interface():
    """Interface for generating new testbooks."""
    
    st.markdown("### 🛠️ Generate New Testbook")
    
    # Document selection
    document_options = {doc.filename: doc_id for doc_id, doc in st.session_state.documents.items()}
    selected_document_name = st.selectbox(
        "Select document to generate testbook from:",
        options=list(document_options.keys()),
        index=0 if document_options else None,
        key="generation_document"
    )
    
    if not selected_document_name:
        st.warning("No document selected")
        return
    
    selected_doc_id = document_options[selected_document_name]
    selected_document = st.session_state.documents[selected_doc_id]
    
    # Show document information
    with st.expander("📄 Document Information", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Features", len(selected_document.features))
        
        with col2:
            st.metric("Requirements", len(selected_document.requirements))
        
        with col3:
            st.metric("Workflows", len(selected_document.workflows))
        
        with col4:
            st.metric("Text Chunks", len(selected_document.chunks))
    
    # Feature selection
    st.markdown("#### 🎯 Feature Selection")
    
    if not selected_document.features:
        st.warning("No features found in the selected document. The generator will use general content analysis.")
        selected_features = []
    else:
        # Display features for selection
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_features = []
            
            if st.checkbox("Select all features", key="select_all_features"):
                selected_features = [f.id for f in selected_document.features]
            else:
                for feature in selected_document.features:
                    if st.checkbox(
                        f"**{feature.name}** - {feature.description[:100]}...",
                        key=f"feature_{feature.id}"
                    ):
                        selected_features.append(feature.id)
        
        with col2:
            st.info(f"""
            **Features Selected:** {len(selected_features)}
            
            **Total Available:** {len(selected_document.features)}
            
            Select features you want to create test procedures for.
            """)
    
    # Generation settings
    st.markdown("#### ⚙️ Generation Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        testbook_name = st.text_input(
            "Testbook Name",
            value=f"Manual Testbook - {selected_document.title or selected_document.filename}",
            key="testbook_name"
        )
    
    with col2:
        include_security_tests = st.checkbox("Include Security Tests", value=True)
        include_performance_tests = st.checkbox("Include Performance Tests", value=True)
    
    with col3:
        include_integration_tests = st.checkbox("Include Integration Tests", value=True)
        detailed_evidence = st.checkbox("Detailed Evidence Collection", value=True)
    
    # Advanced settings
    with st.expander("🔧 Advanced Settings", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            max_procedures_per_feature = st.number_input(
                "Max Procedures per Feature",
                min_value=1,
                max_value=10,
                value=3,
                help="Maximum number of test procedures to generate per feature"
            )
        
        with col2:
            context_chunks = st.number_input(
                "Context Chunks",
                min_value=1,
                max_value=10,
                value=5,
                help="Number of document chunks to use as context"
            )
    
    # Generate button
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Generate Testbook", type="primary", use_container_width=True, key="generate_button"):
            generate_testbook(
                selected_document,
                selected_features,
                testbook_name,
                {
                    'include_security_tests': include_security_tests,
                    'include_performance_tests': include_performance_tests, 
                    'include_integration_tests': include_integration_tests,
                    'detailed_evidence': detailed_evidence,
                    'max_procedures_per_feature': max_procedures_per_feature,
                    'context_chunks': context_chunks
                }
            )

def generate_testbook(document, selected_features, testbook_name, settings):
    """Generate a testbook with the given parameters."""
    
    try:
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Prepare context
        status_text.text("Preparing context and features...")
        progress_bar.progress(20)
        
        # Get additional context chunks if needed
        context_chunks = None
        if settings['context_chunks'] > 0:
            # Use first few chunks as general context
            context_chunks = document.chunks[:settings['context_chunks']]
        
        # Step 2: Generate testbook
        status_text.text("Generating test procedures with AI...")
        progress_bar.progress(40)
        
        testbook = st.session_state.testbook_generator.generate_manual_testbook(
            document=document,
            selected_features=selected_features if selected_features else None,
            context_chunks=context_chunks
        )
        
        # Step 3: Update testbook name and metadata
        status_text.text("Finalizing testbook...")
        progress_bar.progress(80)
        
        testbook.name = testbook_name
        testbook.metadata.update({
            'generation_settings': settings,
            'selected_features_count': len(selected_features) if selected_features else 0,
            'source_document_name': document.filename
        })
        
        # Step 4: Store testbook
        st.session_state.testbooks[testbook.id] = testbook
        
        # Complete
        progress_bar.progress(100)
        status_text.text("✅ Testbook generated successfully!")
        
        # Show results
        st.success("🎉 Testbook generation completed!")
        
        # Display summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Procedures", len(testbook.get_all_procedures()))
        
        with col2:
            st.metric("Functional Tests", len(testbook.functional_procedures))
        
        with col3:
            st.metric("Security Tests", len(testbook.security_procedures))
        
        with col4:
            st.metric("Estimated Time", f"{testbook.total_estimated_time} min")
        
        # Show sample procedures
        if testbook.get_all_procedures():
            st.markdown("#### 📋 Sample Test Procedures")
            
            sample_procedures = testbook.get_all_procedures()[:3]  # Show first 3
            
            for i, procedure in enumerate(sample_procedures, 1):
                with st.expander(f"Test {i}: {procedure.title}", expanded=False):
                    st.write(f"**Category:** {procedure.category.value.title()}")
                    st.write(f"**Priority:** {procedure.priority.value.title()}")
                    st.write(f"**Description:** {procedure.description}")
                    
                    if procedure.test_steps:
                        st.write("**Test Steps:**")
                        for j, step in enumerate(procedure.test_steps[:3], 1):
                            st.write(f"{j}. {step.action}")
                            st.write(f"   *Expected: {step.expected_behavior}*")
        
        # Navigation buttons
        st.markdown("### Next Steps")
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("📊 Review Testbook", use_container_width=True):
                st.switch_page("pages/05_📊_Results_Review.py")
        
        with col_b:
            if st.button("📤 Export to Excel", use_container_width=True):
                export_testbook_to_excel(testbook)
        
        with col_c:
            if st.button("🔄 Compare with Docs", use_container_width=True):
                st.switch_page("pages/06_🔄_Documentation_Comparison.py")
        
    except Exception as e:
        logger.error(f"Error generating testbook: {str(e)}")
        st.error(f"❌ Error generating testbook: {str(e)}")

def testbook_management_interface():
    """Interface for managing generated testbooks."""
    
    st.markdown("### 📋 Generated Testbooks")
    
    if not st.session_state.testbooks:
        st.info("No testbooks generated yet. Use the 'Generate Testbook' tab to create your first testbook.")
        return
    
    # Display testbooks
    for testbook_id, testbook in st.session_state.testbooks.items():
        with st.expander(f"📚 {testbook.name}", expanded=True):
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**Description:** {testbook.description}")
                st.write(f"**Version:** {testbook.version}")
                st.write(f"**Created:** {testbook.created_at.strftime('%Y-%m-%d %H:%M')}")
                
                # Source information
                if testbook.source_document_id:
                    source_doc = st.session_state.documents.get(testbook.source_document_id)
                    if source_doc:
                        st.write(f"**Source:** {source_doc.filename}")
            
            with col2:
                # Metrics
                st.metric("Total Procedures", len(testbook.get_all_procedures()))
                st.metric("Estimated Time", f"{testbook.total_estimated_time} min")
            
            with col3:
                # Category breakdown
                st.write("**Test Categories:**")
                st.write(f"• Functional: {len(testbook.functional_procedures)}")
                st.write(f"• Security: {len(testbook.security_procedures)}")
                st.write(f"• Performance: {len(testbook.performance_procedures)}")
                st.write(f"• Integration: {len(testbook.integration_procedures)}")
                
                # Actions
                if st.button(f"📤 Export Excel", key=f"export_{testbook_id}"):
                    export_testbook_to_excel(testbook)
                
                if st.button(f"🗑️ Delete", key=f"delete_{testbook_id}"):
                    del st.session_state.testbooks[testbook_id]
                    st.rerun()

def testbook_analysis_interface():
    """Interface for analyzing testbook quality and coverage."""
    
    st.markdown("### 📊 Testbook Analysis")
    
    if not st.session_state.testbooks:
        st.info("No testbooks available for analysis.")
        return
    
    # Testbook selection for analysis
    testbook_options = {tb.name: tb_id for tb_id, tb in st.session_state.testbooks.items()}
    selected_testbook_name = st.selectbox(
        "Select testbook to analyze:",
        options=list(testbook_options.keys()),
        key="analysis_testbook"
    )
    
    if not selected_testbook_name:
        return
    
    selected_testbook_id = testbook_options[selected_testbook_name]
    testbook = st.session_state.testbooks[selected_testbook_id]
    
    # Validate testbook completeness
    with st.spinner("Analyzing testbook quality..."):
        validation_result = st.session_state.testbook_generator.validate_testbook_completeness(testbook)
    
    # Display validation results
    col1, col2 = st.columns(2)
    
    with col1:
        if validation_result['is_complete']:
            st.success("✅ Testbook validation passed!")
        else:
            st.error("❌ Testbook has validation issues")
        
        # Statistics
        st.markdown("#### 📈 Statistics")
        stats = validation_result['statistics']
        
        for key, value in stats.items():
            st.metric(key.replace('_', ' ').title(), value)
    
    with col2:
        # Issues and warnings
        if validation_result['issues']:
            st.markdown("#### ⚠️ Issues Found")
            for issue in validation_result['issues']:
                st.error(f"• {issue}")
        
        if validation_result['warnings']:
            st.markdown("#### ⚠️ Warnings")
            for warning in validation_result['warnings']:
                st.warning(f"• {warning}")
        
        # Recommendations
        if validation_result['recommendations']:
            st.markdown("#### 💡 Recommendations")
            for rec in validation_result['recommendations']:
                st.info(f"• {rec}")
    
    # Detailed analysis
    st.markdown("---")
    st.markdown("#### 📋 Detailed Procedure Analysis")
    
    # Category distribution
    all_procedures = testbook.get_all_procedures()
    
    if all_procedures:
        # Priority distribution
        priority_counts = {}
        category_counts = {}
        
        for procedure in all_procedures:
            priority = procedure.priority.value
            category = procedure.category.value
            
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Priority Distribution:**")
            for priority, count in sorted(priority_counts.items()):
                st.write(f"• {priority.title()}: {count}")
        
        with col2:
            st.markdown("**Category Distribution:**")
            for category, count in sorted(category_counts.items()):
                st.write(f"• {category.title()}: {count}")
        
        # Time analysis
        st.markdown("**Time Analysis:**")
        total_time = sum(p.estimated_duration or 0 for p in all_procedures)
        avg_time = total_time / len(all_procedures) if all_procedures else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Time", f"{total_time} min")
        
        with col2:
            st.metric("Average per Test", f"{avg_time:.1f} min")
        
        with col3:
            hours = total_time / 60
            st.metric("Total Hours", f"{hours:.1f} hrs")

def export_testbook_to_excel(testbook):
    """Export testbook to Excel format."""
    
    try:
        with st.spinner("Generating Excel export..."):
            exporter = ExcelExporter()
            excel_buffer = exporter.export_testbook(testbook, template="comprehensive")
            
            # Provide download
            st.download_button(
                label="📥 Download Excel Testbook",
                data=excel_buffer.getvalue(),
                file_name=f"{testbook.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.success("✅ Excel testbook ready for download!")
            
    except Exception as e:
        logger.error(f"Error exporting testbook to Excel: {str(e)}")
        st.error(f"❌ Error exporting to Excel: {str(e)}")

if __name__ == "__main__":
    main()