import os
import pickle
import streamlit as st
from streamlit_option_menu import option_menu
import sqlite3
import bcrypt

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password BLOB
                )''')
    conn.commit()
    conn.close()

# ---------- AUTH FUNCTIONS ----------
def add_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result:
        return bcrypt.checkpw(password.encode(), result[0])
    return False

# ---------- LOGIN AND REGISTRATION ----------
def login():
    st.title("🔐 Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

    if login_button:
        if verify_user(username, password):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success(f"Welcome {username}!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

    st.markdown("Don't have an account?")
    if st.button("Go to Register"):
        st.session_state["show_register"] = True

def register():
    st.title("📝 Register")
    with st.form("register_form"):
        new_user = st.text_input("Choose a Username")
        new_password = st.text_input("Choose a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        register_button = st.form_submit_button("Create Account")

    if register_button:
        if not new_user or not new_password or not confirm_password:
            st.error("Please fill in all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            success = add_user(new_user, new_password)
            if success:
                st.success("Account created successfully. You can now log in.")
                st.session_state["show_register"] = False
                st.session_state["username"] = new_user
                st.experimental_rerun()
            else:
                st.error("Username already exists. Please choose another.")

    st.markdown("Already have an account?")
    if st.button("Go to Login"):
        st.session_state["show_register"] = False

# ---------- DISEASE PREDICTION APP ----------
def disease_prediction_app():
    # Set page configuration
    st.set_page_config(page_title="Health Assistant", layout="wide", page_icon="🧑‍⚕️")

    # Load saved models
    with open('diabetes_svm_model_updatee.sav', 'rb') as file:
        diabetes_data = pickle.load(file)
        diabetes_model = diabetes_data['model']
        diabetes_scaler = diabetes_data['scaler']

    with open('heart_disease_svm_model_updatee.sav', 'rb') as file:
        heart_data = pickle.load(file)
        heart_disease_model = heart_data['model']
        heart_scaler = heart_data['scaler']

    with open('parkinsons_svm_model_updatee.sav', 'rb') as file:
        parkinsons_data = pickle.load(file)
        parkinsons_model = parkinsons_data['model']
        parkinsons_scaler = parkinsons_data['scaler']

    with open('breast_cancer_svm_model.sav', 'rb') as file:
        breast_cancer_data = pickle.load(file)
        breast_cancer_model = breast_cancer_data['model']
        breast_cancer_scaler = breast_cancer_data['scaler']

    # Sidebar Navigation
with st.sidebar:
        selected = option_menu(
            'Multiple Disease Prediction System',
            ['Diabetes Prediction', 'Heart Disease Prediction', 'Parkinsons Prediction', 'Breast Cancer Prediction'],
            menu_icon='hospital-fill',
            icons=['activity', 'heart', 'person', 'virus'],
            default_index=0
        )    


if selected == 'Diabetes Prediction':
    st.title('Diabetes Prediction using ML')

    # Getting the input data from the user
    col1, col2, col3 = st.columns(3)

    with col1:
        Pregnancies = st.text_input('Number of Pregnancies')

    with col2:
        Glucose = st.text_input('Glucose Level')

    with col3:
        BloodPressure = st.text_input('Blood Pressure value')

    with col1:
        SkinThickness = st.text_input('Skin Thickness value')

    with col2:
        Insulin = st.text_input('Insulin Level')

    with col3:
        BMI = st.text_input('BMI value')

    with col1:
        DiabetesPedigreeFunction = st.text_input('Diabetes Pedigree Function value')

    with col2:
        Age = st.text_input('Age of the Person')

    # Code for Prediction
    diab_diagnosis = ''

    if st.button('Diabetes Test Result'):
        try:
            # Validate and convert user input
            user_input = [Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin,
                          BMI, DiabetesPedigreeFunction, Age]

            # Check for empty inputs and strip whitespace
            user_input = [x.strip() for x in user_input]  # Remove whitespace
            if any(x == '' for x in user_input):
                raise ValueError("All fields must be filled.")

            # Convert inputs to float and handle conversion errors
            user_input = [float(x) for x in user_input]

            # Debugging: Print user inputs
            st.write("User  inputs:", user_input)

            # Scale the input data
            scaled_input = diabetes_scaler.transform([user_input])

            # Predict
            diab_prediction = diabetes_model.predict(scaled_input)

            if diab_prediction[0] == 1:
                diab_diagnosis = 'The person is diabetic'
            else:
                diab_diagnosis = 'The person is not diabetic'

        except ValueError as e:
            diab_diagnosis = f'Error: {e}'
            st.error(diab_diagnosis)

    st.success(diab_diagnosis)

if selected == 'Heart Disease Prediction':
    # Page title
    st.title('Heart disease Prediction using ML')

    # Getting the input data from the user
    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.text_input('Age')

    with col2:
        sex = st.text_input('Sex (0-Female, 1-Male)')

    with col3:
        cp = st.text_input('Chest pain type (0,1,2,3')

    with col1:
        trestbps = st.text_input('Resting blood pressure')

    with col2:
        chol = st.text_input('Cholesterol')

    with col3:
        fbs = st.text_input('Fasting blood pressure (1 = True (High fasting blood sugar), 0 = False (Normal fasting blood sugar))')

    with col1:
        restecg = st.text_input('Resting Electrocardiographic Results(0: Normal, 1: Having ST-T wave abnormalities (suggesting potential heart issues), 2: Showing left ventricular hypertrophy (by Estes’ criteria))')

    with col2:
        thalach = st.text_input('Maximum Heart Rate Achieved')
    with col3:
        exang = st.text_input('Excercie-induced Agina (1 = Yes (Chest pain induced by exercise),0 = No (No chest pain during exercise))')
    with col1:
        oldpeak = st.text_input('ST Depression induced by Exercise Relative to rest')
    with col2: 
        slope = st.text_input('Slope of the peak Exercise ST Segment(0: Upsloping (better heart health),1: Flat (indicating possible heart disease), 2: Downsloping (strong indicator of heart issues))')
    with col3:
        ca = st.text_input('Number of Major Vessels colored by Fluoroscopy(Values range from 0 to 3, where a higher number suggests more vessel narrowing (blockage))')
    with col2:
        thal = st.text_input('Thalassemia (0:Unknown,1: Fixed defect (no blood flow in some parts of the heart), 2: Normal (no issues), 3: Reversible defect (blood flow is reduced during stress but normal at rest))')
        

    # Code for Prediction
    heart_diagnosis = ''

    # Creating a button for Prediction
    if st.button('Heart Test Result'):
        try:
            # Validate and convert user input
            user_input = [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]

            # Check for empty inputs
            if any(x == '' for x in user_input):
                raise ValueError("All fields must be filled.")

            # Convert inputs to float and handle conversion errors
            user_input = [float(x) for x in user_input]

            # Debugging: Print user inputs
            st.write("User inputs:", user_input)

            # Predict
            heart_prediction = heart_disease_model.predict([user_input])

            # Debugging: Print prediction result
            st.write("Prediction result:", heart_prediction)

            if heart_prediction[0] == 1:
                heart_diagnosis = 'The person has a faulty heart'
            else:
                heart_diagnosis = 'The person has a healthy heart'

        except ValueError as e:
            heart_diagnosis = f'Error: {e}'
            st.error(heart_diagnosis)

    st.success(heart_diagnosis)
    
# Parkinson's Prediction Page
if selected == 'Parkinsons Prediction':
    # Page title
    st.title('Parkinson’s Disease Prediction using ML')

    # Getting the input data from the user
    col1, col2, col3 = st.columns(3)

    with col1:
        fo = st.text_input('MDVP:Fo(Hz) (Average vocal fundamental frequency)')

    with col2:
        fhi = st.text_input('MDVP:Fhi(Hz) (Maximum vocal fundamental frequency)')

    with col3:
        flo = st.text_input('MDVP:Flo(Hz) (Minimum vocal fundamental frequency)')

    with col1:
        jitter_percent = st.text_input('MDVP:Jitter(%) (Jitter percentage)')

    with col2:
        jitter_abs = st.text_input('MDVP:Jitter(Abs) (Absolute jitter)')

    with col3:
        rap = st.text_input('MDVP:RAP (Relative amplitude perturbation)')

    with col1:
        ppq = st.text_input('MDVP:PPQ (Five-point period perturbation quotient)')

    with col2:
        ddp = st.text_input('Jitter:DDP (Average absolute difference of differences between jitter cycles)')

    with col3:
        shimmer = st.text_input('MDVP:Shimmer (Shimmer amplitude)')

    with col1:
        shimmer_db = st.text_input('MDVP:Shimmer(dB) (Shimmer in decibels)')

    with col2:
        apq3 = st.text_input('Shimmer:APQ3 (Three-point amplitude perturbation quotient)')

    with col3:
        apq5 = st.text_input('Shimmer:APQ5 (Five-point amplitude perturbation quotient)')

    with col1:
        apq = st.text_input('MDVP:APQ (Amplitude perturbation quotient)')

    with col2:
        dda = st.text_input('Shimmer:DDA (Average absolute differences of differences between amplitude cycles)')

    with col3:
        nhr = st.text_input('NHR (Noise-to-harmonics ratio)')

    with col1:
        hnr = st.text_input('HNR (Harmonics-to-noise ratio)')

    with col2:
        rpde = st.text_input('RPDE (Recurrence period density entropy)')

    with col3:
        dfa = st.text_input('DFA (Detrended fluctuation analysis)')

    with col1:
        spread1 = st.text_input('Spread1 (Nonlinear measure of fundamental frequency variation)')

    with col2:
        spread2 = st.text_input('Spread2 (Nonlinear measure of fundamental frequency variation)')

    with col3:
        d2 = st.text_input('D2 (Nonlinear dynamical complexity measure)')

    with col1:
        ppe = st.text_input('PPE (Pitch period entropy)')

    # Code for Prediction
    parkinsons_diagnosis = ''

    # Creating a button for Prediction
    if st.button('Parkinson’s Test Result'):
        try:
            # Validate and convert user input
            user_input = [fo, fhi, flo, jitter_percent, jitter_abs, rap, ppq, ddp,
                          shimmer, shimmer_db, apq3, apq5, apq, dda, nhr, hnr, rpde, dfa,
                          spread1, spread2, d2, ppe]

            # Check for empty inputs and strip whitespace
            user_input = [x.strip() for x in user_input]  # Remove whitespace
            if any(x == '' for x in user_input):
                raise ValueError("All fields must be filled.")

            # Convert inputs to float and handle conversion errors
            user_input = [float(x) for x in user_input]

            # Debugging: Print user inputs
            st.write("User  inputs:", user_input)

            # Predict
            parkinsons_prediction = parkinsons_model.predict([user_input])

            if parkinsons_prediction[0] == 1:
                parkinsons_diagnosis = 'The person has Parkinson\'s disease'
            else:
                parkinsons_diagnosis = 'The person does not have Parkinson\'s disease'

        except ValueError as e:
            parkinsons_diagnosis = f'Error: {e}'
            st.error(parkinsons_diagnosis)

    st.success(parkinsons_diagnosis)
    
# Breast Cancer Prediction Page
if selected == 'Breast Cancer Prediction':
    st.title('Breast Cancer Prediction using ML')

    # Getting the input data from the user
    col1, col2, col3 = st.columns(3)

    with col1:
        radius_mean = st.text_input('Radius Mean')
    with col2:
        texture_mean = st.text_input('Texture Mean')
    with col3:
        perimeter_mean = st.text_input('Perimeter Mean')

    with col1:
        area_mean = st.text_input('Area Mean')
    with col2:
        smoothness_mean = st.text_input('Smoothness Mean')
    with col3:
        compactness_mean = st.text_input('Compactness Mean')

    with col1:
        concavity_mean = st.text_input('Concavity Mean')
    with col2:
        concave_points_mean = st.text_input('Concave Points Mean')
    with col3:
        symmetry_mean = st.text_input('Symmetry Mean')

    with col1:
        fractal_dimension_mean = st.text_input('Fractal Dimension Mean')
    with col2:
        radius_se = st.text_input('Radius SE')
    with col3:
        texture_se = st.text_input('Texture SE')

    with col1:
        perimeter_se = st.text_input('Perimeter SE')
    with col2:
        area_se = st.text_input('Area SE')
    with col3:
        smoothness_se = st.text_input('Smoothness SE')

    with col1:
        compactness_se = st.text_input('Compactness SE')
    with col2:
        concavity_se = st.text_input('Concavity SE')
    with col3:
        concave_points_se = st.text_input('Concave Points SE')

    with col1:
        symmetry_se = st.text_input('Symmetry SE')
    with col2:
        fractal_dimension_se = st.text_input('Fractal Dimension SE')
    with col3:
        radius_worst = st.text_input('Radius Worst')

    with col1:
        texture_worst = st.text_input('Texture Worst')
    with col2:
        perimeter_worst = st.text_input('Perimeter Worst')
    with col3:
        area_worst = st.text_input('Area Worst')

    with col1:
        smoothness_worst = st.text_input('Smoothness Worst')
    with col2:
        compactness_worst = st.text_input('Compactness Worst')
    with col3:
        concavity_worst = st.text_input('Concavity Worst')

    with col1:
        concave_points_worst = st.text_input('Concave Points Worst')
    with col2:
        symmetry_worst = st.text_input('Symmetry Worst')
    with col3:
        fractal_dimension_worst = st.text_input('Fractal Dimension Worst')

    # Code for Prediction
    cancer_diagnosis = ''

    if st.button('Breast Cancer Test Result'):
        try:
            # Validate and convert user input
            user_input = [
                radius_mean, texture_mean, perimeter_mean, area_mean, smoothness_mean,
                compactness_mean, concavity_mean, concave_points_mean, symmetry_mean,
                fractal_dimension_mean, radius_se, texture_se, perimeter_se, area_se,
                smoothness_se, compactness_se, concavity_se, concave_points_se,
                symmetry_se, fractal_dimension_se, radius_worst, texture_worst,
                perimeter_worst, area_worst, smoothness_worst, compactness_worst,
                concavity_worst, concave_points_worst, symmetry_worst, fractal_dimension_worst
            ]

            # Check for empty inputs and strip whitespace
            user_input = [x.strip() for x in user_input]  # Remove whitespace
            if any(x == '' for x in user_input):
                raise ValueError("All fields must be filled.")

            # Convert inputs to float and handle conversion errors
            user_input = [float(x) for x in user_input]

            # Debugging: Print user inputs
            st.write("User  inputs:", user_input)

            # Scale the input data
            scaled_input = breast_cancer_scaler.transform([user_input])

            # Predict
            cancer_prediction = breast_cancer_model.predict(scaled_input)

            if cancer_prediction[0] == 1:
                cancer_diagnosis = 'The person is Malignant (Breast Cancer Present)'
            else:
                cancer_diagnosis = 'The person is Benign (No Breast Cancer)'

        except ValueError as e:
            cancer_diagnosis = f'Error: {e}'
            st.error(cancer_diagnosis)

    st.success(cancer_diagnosis)
def main():
    init_db()
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
    if "show_register" not in st.session_state:
        st.session_state["show_register"] = False

    if st.session_state["logged_in"]:
        disease_prediction_app()
    elif st.session_state["show_register"]:
        register()
    else:
        login()

if __name__ == "__main__":
    main()
