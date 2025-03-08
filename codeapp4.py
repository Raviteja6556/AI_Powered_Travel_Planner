import streamlit as st
import google.generativeai as genai
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import os
import re
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup
def setup_ai_model():
    api_key = "AIzaSyDOGNoA-G1ceO6rW0S_ujw6Y0opowIQGf8"
    chat_template = ChatPromptTemplate(
        messages=[
            ("system", """You are an AI-powered travel planning assistant. Provide a detailed travel plan from [Source] to [Destination] for the dates [Start Date] to [End Date], including all modes of transport (flights, trains, buses, cabs), estimated costs, and any relevant travel tips."""),
            ("human", "From {source} to {destination} from {start_date} to {end_date}.")
        ]
    )
    # Use Gemini 2.0 Flash-Lite for efficiency
    chat_model = ChatGoogleGenerativeAI(api_key=api_key, model="gemini-2.0-flash-lite", temperature=1)
    parser = StrOutputParser()
    return chat_template | chat_model | parser

# Input Validation
def validate_location(location):
    if not location:
        return False
    # Basic validation, can be improved with more complex regex or external validation services
    return bool(re.match("^[a-zA-Z\s]+$", location))

# List of major cities in India
major_cities = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad", "Chennai", "Kolkata", "Pune", "Surat", "Jaipur",
    "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane", "Agra", "Vadodara", "Visakhapatnam", "Bhopal", "Chandigarh",
    "Coimbatore", "Patna", "Mysore", "Ranchi", "Gurgaon", "Noida", "Ghaziabad", "Faridabad", "Srinagar", "Jammu",
    "Dehradun", "Amritsar", "Varanasi", "Kochi", "Trivandrum", "Guwahati", "Raipur", "Jamshedpur", "Bhubaneswar",
    "Cuttack", "Siliguri", "Dhanbad", "Asansol", "Allahabad", "Meerut", "Jodhpur", "Udaipur", "Ajmer", "Kota"
]

# Function to get weather forecast
def get_weather_forecast(location):
    weather_api_key = "d6956b719d7c080569e6f5e53d369b53"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={weather_api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        return data["weather"][0]["description"]
    
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    
    except requests.exceptions.ConnectionError as conn_err:
        return f"Connection error occurred: {conn_err}"
    
    except requests.exceptions.Timeout as timeout_err:
        return f"Timeout error occurred: {timeout_err}"
    
    except requests.exceptions.RequestException as req_err:
        return f"An error occurred: {req_err}"

# App Interface
def create_app_interface(chain):
    st.title("AI-Powered Travel Planner")
    
    # Display booking links at the beginning
    st.write("Book your tickets:")
    st.write("- Flights: [Expedia](https://www.expedia.com/), [Kayak](https://www.kayak.com/)")
    st.write("- Trains: [Indian Railways](https://www.irctc.co.in/), [Amtrak](https://www.amtrak.com/)")
    st.write("- Buses: [RedBus](https://www.redbus.in/), [MakeMyTrip](https://www.makemytrip.com/bus-tickets/)")
    
    # Dropdown for common locations
    source = st.selectbox("Select source location", ["Other"] + major_cities)
    if source == "Other":
        source = st.text_input("Enter custom source location")
    
    destination = st.selectbox("Select destination location", ["Other"] + major_cities)
    if destination == "Other":
        destination = st.text_input("Enter custom destination location")
    
    start_date = st.date_input("Enter start date")
    end_date = st.date_input("Enter end date")
    
    budget = st.number_input("Enter your budget (optional)", min_value=0)
    preferred_mode = st.selectbox("Preferred mode of transport", ["Any", "Flight", "Train", "Bus", "Cab"])
    
    if st.button("Plan Trip"):
        if not validate_location(source) or not validate_location(destination):
            st.error("Please enter valid locations.")
            return
        
        try:
            # Pass a dictionary to chain.invoke()
            raw_input = {
                "source": source,
                "destination": destination,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "budget": budget,
                "preferred_mode": preferred_mode
            }
            output = chain.invoke(raw_input)
            
            st.write("Travel Plan:")
            st.write(output)
            
            # Display weather forecast
            forecast = get_weather_forecast(destination)
            st.write(f"Weather forecast at {destination}: {forecast}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Main Function
def main():
    chain = setup_ai_model()
    create_app_interface(chain)

if __name__ == "__main__":
    main()