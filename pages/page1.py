from data.data_loader import load_data

def render():
    data = load_data()
    st.write(data)