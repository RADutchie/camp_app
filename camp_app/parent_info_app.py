import openpyxl
import pandas as pd
import streamlit as st


def show():
    # Streamlit app title
    st.title("Parent Camp Info Processor")

    # File upload for group data
    group_file = st.file_uploader("Upload the Camp Group Data Excel File", type=["xlsx"])
    # File upload for camp data
    camp_data_file = st.file_uploader("Upload the Camp Parent Data Excel File", type=["xlsx"])

    # Input for sheet name format
    sheet_name_format = st.selectbox(
        "Select the Sheet Name Format",
        options=["GROUP {}", "CAMP {} GROUP {}"],
        help="Choose 'GROUP {}' for simple group names or 'CAMP {} GROUP {}' for camp-specific group names."
    )

    # Input for the number of groups
    num_groups = st.number_input("Enter the Number of Groups", min_value=1, step=1)

    # Input for camp number (only relevant for 'CAMP {} GROUP {}' format)
    camp_number = 0
    if sheet_name_format == "CAMP {} GROUP {}":
        camp_number = st.number_input("Enter the Number of Camps", min_value=1, step=1)

    st.divider()
    st.markdown("#### Please review the headers of the uploaded files before proceeding.")
    st.markdown("**Note:** The headers should match exactly the expected format for processing.")
    st.markdown("**Expected Headers:** GENDER, CLASS/HG, CAREGIVER_A, A_MOBILE, CAREGIVER_B, B_MOBILE")
    # Review headers of the uploaded files
    if st.button("Review Headers"):
        if group_file:
            if sheet_name_format == "GROUP {}":
                group_data = pd.read_excel(group_file, sheet_name=sheet_name_format.format(1), header=1, engine="openpyxl")
                st.markdown("**Headers in Group Data File:**")
                headers = group_data.drop(columns=["Unnamed: 0"]).columns.tolist()
                st.write(", ".join(headers))
            elif sheet_name_format == "CAMP {} GROUP {}":
                group_data = pd.read_excel(group_file, sheet_name=sheet_name_format.format(1, 1), header=1, engine="openpyxl")
                st.markdown("**Headers in Group Data File:**")
                headers = group_data.drop(columns=["Unnamed: 0"]).columns.tolist()
                st.write(", ".join(headers))
        if camp_data_file:
            camp_data = pd.read_excel(camp_data_file, sheet_name="Sheet2")
            st.markdown("**Headers in Parent Camp Data File:**")
            headers = camp_data.columns.tolist()
            st.write(", ".join(headers))

    class_type = st.selectbox(
        "Select the class type header",
        options=["HG", "CLASS"],
        help="Select the correct header that contains the class type information."
    )
    st.divider()
    # Process files when both are uploaded
    if st.button("Merge files"):
        if group_file and camp_data_file:
            try:
                # Read the camp data file
                camp_data = pd.read_excel(camp_data_file, sheet_name="Sheet2")

                # Columns to copy from camp data
                cols_to_copy = ["GENDER", class_type, "CAREGIVER_A", "A_MOBILE", "CAREGIVER_B", "B_MOBILE"]

                # Initialize a dictionary to store group data
                group_data = {}

                # Get all sheet names in the group file and convert them to uppercase
                excel_file = pd.ExcelFile(group_file)
                sheet_names = {sheet_name.upper(): sheet_name for sheet_name in excel_file.sheet_names}

                # Read each group sheet
                if sheet_name_format == "GROUP {}":
                    for group in range(1, num_groups + 1):
                        sheet_name = sheet_name_format.format(group)

                        # Check if the sheet name exists in the group file
                        if sheet_name not in sheet_names:
                            st.warning(f"Sheet '{sheet_name}' does not exist in the uploaded group file. Skipping.")
                            continue

                        try:
                            group = pd.read_excel(group_file, sheet_name=sheet_names[sheet_name], header=1, engine="openpyxl")
                            group = group.dropna(axis=0, subset=["Unnamed: 0"]).drop(columns=["Unnamed: 0"])
                            group = group.applymap(lambda x: x.strip() if isinstance(x, str) else x)
                            group_data[sheet_name] = group
                        except Exception as e:
                            st.error(f"Error reading sheet '{sheet_name}': {e}")
                            st.stop()

                elif sheet_name_format == "CAMP {} GROUP {}":
                    for camp in range(1, camp_number + 1):
                        for group in range(1, num_groups + 1):
                            sheet_name = sheet_name_format.format(camp, group)

                            # Check if the sheet name exists in the group file
                            if sheet_name not in sheet_names:
                                st.warning(f"Sheet '{sheet_name}' does not exist in the uploaded group file. Skipping.")
                                continue

                            try:
                                group = pd.read_excel(group_file, sheet_name=sheet_names[sheet_name], header=1, engine="openpyxl")
                                group = group.dropna(axis=0, subset=["Unnamed: 0"]).drop(columns=["Unnamed: 0"])
                                group = group.applymap(lambda x: x.strip() if isinstance(x, str) else x)
                                group_data[sheet_name] = group
                            except Exception as e:
                                st.error(f"Error reading sheet '{sheet_name}': {e}")
                                st.stop()

                # Merge group data with camp data
                merged_data = {}
                for sheet_name, group in group_data.items():
                    try:
                        merged = pd.merge(
                            group.drop(columns=cols_to_copy),
                            camp_data[["SURNAME", "FIRST NAME"] + cols_to_copy],
                            on=["SURNAME", "FIRST NAME"],
                            how="left",
                        )
                        merged_data[sheet_name] = merged
                    except KeyError as e:
                        st.error(f"Column mismatch in sheet '{sheet_name}': {e}, check the headers.")
                        st.stop()

                # Save merged data to a new Excel file
                output_file = "group_info.xlsx"
                with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
                    for sheet_name, data in merged_data.items():
                        data.to_excel(writer, sheet_name=sheet_name, index=False)

                # Provide download link for the output file
                with open(output_file, "rb") as f:
                    st.download_button(
                        label="Download Merged Group Info",
                        data=f,
                        file_name="group_info.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )

            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.info("Please upload both the Group Data and Camp Data files to proceed.")
