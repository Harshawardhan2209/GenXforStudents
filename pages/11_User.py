import streamlit as st
import sqlite3
import random
import string

# Database initialization
conn = sqlite3.connect('user_data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT)''')
conn.commit()

st.title("College.ai")

# Function to generate OTP
def generate_otp():
    otp = ''.join(random.choices(string.digits, k=6))
    return otp


# Function to send OTP (dummy implementation)
def send_otp(email, otp):
    # Dummy implementation, replace with actual email sending logic
    st.write(f"An OTP has been sent to {email}. Your OTP is: {otp}")


def main():
    if "logged_in" not in st.session_state:
        form_type = st.radio("Select Action", ("Login", "Sign Up", "Forgot Password"))

        if form_type == "Login":
            form = st.form(key="login_form")
            form.subheader("Login")

            user = form.text_input("Username")
            password = form.text_input("Password", type="password")

            if form.form_submit_button("Login"):
                # Check if username and password are correct
                c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, password))
                result = c.fetchone()
                if result:
                    st.session_state["user"] = user
                    st.session_state["logged_in"] = True
                    st.success("Logged in successfully!")
                else:
                    st.error("Invalid username or password")

        elif form_type == "Sign Up":
            form = st.form(key="signup_form")
            form.subheader("Sign Up")

            new_user = form.text_input("New Username")
            new_password = form.text_input("New Password", type="password")
            email = form.text_input("Email")

            if form.form_submit_button("Sign Up"):
                # Add user to database
                c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                          (new_user, new_password, email))
                conn.commit()
                st.success("Account created successfully! Please login.")

        elif form_type == "Forgot Password":
            form = st.form(key="forgot_password_form")
            form.subheader("Forgot Password")

            email = form.text_input("Enter Email")

            if form.form_submit_button("Send OTP"):
                # Check if email exists in database
                c.execute("SELECT * FROM users WHERE email=?", (email,))
                result = c.fetchone()
                if result:
                    otp = generate_otp()
                    send_otp(email, otp)
                    st.success("OTP sent successfully! Check your email.")
                else:
                    st.error("Email not found in database")

    else:
        st.subheader("Logged in")
        st.write("You are logged in as:", st.session_state["user"])

        if st.button("Logout"):
            del st.session_state["logged_in"]
            del st.session_state["user"]
            st.success("Logged out successfully!")


if __name__ == "__main__":
    main()
