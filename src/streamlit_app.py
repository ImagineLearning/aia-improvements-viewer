#!/usr/bin/env python3
"""
Streamlit app for viewing errata improvements by grade level and unit.
"""

import streamlit as st
import pandas as pd
import os
from pathlib import Path

# Configure the page
st.set_page_config(
    page_title="Errata Viewer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_errata_data():
    """Load errata data from CSV file."""
    csv_path = Path("src/output/errata_changes.csv")
    sample_path = Path("sample_data.csv")
    
    # Try to load the real data first
    if csv_path.exists():
        try:
            df = pd.read_csv(csv_path)
            st.success("📊 Displaying current errata data from latest extraction.")
            return df
        except Exception as e:
            st.warning(f"Error loading main CSV file: {e}. Using sample data.")
    
    # Use sample data as fallback
    if sample_path.exists():
        try:
            df = pd.read_csv(sample_path)
            st.info("📋 Displaying sample data. Run the extraction script to get current data.")
            return df
        except Exception as e:
            st.error(f"Error loading sample data: {e}")
            return None
    
    st.error("No data files found. Please run the extraction script to generate data.")
    return None

def format_resource_info(resource, location, page_numbers):
    """Format resource, location, and page numbers into a single string."""
    parts = []
    
    # Convert to string and check if not empty/NaN
    resource_str = str(resource) if pd.notna(resource) and resource else ""
    location_str = str(location) if pd.notna(location) and location else ""
    page_numbers_str = str(page_numbers) if pd.notna(page_numbers) and page_numbers else ""
    
    if resource_str and resource_str != "nan":
        parts.append(resource_str)
    
    if location_str and location_str != "nan":
        parts.append(location_str)
    
    if page_numbers_str and page_numbers_str != "nan":
        parts.append(f"Page(s): {page_numbers_str}")
    
    return " - ".join(parts) if parts else "No resource information available"

def main():
    """Main app function."""
    
    # Title and description
    st.title("📚 Curriculum Improvements Viewer")
    st.markdown("*View curriculum improvements and corrections by grade level and unit*")
    
    # Load data
    df = load_errata_data()
    
    if df is None:
        st.stop()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Get unique grade levels and sort them in educational order
    grade_levels = df['Grade_Level'].unique()
    
    # Define the correct educational order
    grade_order = [
        'Kindergarten',
        'Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5', 
        'Grade 6', 'Grade 7', 'Grade 8',
        'Algebra 1', 'Geometry', 'Algebra 2'
    ]
    
    # Sort grade levels according to educational order
    sorted_grade_levels = []
    for grade in grade_order:
        if grade in grade_levels:
            sorted_grade_levels.append(grade)
    
    # Add any grades not in our predefined order (just in case)
    for grade in grade_levels:
        if grade not in sorted_grade_levels:
            sorted_grade_levels.append(grade)
    
    # Grade level selection
    selected_grade = st.sidebar.selectbox(
        "Select Grade Level:",
        options=sorted_grade_levels,
        index=0 if len(sorted_grade_levels) > 0 else None
    )
    
    # Filter units based on selected grade
    if selected_grade:
        grade_units = sorted(df[df['Grade_Level'] == selected_grade]['Unit'].unique())
        
        selected_unit = st.sidebar.selectbox(
            "Select Unit:",
            options=grade_units,
            index=0 if len(grade_units) > 0 else None
        )
    else:
        selected_unit = None
    
    # View button
    view_button = st.sidebar.button("🔍 View Improvements", type="primary")
    
    # Display results
    if view_button and selected_grade and selected_unit:
        
        # Filter data
        filtered_df = df[
            (df['Grade_Level'] == selected_grade) & 
            (df['Unit'] == selected_unit)
        ].copy()
        
        if filtered_df.empty:
            st.warning(f"No improvements found for {selected_grade}, {selected_unit}")
        else:
            # Display header
            st.header(f"📖 {selected_grade} - {selected_unit}")
            st.markdown(f"**{len(filtered_df)} improvement(s) found**")
            
            # Sort by date updated (most recent first)
            try:
                # Convert date column to datetime for sorting
                filtered_df['Date_Updated_Sort'] = pd.to_datetime(filtered_df['Date_Updated'], errors='coerce')
                filtered_df = filtered_df.sort_values('Date_Updated_Sort', ascending=False, na_last=True)
            except:
                # If date conversion fails, just use original order
                pass
            
            # Display each improvement in an expandable section
            for idx, (_, row) in enumerate(filtered_df.iterrows(), 1):
                
                # Format the resource information
                resource_info = format_resource_info(
                    row.get('Resource', ''),
                    row.get('Location', ''),
                    row.get('Page_Numbers', '')
                )
                
                # Create expandable section
                with st.expander(f"📝 Improvement {idx}", expanded=False):
                    
                    # Bold resource information
                    st.markdown(f"**{resource_info}**")
                    
                    # Improvement description
                    improvement_desc = row.get('Improvement_Description', '')
                    if pd.notna(improvement_desc) and improvement_desc:
                        improvement_desc = str(improvement_desc)
                    else:
                        improvement_desc = 'No description available'
                    
                    st.markdown(improvement_desc)
                    
                    # Additional info in smaller text
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        date_updated = row.get('Date_Updated')
                        if pd.notna(date_updated) and date_updated:
                            st.caption(f"🗓️ Updated: {date_updated}")
                    
                    with col2:
                        improvement_type = row.get('Improvement_Type')
                        if pd.notna(improvement_type) and improvement_type:
                            st.caption(f"🏷️ Type: {improvement_type}")
                    
                    with col3:
                        date_extracted = row.get('Date_Extracted')
                        if pd.notna(date_extracted) and date_extracted:
                            st.caption(f"📥 Extracted: {date_extracted}")
    
    elif not view_button:
        # Welcome message
        st.info("👈 Please select a grade level and unit from the sidebar, then click 'View Improvements' to see the data.")
    
    else:
        st.warning("Please select both a grade level and unit to view improvements.")

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("*Improvement Viewer v1.0*")
    if df is not None and not df.empty:
        last_extracted = df['Date_Extracted'].iloc[0]
        if pd.notna(last_extracted):
            st.sidebar.caption(f"Last updated: {last_extracted}")
        else:
            st.sidebar.caption("Last updated: Unknown")

if __name__ == "__main__":
    main()
