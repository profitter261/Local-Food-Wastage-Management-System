# Local-Food-Wastage-Management-System
Food wastage is a significant issue, with many households and restaurants discarding surplus food while numerous people struggle with food insecurity. This project aims to develop a Local Food Wastage Management System, where:
1) Restaurants and individuals can list surplus food.
2) NGOs or individuals in need can claim the food.
3) SQL stores available food details and locations.
4) A Streamlit app enables interaction, filtering, CRUD operation and visualization.

## Approach :-
1) Data Preparation
Utilize a provided dataset containing food donation records.
Ensure consistency and accuracy in data formatting.
2) Database Creation
Store food availability data in SQL tables.
Implement CRUD operations for updating, adding, and removing records.
3) Data Analysis.
Identify food wastage trends based on categories, locations, and expiry dates.
Generate reports for effective food distribution.
4) Application Development
Develop a Streamlit-based user interface to:
i) Display output of the  15 SQL queries .
ii) Provide filtering options based on city, provider, food type, and meal type.
iii) Show contact details of providers for direct coordination.
5. Deployment
Deploy the Streamlit application for accessibility and real-time interaction

## Data Flow and Architecture
1) Data Storage:
Use SQL database to store food donations, locations, and provider details.
2) Processing Pipeline:
Do analysis and generate insights into food wastage patterns.
3) Deployment:
Develop a Streamlit-based interface for food providers and seekers.

## Dataset
1) Providers Dataset : providers_data.csv
3) Receivers Dataset: receivers_data.csv
2) Food Listings Dataset: food_listings_data.csv
4) Claims Dataset: claims_data.csv



