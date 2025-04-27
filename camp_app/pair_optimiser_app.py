from io import BytesIO

import pandas as pd
import streamlit as st
from student_pair_optimiser import (
    check_for_missing_or_absent,
    final_preferenceses_for_optimisation,
    get_student_preferences,
    solve_pairing,
    students_not_paired,
)


def show():
    # Streamlit App
    st.title("Student Pair Optimiser")

    # File Upload
    uploaded_file = st.file_uploader("Upload a CSV or Excel file with student names and preferences", type=["csv", "xlsx"])

    if uploaded_file:
        # Read the file
        if uploaded_file.name.endswith('.csv'):
            student_data = pd.read_csv(uploaded_file).astype('str')
        else:
            student_data = pd.read_excel(uploaded_file).astype('str')

        st.write("Uploaded Data:")
        st.dataframe(student_data)

        corrected_preferences, main_students = get_student_preferences(student_data)

        # Add editor for kids not attending
        st.subheader("Add Kids Not Attending")
        not_attending_list = []
        not_attending = st.text_area("Enter names of kids not attending, separated by commas")
        not_attending_list = [name.strip() for name in not_attending.split(",") if name.strip()]

        st.divider()
        # Check for missing or absent students
        students_only_in_preferences = check_for_missing_or_absent(corrected_preferences, main_students, not_attending_list)
        students_only_in_preferences.sort()

        if st.button("Check for Missing or Absent Students"):
            if students_only_in_preferences:
                st.write("Students only in preferences but not in the main list:")
                st.dataframe(students_only_in_preferences)
                st.write("Please check the names and ensure they are correct. Any misspellings or incorrect names should be corrected in the CSV file and reloaded.")
                st.write("Any students to be kept out of the pairings should be added to the list of kids not attending and they will be excluded from the optimisation.")
            else:
                st.write("All students are accounted for.")

            # Download button for optimised pairs
            df = pd.DataFrame(students_only_in_preferences, columns=["Students Only in Preferences"])
            output = BytesIO()
            df.to_csv(output, index=False)
            output.seek(0)
            st.download_button(
                label="Download Students Only in Preferences as CSV",
                data=output,
                file_name="students_in_preferences.csv",
                mime="text/csv"
            )

        st.divider()
        exclude_missing_students = st.checkbox("Exclude Missing Students from Pairing Optimisation", value=False)
        if exclude_missing_students:
            st.write("Students only in preferences will be excluded from the optimisation process.")
            st.write("If retained, they are added with no preferences and are optimised with the other kids who preferenced them.")
        else:
            st.write("Students only in preferences will be included in the optimisation process with no preferences.")
            st.write("They will be optimised with the other kids who preferenced them.")

        st.divider()
        # Optimise pairs
        if st.button("Optimise Pairs"):
            try:
                # Final preferences for optimisation
                final_preferences = final_preferenceses_for_optimisation(corrected_preferences, students_only_in_preferences, not_attending_list, exclude=exclude_missing_students)
                optimised_pairs = solve_pairing(final_preferences)
                not_paired = students_not_paired(final_preferences, optimised_pairs)
                st.write("students not paired:")
                st.write(not_paired)
                st.write("Optimised Pairs:")
                st.dataframe(optimised_pairs)

                # Download button for optimised pairs
                optimised_pairs_df = pd.DataFrame(optimised_pairs, columns=["Student_1", "Student_2"])
                output = BytesIO()
                optimised_pairs_df.to_csv(output, index=False)
                output.seek(0)
                st.download_button(
                    label="Download Optimised Pairs as CSV",
                    data=output,
                    file_name="optimised_pairs.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"An error occurred during optimisation: {e}")
