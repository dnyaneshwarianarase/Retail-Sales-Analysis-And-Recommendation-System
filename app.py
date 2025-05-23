# import streamlit as st
# from database import save_user_to_db, validate_login, is_user_exists, update_user_password
# ############## Import the visualization and recommendation functions
# from visualization import run_visualization_dashboard
# from recommendation import run_recommendation_dashboard


# st.set_page_config(page_title="app", layout="wide")

# # Session management
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False
# if "username" not in st.session_state:
#     st.session_state.username = None

# # Login form
# def login_page():
#     st.title("Login Page")
#     username_or_email = st.text_input("Username or Email", key="login_username")
#     password = st.text_input("Password", type="password", key="login_password")

#     if st.button("Login"):
#         user = validate_login(username_or_email, password)
#         if user:
#             st.session_state.logged_in = True
#             st.session_state.username = user[0]  # Store username in session
#             st.success(f"Welcome {user[0]}!")
#         else:
#             st.error("Invalid username/email or password!")

# # Signup form
# def signup_page():
#     st.title("Signup Page")
#     username = st.text_input("Choose a Username", key="signup_username")
#     email = st.text_input("Enter Email", key="signup_email")
#     password = st.text_input("Choose a Password", type="password", key="signup_password")
    
#     if st.button("Sign Up"):
#         if is_user_exists(username, email):
#             st.error("Username or email already exists!")
#         else:
#             success = save_user_to_db(username, email, password)
#             if success:
#                 st.success("Signup successful! You can now log in.")
#             else:
#                 st.error("Error creating account!")

# # Password reset
# def reset_password_page():
#     st.title("Reset Password")
#     email = st.text_input("Enter your registered email", key="reset_email")
#     new_password = st.text_input("Enter New Password", type="password", key="reset_password")

#     if st.button("Reset Password"):
#         if is_user_exists(email=email):
#             update_user_password(email, new_password, by_email=True)
#             st.success("Password updated successfully!")
            
#         else:
#             st.error("Email not found!")

# # # Navigation
# # menu = ["Login", "Signup", "Reset Password"]
# # choice = st.sidebar.selectbox("Menu", menu)

# # if choice == "Login":
# #     login_page()
# # elif choice == "Signup":
# #     signup_page()
# # elif choice == "Reset Password":
# #     reset_password_page()


# # MAIN DASHBOARD
# def dashboard():
#     st.sidebar.title("D-Mart Dashboard")
#     page = st.sidebar.radio("Navigation", ["📊 Overview", "🤝 Product Recommendation"])

#     if page == "📊 Overview":
#         run_visualization_dashboard()
#     elif page == "🤝 Product Recommendation":
#         run_recommendation_dashboard()

# # MAIN APP NAVIGATION
# if st.session_state.logged_in:
#     dashboard()
# else:
#     menu = st.sidebar.selectbox("Menu", ["Login", "Signup", "Reset Password"])
#     if menu == "Login":
#         login_page()
#     elif menu == "Signup":
#         signup_page()
#     elif menu == "Reset Password":
#         reset_password_page()


########################################################
import streamlit as st
from database import save_user_to_db, validate_login, is_user_exists, update_user_password
from visualization import run_visualization_dashboard
from recommendation import run_recommendation_dashboard

st.set_page_config(page_title="D-Mart Analytics", layout="wide")

# Session management (Not strictly necessary anymore, just for handling login state if needed)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# Login form
def login_page():
    st.title("Login Page")
    username_or_email = st.text_input("Username or Email", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        user = validate_login(username_or_email, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = user[0]  # Store username in session
            st.success(f"Welcome {user[0]}!")
        else:
            st.error("Invalid username/email or password!")

# Signup form
def signup_page():
    st.title("Signup Page")
    username = st.text_input("Choose a Username", key="signup_username")
    email = st.text_input("Enter Email", key="signup_email")
    password = st.text_input("Choose a Password", type="password", key="signup_password")
    
    if st.button("Sign Up"):
        if is_user_exists(username, email):
            st.error("Username or email already exists!")
        else:
            success = save_user_to_db(username, email, password)
            if success:
                st.success("Signup successful! You can now log in.")
            else:
                st.error("Error creating account!")

# Password reset
def reset_password_page():
    st.title("Reset Password")
    email = st.text_input("Enter your registered email", key="reset_email")
    new_password = st.text_input("Enter New Password", type="password", key="reset_password")

    if st.button("Reset Password"):
        if is_user_exists(email=email):
            update_user_password(email, new_password, by_email=True)
            st.success("Password updated successfully!")
        else:
            st.error("Email not found!")

# MAIN DASHBOARD
def dashboard():
    st.sidebar.title("D-Mart Dashboard")
    page = st.sidebar.radio("Navigation", ["📊 Overview", "🤝 Product Recommendation"])

    if page == "📊 Overview":
        run_visualization_dashboard()
    elif page == "🤝 Product Recommendation":
        run_recommendation_dashboard()

# MAIN APP NAVIGATION
def main_app():
    # Sidebar navigation with all pages visible
    menu = st.sidebar.selectbox("Menu", ["Login", "Signup", "Reset Password", "Dashboard"])
    
    if menu == "Login":
        login_page()
    elif menu == "Signup":
        signup_page()
    elif menu == "Reset Password":
        reset_password_page()
    elif menu == "Dashboard":
        # Display dashboard even if not logged in
        dashboard()

# Run the main app
main_app()
