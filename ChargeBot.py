import streamlit as st
import pandas as pd

# EV Charger Database
charger_db = {
    "Level 1 (120V)": {
        "power": 1.4,  # kW
        "amps": 12,
        "voltage": 120,
        "best_for": ["PHEVs", "short-range EVs", "overnight residential"],
        "installation": "Plug-in (NEMA 5-15)",
        "cost": "Low",
        "charge_rate": "2-5 miles/hour"
    },
    "Level 2 (240V)": {
        "power": 7.2,  # kW (typical)
        "amps": 30,
        "voltage": 240,
        "best_for": ["Most BEVs", "daily commuting", "residential/commercial"],
        "installation": "Hardwired or plug-in (NEMA 14-50)",
        "cost": "Medium",
        "charge_rate": "10-20 miles/hour"
    },
    "DC Fast Charger (50kW)": {
        "power": 50,  # kW
        "amps": 125,
        "voltage": 480,
        "best_for": ["Commercial locations", "highway corridors", "fleets"],
        "installation": "Professional installation required",
        "cost": "High",
        "charge_rate": "100-200 miles/hour"
    },
    "DC Fast Charger (150kW+)": {
        "power": 150,  # kW
        "amps": 400,
        "voltage": 800,
        "best_for": ["Commercial locations", "long-distance travel", "public charging"],
        "installation": "Professional installation + utility upgrades",
        "cost": "Very High",
        "charge_rate": "300+ miles/hour"
    }
}

# Vehicle Database
vehicle_db = {
    "Tesla Model 3 Standard Range": {"battery": 54, "range": 272, "max_charge_rate": 170},
    "Tesla Model 3 Long Range": {"battery": 82, "range": 358, "max_charge_rate": 250},
    "Chevy Bolt EV": {"battery": 65, "range": 259, "max_charge_rate": 55},
    "Nissan Leaf (40 kWh)": {"battery": 40, "range": 149, "max_charge_rate": 50},
    "Ford Mustang Mach-E": {"battery": 68, "range": 230, "max_charge_rate": 150},
    "PHEV (e.g., Prius Prime)": {"battery": 8.8, "range": 25, "max_charge_rate": 3.3},
    "Other EV": {"battery": 50, "range": 200, "max_charge_rate": 50},
    "Other PHEV": {"battery": 10, "range": 30, "max_charge_rate": 3.3}
}

def calculate_readiness_score(location_type, power_availability, parking_spaces, electrical_panel_space, budget):
    """Calculate site readiness score (0-100)"""
    score = 0
    
    # Location type (residential vs commercial)
    if location_type == "Residential":
        score += 20  # Easier to install
    else:
        score += 10  # May require permits
    
    # Power availability
    if power_availability == "200A+ service":
        score += 30
    elif power_availability == "100-200A service":
        score += 20
    elif power_availability == "<100A service":
        score += 5
    
    # Parking spaces
    if parking_spaces == "Dedicated space near panel":
        score += 20
    elif parking_spaces == "Dedicated space, far from panel":
        score += 10
    else:
        score += 5
    
    # Electrical panel space
    if electrical_panel_space == "Plenty of space":
        score += 20
    elif electrical_panel_space == "Some space":
        score += 10
    else:
        score += 5
    
    # Budget
    if budget == "High":
        score += 10
    elif budget == "Medium":
        score += 7
    else:
        score += 3
    
    # Cap at 100
    return min(score, 100)

def recommend_charger(vehicle, location_type, daily_miles, power_availability, readiness_score):
    """Recommend charger based on inputs"""
    vehicle_data = vehicle_db[vehicle]
    is_phev = "PHEV" in vehicle
    
    # Basic logic for recommendation
    if is_phev:
        return "Level 1 (120V)", "PHEVs typically don't need more than Level 1 charging"
    
    if location_type == "Residential":
        if daily_miles < 50:
            if power_availability in ["<100A service", "100-200A service"]:
                return "Level 2 (240V)", "Best balance for residential use with your power availability"
            else:
                return "Level 2 (240V)", "Ideal for home charging with your power availability"
        else:
            return "Level 2 (240V)", "Best for residential use with higher daily mileage"
    else:  # Commercial
        if readiness_score > 70 and vehicle_data["max_charge_rate"] > 100:
            return "DC Fast Charger (150kW+)", "Commercial location with good readiness for fast charging"
        elif readiness_score > 50:
            return "DC Fast Charger (50kW)", "Good commercial option for multiple users"
        else:
            return "Level 2 (240V)", "Best commercial option given site constraints"

def main():
    st.set_page_config(page_title="EV Charger Recommendation Assistant", layout="wide")
    
    st.title("EV Charger Recommendation Assistant")
    st.write("This tool helps recommend the right EV charger based on your vehicle, location, and electrical infrastructure.")
    
    with st.expander("⚡ How to use this tool"):
        st.write("""
        1. Select your vehicle model or choose the closest match
        2. Provide information about your location and electrical setup
        3. Get charger recommendations and site readiness assessment
        4. Review detailed information about the recommended charger types
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Vehicle Information")
        vehicle = st.selectbox("Select your vehicle", list(vehicle_db.keys()))
        
        if vehicle in vehicle_db:
            vehicle_data = vehicle_db[vehicle]
            st.write(f"**Battery:** {vehicle_data['battery']} kWh")
            st.write(f"**Range:** {vehicle_data['range']} miles")
            st.write(f"**Max Charge Rate:** {vehicle_data['max_charge_rate']} kW")
        
        daily_miles = st.slider("Average daily miles driven", 10, 300, 40)
    
    with col2:
        st.subheader("Location Information")
        location_type = st.radio("Location type", ["Residential", "Commercial"])
        
        power_availability = st.selectbox("Electrical service available", 
                                        ["<100A service", "100-200A service", "200A+ service"])
        
        parking_spaces = st.selectbox("Parking space situation", 
                                    ["Dedicated space near panel", 
                                     "Dedicated space, far from panel", 
                                     "Shared/unassigned parking"])
        
        electrical_panel_space = st.selectbox("Electrical panel space", 
                                            ["Plenty of space", "Some space", "No space available"])
        
        budget = st.selectbox("Budget for installation", 
                            ["Low", "Medium", "High"])
    
    # Calculate readiness score
    readiness_score = calculate_readiness_score(location_type, power_availability, 
                                              parking_spaces, electrical_panel_space, budget)
    
    # Get recommendation
    recommended_charger, recommendation_reason = recommend_charger(
        vehicle, location_type, daily_miles, power_availability, readiness_score
    )
    
    st.divider()
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Recommendation")
        st.metric("Recommended Charger", recommended_charger)
        st.write(recommendation_reason)
        
        charger_data = charger_db[recommended_charger]
        st.write(f"**Power:** {charger_data['power']} kW")
        st.write(f"**Charge Rate:** {charger_data['charge_rate']}")
        st.write(f"**Installation:** {charger_data['installation']}")
        st.write(f"**Cost:** {charger_data['cost']}")
    
    with col4:
        st.subheader("Site Readiness Assessment")
        st.metric("Readiness Score", f"{readiness_score}/100")
        
        # Gauge for readiness score
        st.progress(readiness_score / 100)
        
        if readiness_score > 80:
            st.success("Excellent site readiness for EV charger installation!")
        elif readiness_score > 60:
            st.warning("Good readiness, but may require some upgrades")
        else:
            st.error("Site may require significant upgrades for optimal charger installation")
        
        st.write("**Factors considered:**")
        st.write(f"- Location type: {location_type}")
        st.write(f"- Power availability: {power_availability}")
        st.write(f"- Parking situation: {parking_spaces}")
        st.write(f"- Electrical panel space: {electrical_panel_space}")
        st.write(f"- Budget: {budget}")
    
    st.divider()
    
    st.subheader("All Charger Types Comparison")
    charger_df = pd.DataFrame.from_dict(charger_db, orient='index')
    st.dataframe(charger_df, use_container_width=True)

if __name__ == "__main__":
    main()