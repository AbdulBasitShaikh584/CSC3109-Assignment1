import requests
import pandas as pd
import streamlit as st

API = "http://localhost:5000/students"

st.title("Student Management System")


def fetch_students():
    try:
        r = requests.get(API, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        st.error(f"Cannot reach the API: {e}")
        return []


def show_result(resp, ok_msg):
    if resp.ok:
        st.session_state["flash"] = ok_msg
        st.rerun()  # refresh displayed records
    else:
        st.error(resp.json().get("error", "Something went wrong"))


if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

students = fetch_students()

# ---- View ----
st.subheader("All Students")
if students:
    st.dataframe(pd.DataFrame(students), use_container_width=True, hide_index=True)
else:
    st.info("No students found.")

# ---- Add ----
st.subheader("Add New Student")
with st.form("add_form", clear_on_submit=True):
    name = st.text_input("Name")
    dept = st.text_input("Department")
    email = st.text_input("Email")
    if st.form_submit_button("Add Student"):
        show_result(
            requests.post(API, json={"name": name, "department": dept, "email": email}),
            "Student added!",
        )

# ---- Update / Delete ----
st.subheader("Update or Delete Student")
if students:
    options = {f"{s['id']} - {s['name']}": s for s in students}
    choice = st.selectbox("Select a student", list(options.keys()))
    s = options[choice]

    with st.form(f"update_form_{s['id']}"):
        u_name = st.text_input("Name", value=s["name"])
        u_dept = st.text_input("Department", value=s["department"])
        u_email = st.text_input("Email", value=s["email"])
        if st.form_submit_button("Update Student"):
            show_result(
                requests.put(f"{API}/{s['id']}", json={"name": u_name, "department": u_dept, "email": u_email}),
                "Student updated!",
            )

    if st.button("Delete Student", type="primary"):
        show_result(requests.delete(f"{API}/{s['id']}"), "Student deleted!")
