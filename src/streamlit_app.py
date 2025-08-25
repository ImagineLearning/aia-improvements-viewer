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
    
    # Create tabs
    tab1, tab2 = st.tabs(["📖 Grade & Unit View", "📊 Student-Facing Report"])
    
    with tab1:
        show_grade_unit_view(df)
    
    with tab2:
        show_student_facing_report(df)

def show_grade_unit_view(df):
    """Display the original grade and unit filtering view."""
    
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

def classify_content_type(resource_text, description_text=None):
    """
    Classify content as Student-facing, Teacher-facing, or Ambiguous based on resource text and description.
    
    Args:
        resource_text: The resource description text
        description_text: The improvement description text (optional for secondary filtering)
    
    Returns:
        str: 'Teacher-facing', 'Student-facing', or 'Ambiguous'
    """
    if pd.isna(resource_text) or not resource_text:
        resource_text = ""
    
    if pd.isna(description_text) or not description_text:
        description_text = ""
    
    resource_lower = str(resource_text).lower()
    description_lower = str(description_text).lower()
    
    # Teacher-facing keywords (checked first - higher priority)
    teacher_keywords = [
        'teacher', 'teacher edition', 'teacher guide', 'answer key', 
        'solutions', 'rubric', 'scoring guide', 'responding to student thinking', 
        'notes', 'script'
    ]
    
    # Additional teacher-facing keywords for description filtering
    teacher_description_keywords = [
        'responding to student thinking', 'teacher guide', 'answer key',
        'scoring guide', 'rubric', 'teacher edition', 'instructor',
        'facilitator', 'teaching notes', 'pedagogical'
    ]
    
    # Student-facing keywords
    student_keywords = [
        'student workbook', 'student', 'practice problem', 'warm-up', 
        'cool-down', 'activity', 'task', 'lesson', 'assessment', 
        'checkpoint', 'quiz', 'test', 'exit ticket'
    ]
    
    # Check for teacher-facing content in resource first (higher priority)
    for keyword in teacher_keywords:
        if keyword in resource_lower:
            return 'Teacher-facing'
    
    # Secondary check: Teacher-facing content in description
    for keyword in teacher_description_keywords:
        if keyword in description_lower:
            return 'Teacher-facing'
    
    # Then check for student-facing content in resource
    for keyword in student_keywords:
        if keyword in resource_lower:
            return 'Student-facing'
    
    # If ambiguous (including cases where both teacher & student appear or generic labels)
    # Based on your note, ambiguous items are teacher-facing
    return 'Teacher-facing'

def show_student_facing_report(df):
    """Display the student-facing report view with date-based organization."""
    
    st.header("📊 Student-Facing Content Report")
    st.markdown("*View all student-facing improvements organized by date*")
    
    # Add content type classification to dataframe
    df_with_classification = df.copy()
    df_with_classification['Content_Type'] = df_with_classification.apply(
        lambda row: classify_content_type(row['Resource'], row['Improvement_Description']), 
        axis=1
    )
    
    # Content type filter
    st.subheader("🎯 Content Filter")
    content_filter = st.radio(
        "Select content type to display:",
        options=['Student-facing', 'Teacher-facing', 'All Content'],
        index=0,  # Default to Student-facing
        horizontal=True,
        help="Filter improvements by whether they affect student-facing or teacher-facing materials"
    )
    
    # Apply content filter
    if content_filter == 'Student-facing':
        filtered_by_content = df_with_classification[df_with_classification['Content_Type'] == 'Student-facing'].copy()
    elif content_filter == 'Teacher-facing':
        filtered_by_content = df_with_classification[df_with_classification['Content_Type'] == 'Teacher-facing'].copy()
    else:  # All Content
        filtered_by_content = df_with_classification.copy()
    
    # Get unique grade levels for multi-select
    grade_levels = filtered_by_content['Grade_Level'].unique()
    
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
    
    # Add any grades not in our predefined order
    for grade in grade_levels:
        if grade not in sorted_grade_levels:
            sorted_grade_levels.append(grade)
    
    # Multi-select for grades
    selected_grades = st.multiselect(
        "📚 Select Grade Level(s):",
        options=sorted_grade_levels,
        default=sorted_grade_levels,  # Default to all grades
        help="Select one or more grade levels to include in the report"
    )
    
    if not selected_grades:
        st.warning("Please select at least one grade level to view the report.")
        return
    
    # Filter data by selected grades
    filtered_df = filtered_by_content[filtered_by_content['Grade_Level'].isin(selected_grades)].copy()
    
    if filtered_df.empty:
        st.warning(f"No {content_filter.lower()} content found for the selected grade levels.")
        return
    
    # Sort by date (most recent first)
    try:
        filtered_df['Date_Updated_Sort'] = pd.to_datetime(filtered_df['Date_Updated'], errors='coerce')
        filtered_df = filtered_df.sort_values('Date_Updated_Sort', ascending=False, na_last=True)
    except:
        pass
    
    # Create report summary with content type breakdown
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Changes", len(filtered_df))
    with col2:
        st.metric("Grade Levels", len(selected_grades))
    with col3:
        unique_dates = filtered_df['Date_Updated'].nunique()
        st.metric("Update Dates", unique_dates)
    with col4:
        st.metric("Content Type", content_filter)
    
    # Show content type distribution for transparency
    if content_filter == 'All Content':
        st.subheader("📈 Content Type Distribution")
        content_counts = df_with_classification['Content_Type'].value_counts()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Student-facing", content_counts.get('Student-facing', 0))
        with col2:
            st.metric("Teacher-facing", content_counts.get('Teacher-facing', 0))
        with col3:
            total_classified = content_counts.get('Student-facing', 0) + content_counts.get('Teacher-facing', 0)
            st.metric("Total Classified", total_classified)
    
    # Export button
    if st.button("📥 Export as CSV", type="secondary"):
        csv_data = filtered_df[['Date_Updated', 'Grade_Level', 'Unit', 'Resource', 'Page_Numbers', 'Improvement_Description', 'Content_Type']].copy()
        csv_string = csv_data.to_csv(index=False)
        content_type_filename = content_filter.lower().replace('-', '_').replace(' ', '_')
        st.download_button(
            label="Download CSV",
            data=csv_string,
            file_name=f"{content_type_filename}_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Display data in a table format organized by date
    st.subheader(f"📋 Detailed {content_filter} Report")
    
    # Create a cleaner display dataframe (excluding Location since it's all N/A)
    display_df = filtered_df[['Date_Updated', 'Grade_Level', 'Unit', 'Resource', 'Page_Numbers', 'Improvement_Description', 'Content_Type']].copy()
    
    # Rename columns for better display
    display_df.columns = ['Date Updated', 'Grade Level', 'Unit', 'Resource', 'Page Numbers', 'Description', 'Content Type']
    
    # Fill NaN values for better display
    display_df = display_df.fillna('N/A')
    
    # Configure column widths and text wrapping (removed Location column)
    column_config = {
        "Date Updated": st.column_config.TextColumn(width="medium"),
        "Grade Level": st.column_config.TextColumn(width="medium"),
        "Unit": st.column_config.TextColumn(width="medium"),
        "Resource": st.column_config.TextColumn(width="medium"),
        "Page Numbers": st.column_config.TextColumn(width="small"),
        "Description": st.column_config.TextColumn(
            width="large",
            help="Full description of the improvement"
        ),
        "Content Type": st.column_config.TextColumn(width="medium")
    }
    
    # Display as dataframe with text wrapping and sorting capability
    st.dataframe(
        display_df,
        use_container_width=True,
        height=600,
        column_config=column_config
    )
    
    # Organize detailed view by grade level in tabs
    st.subheader("🔍 Detailed View by Grade Level")
    
    if len(selected_grades) == 1:
        # If only one grade selected, show without tabs
        grade = selected_grades[0]
        grade_data = filtered_df[filtered_df['Grade_Level'] == grade]
        _display_grade_improvements(grade_data, grade)
    else:
        # Multiple grades - use tabs for organization
        grade_tabs = st.tabs([f"📚 {grade}" for grade in selected_grades])
        
        for i, grade in enumerate(selected_grades):
            with grade_tabs[i]:
                grade_data = filtered_df[filtered_df['Grade_Level'] == grade]
                _display_grade_improvements(grade_data, grade)

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("*Improvement Viewer v1.0*")
    if not filtered_df.empty:
        last_extracted = filtered_df['Date_Extracted'].iloc[0]
        if pd.notna(last_extracted):
            st.sidebar.caption(f"Last updated: {last_extracted}")
        else:
            st.sidebar.caption("Last updated: Unknown")

def _display_grade_improvements(grade_data, grade_name):
    """Helper function to display improvements for a specific grade level."""
    if grade_data.empty:
        st.info(f"No improvements found for {grade_name}")
        return
    
    st.markdown(f"**{len(grade_data)} improvement(s) for {grade_name}**")
    
    # Sort by date for this grade
    try:
        grade_data = grade_data.sort_values('Date_Updated_Sort', ascending=False, na_last=True)
    except:
        pass
    
    # Display improvements as expandable cards
    for idx, (_, row) in enumerate(grade_data.iterrows(), 1):
        date_str = row.get('Date_Updated', 'Unknown Date')
        content_type = row.get('Content_Type', 'Unknown')
        unit_str = row.get('Unit', 'Unknown Unit')
        
        # Add emoji based on content type
        emoji = "👨‍🏫" if content_type == "Teacher-facing" else "👨‍🎓"
        
        with st.expander(f"{emoji} {unit_str} - {date_str} - Change {idx}", expanded=False):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("**Change Details:**")
                st.write(f"**Content Type:** {content_type}")
                st.write(f"**Unit:** {row.get('Unit', 'N/A')}")
                st.write(f"**Resource:** {row.get('Resource', 'N/A')}")
                st.write(f"**Location:** {row.get('Location', 'N/A')}")
                if pd.notna(row.get('Page_Numbers')) and row.get('Page_Numbers'):
                    st.write(f"**Pages:** {row.get('Page_Numbers')}")
                st.write(f"**Date Updated:** {date_str}")
            
            with col2:
                st.markdown("**Description:**")
                improvement_desc = row.get('Improvement_Description', 'No description available')
                if pd.notna(improvement_desc) and improvement_desc:
                    st.write(str(improvement_desc))
                else:
                    st.write('No description available')

if __name__ == "__main__":
    main()
