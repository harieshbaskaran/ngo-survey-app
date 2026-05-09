import streamlit as st
import pandas as pd
import io
import snowflake.connector

# -----------------------------------
# SNOWFLAKE CONNECTION
# -----------------------------------

conn = snowflake.connector.connect(
    user=st.secrets["snowflake"]["user"],
    password=st.secrets["snowflake"]["password"],
    account=st.secrets["snowflake"]["account"],
    warehouse=st.secrets["snowflake"]["warehouse"],
    database=st.secrets["snowflake"]["database"],
    schema=st.secrets["snowflake"]["schema"]
)

session = conn.cursor()

# -----------------------------------
# USER LOGIN DATA
# -----------------------------------

users = {
    "admin": {
        "password": "admin123",
        "role": "Admin"
    },
    "member1": {
        "password": "member123",
        "role": "Survey Member"
    },
    "member2": {
        "password": "member123",
        "role": "Survey Member"
    }
}

# -----------------------------------
# SESSION STATE
# -----------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="NGO Survey System",
    page_icon="📋",
    layout="wide"
)

# -----------------------------------
# LOGIN PAGE
# -----------------------------------

if not st.session_state.logged_in:

    st.title("🔐 NGO Survey Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    login_button = st.button("Login")

    if login_button:

        if username in users:

            if users[username]["password"] == password:

                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = users[username]["role"]

                st.success("✅ Login Successful!")

                st.rerun()

            else:

                st.error("❌ Invalid Password")

        else:

            st.error("❌ Invalid Username")

    st.stop()

# -----------------------------------
# SIDEBAR
# -----------------------------------

st.sidebar.title("📋 NGO Survey System")

st.sidebar.write(
    f"👤 User: {st.session_state.username}"
)

st.sidebar.write(
    f"🔑 Role: {st.session_state.role}"
)

st.sidebar.markdown("---")

if st.sidebar.button("🚪 Logout"):

    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

    st.rerun()

# -----------------------------------
# MENU
# -----------------------------------

if st.session_state.role == "Admin":

    menu = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Home",
            "📝 New Survey",
            "📊 Dashboard",
            "📥 Downloads",
            "⚙️ Admin"
        ]
    )

else:

    menu = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Home",
            "📝 New Survey",
            "📊 Dashboard"
        ]
    )

# -----------------------------------
# HOME PAGE
# -----------------------------------

if menu == "🏠 Home":

    st.title("📋 NGO Survey Management System")

    st.markdown("---")

    query = "SELECT * FROM BEGGAR_SURVEY"

    df = pd.read_sql(query, conn)

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Surveys", len(df))

    col2.metric(
        "Survey Members",
        df["SURVEY_MEMBER"].nunique()
    )

    col3.metric(
        "Areas Covered",
        df["LOCATION"].nunique()
    )

    st.markdown("---")

    st.subheader("Welcome")

    st.write("""
    This application is used to collect and manage beggar survey data for NGO and Government welfare analysis.
    """)

# -----------------------------------
# NEW SURVEY PAGE
# -----------------------------------

elif menu == "📝 New Survey":

    st.title("📝 New Survey Form")

    st.markdown("---")

    with st.form("survey_form"):

        col1, col2 = st.columns(2)

        with col1:

            survey_member = st.text_input(
                "Survey Member Name"
            )

            beggar_name = st.text_input(
                "Beggar Name"
            )

            age = st.number_input(
                "Age",
                min_value=0,
                max_value=120
            )

            gender = st.selectbox(
                "Gender",
                ["Male", "Female", "Other"]
            )

        with col2:

            location = st.text_input(
                "Location"
            )

            disability = st.selectbox(
                "Disability",
                ["Yes", "No"]
            )

            addiction = st.selectbox(
                "Addiction",
                ["Yes", "No"]
            )

            shelter_needed = st.selectbox(
                "Shelter Needed",
                ["Yes", "No"]
            )

            uploaded_photo = st.file_uploader(
                "Upload Photo",
                type=["jpg", "jpeg", "png"]
            )

            if uploaded_photo is not None:

                st.image(
                    uploaded_photo,
                    caption="Uploaded Photo Preview",
                    width=250
                )

        notes = st.text_area(
            "Additional Notes"
        )

        submitted = st.form_submit_button(
            "Submit Survey"
        )

        if submitted:

            insert_query = f"""
            INSERT INTO BEGGAR_SURVEY
            (
                SURVEY_MEMBER,
                BEGGAR_NAME,
                AGE,
                GENDER,
                LOCATION,
                DISABILITY,
                ADDICTION,
                SHELTER_NEEDED,
                NOTES,
                PHOTO_NAME
            )
            VALUES
            (
                '{survey_member}',
                '{beggar_name}',
                {age},
                '{gender}',
                '{location}',
                '{disability}',
                '{addiction}',
                '{shelter_needed}',
                '{notes}',
                '{uploaded_photo.name if uploaded_photo else ""}'
            )
            """

            session.execute(insert_query)

            conn.commit()

            st.success(
                "✅ Survey Submitted Successfully!"
            )

# -----------------------------------
# DASHBOARD
# -----------------------------------

elif menu == "📊 Dashboard":

    st.title("📊 NGO Survey Dashboard")

    st.markdown("---")

    query = "SELECT * FROM BEGGAR_SURVEY"

    df = pd.read_sql(query, conn)

    total_surveys = len(df)

    total_male = len(
        df[df["GENDER"] == "Male"]
    )

    total_female = len(
        df[df["GENDER"] == "Female"]
    )

    total_disability = len(
        df[df["DISABILITY"] == "Yes"]
    )

    total_addiction = len(
        df[df["ADDICTION"] == "Yes"]
    )

    shelter_needed = len(
        df[df["SHELTER_NEEDED"] == "Yes"]
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Surveys",
        total_surveys
    )

    col2.metric(
        "Male",
        total_male
    )

    col3.metric(
        "Female",
        total_female
    )

    col4, col5, col6 = st.columns(3)

    col4.metric(
        "Disability",
        total_disability
    )

    col5.metric(
        "Addiction",
        total_addiction
    )

    col6.metric(
        "Shelter Needed",
        shelter_needed
    )

    st.markdown("---")

    # GENDER CHART

    st.subheader("Gender Distribution")

    gender_data = df["GENDER"].value_counts()

    st.bar_chart(gender_data)

    st.markdown("---")

    # LOCATION CHART

    st.subheader("Location Analysis")

    location_data = df["LOCATION"].value_counts()

    st.bar_chart(location_data)

    st.markdown("---")

    # FILTERS

    st.subheader("🔍 Search & Filters")

    col1, col2 = st.columns(2)

    with col1:

        locations = ["All"] + list(
            df["LOCATION"].unique()
        )

        selected_location = st.selectbox(
            "Select Location",
            locations
        )

    with col2:

        genders = ["All"] + list(
            df["GENDER"].unique()
        )

        selected_gender = st.selectbox(
            "Select Gender",
            genders
        )

    filtered_df = df.copy()

    if selected_location != "All":

        filtered_df = filtered_df[
            filtered_df["LOCATION"] == selected_location
        ]

    if selected_gender != "All":

        filtered_df = filtered_df[
            filtered_df["GENDER"] == selected_gender
        ]

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

    st.markdown("---")

    # MEMBER PERFORMANCE

    st.subheader("👥 Survey Member Performance")

    member_data = df[
        "SURVEY_MEMBER"
    ].value_counts()

    st.bar_chart(member_data)

    st.markdown("---")

    # RECENT SURVEYS

    st.subheader("Recent Surveys")

    recent_df = df.tail(5)

    st.dataframe(
        recent_df,
        use_container_width=True
    )

# -----------------------------------
# DOWNLOAD PAGE
# -----------------------------------

elif menu == "📥 Downloads":

    st.title("📥 Download Center")

    st.markdown("---")

    query = "SELECT * FROM BEGGAR_SURVEY"

    df = pd.read_sql(query, conn)

    st.subheader("Survey Data")

    st.dataframe(
        df,
        use_container_width=True
    )

    st.markdown("---")

    # CSV DOWNLOAD

    csv = df.to_csv(index=False)

    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name="ngo_survey_data.csv",
        mime="text/csv"
    )

    # EXCEL DOWNLOAD

    excel_buffer = io.BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="SurveyData"
        )

    excel_data = excel_buffer.getvalue()

    st.download_button(
        label="⬇️ Download Excel",
        data=excel_data,
        file_name="ngo_survey_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# -----------------------------------
# ADMIN PAGE
# -----------------------------------

elif menu == "⚙️ Admin":

    st.title("⚙️ Admin Panel")

    st.markdown("---")

    query = "SELECT * FROM BEGGAR_SURVEY"

    df = pd.read_sql(query, conn)

    st.subheader("All Survey Records")

    st.dataframe(
        df,
        use_container_width=True
    )

    st.markdown("---")

    # PHOTO RECORDS

    st.subheader("📸 Uploaded Photo Records")

    photo_df = df[
        df["PHOTO_NAME"] != ""
    ][
        ["SURVEY_ID", "BEGGAR_NAME", "PHOTO_NAME"]
    ]

    st.dataframe(
        photo_df,
        use_container_width=True
    )

    st.markdown("---")

    # DELETE RECORD

    st.subheader("🗑️ Delete Survey Record")

    delete_id = st.number_input(
        "Enter Survey ID to Delete",
        min_value=1,
        step=1
    )

    delete_button = st.button(
        "Delete Record"
    )

    if delete_button:

        delete_query = f"""
        DELETE FROM BEGGAR_SURVEY
        WHERE SURVEY_ID = {delete_id}
        """

        session.execute(delete_query)

        conn.commit()

        st.success(
            f"Record {delete_id} deleted successfully!"
        )

        st.rerun()
