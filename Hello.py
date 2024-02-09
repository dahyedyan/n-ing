import streamlit as st
import pandas as pd
from datetime import datetime

# Function to process the CSV data
def process_data(file, start_date, end_date):
    # Read the CSV data
    chat_data = pd.read_csv(file)
    
    # Convert date columns to datetime
    chat_data['Date'] = pd.to_datetime(chat_data['Date'], format='%Y-%m-%d %H:%M:%S')
    
    # Ensure start_date and end_date are datetime objects at the beginning of the day for start and end of the day for end
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1, seconds=-1)
    
    # Filter data for the given date range
    mask = (chat_data['Date'] >= start_datetime) & (chat_data['Date'] <= end_datetime)
    filtered_data = chat_data[mask]
    
    # Find messages that contain the keyword '#정산'
    settlement_messages = filtered_data[filtered_data['Message'].str.contains('#정산')]
    
    # Process messages to extract settlement data
    settlement_data = []
    for _, row in settlement_messages.iterrows():
        entries = row['Message'].split()
        for entry in entries:
            if '/' in entry:
                item, amount = entry.split('/')
                if item and amount:
                    settlement_data.append({
                        'Date': row['Date'],
                        'Settler': row['User'],
                        'Usage': item.replace('#정산', '').strip(),
                        'Amount': float(amount.strip())
                    })
    
    # Convert to DataFrame
    settlement_df = pd.DataFrame(settlement_data)
    
    # Summarize data by settler
    summary_by_settler = settlement_df.groupby('Settler')['Amount'].sum().reset_index()
    grand_total = settlement_df['Amount'].sum()
    
    # Calculate the amount each person should pay (N빵)
    equal_share = grand_total / len(summary_by_settler)
    
    # Calculate how much each settler needs to pay or receive
    summary_by_settler['Settlement'] = equal_share - summary_by_settler['Amount']
    
    # Format the Settlement column to show + for amounts to pay, and - for amounts to receive
    summary_by_settler['Settlement'] = summary_by_settler['Settlement'].apply(
        lambda x: f"+{x:.2f}" if x > 0 else f"{x:.2f}")
    
    return summary_by_settler, grand_total, equal_share

# Streamlit interface
st.title('Monthly Settlement Calculator')

# File upload widget
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Date input fields
start_date = st.date_input('Start Date', datetime.today())
end_date = st.date_input('End Date', datetime.today())

# Button to process data
if st.button('Calculate Settlements'):
    if uploaded_file is not None and start_date and end_date:
        # Process the uploaded CSV file
        summary_by_settler, grand_total, equal_share = process_data(uploaded_file, start_date, end_date)
        
        # Display results
        st.write('Total amount spent by each settler:')
        st.dataframe(summary_by_settler)
        
        st.write(f'Grand Total of all expenses: {grand_total:.2f}')
        st.write(f'Each person\'s share: {equal_share:.2f}')
        
        # Show how much each settler needs to pay or receive
        st.write('Settlement per settler:')
        st.dataframe(summary_by_settler[['Settler', 'Settlement']])
    else:
        st.error('Please upload a file and select a valid date range.')

# Run the Streamlit app from the command line using: streamlit run your_script_name.py
