# Metrics Handler
An application that handles book management and tracks various metrics.

## Introduction
This app is designed to manage books and their associated metrics efficiently. It offers real-time data handling and performance metrics analysis. Also there is an option to post metrics for testing purposes.

## Requirements
- MongoDB
- Python (version 3.12.1)
- Node.js

## Installation
### Backend Setup
1. Install MongoDB and set it up as per the official documentation. (https://www.mongodb.com/atlas/database)
2. Install Python dependencies:
```pip install -r requirements.txt```

### Frontend Setup
1. Ensure Node.js is installed.
2. Install frontend dependencies:
```npm install```

## Usage
- To run the backend:
```python app.py```

- To start the frontend:
```npm start```

## Considerations
1. **Use of NoSQL Databases**: For rapid insertion of metrics data.
2. **Database Indexing**: Indexes are set on the timestamp column and other relevant columns for efficient searching.
3. **Cache Implementation**: A cache system is implemented to enhance query performance.
4. **Cache Maintenance Task**: Regular cache updates are maintained.
5. **Zero Value Function**: A function is included to insert '0' values for metrics like error counts.
6. **Real-time Data and Sockets**: Web sockets are used for real-time data handling.
7. **User Interface for Data Visualization**: The frontend supports adjusting intervals for viewing metrics averages (day, hour, minute).
8. **Time Zone Handling**: All data is stored in UTC.
9. **API Design and Security**: The application has a secure API with token-based security measures.
10. **Testing for Accuracy**: Unit tests ensure the accuracy of metric calculations and data handling.

## Next Steps
1. **Database Features Evaluation**: Investigate specific database features like series collections and triggers on insertions in MongoDB to enhance real-time data management.
2. **Containerization and Kubernetes Integration**: Implement container support for simplified deployment and scalable infrastructure management using Kubernetes.
3. **Scalability of Data Storage**: Explore strategies for scaling data storage to accommodate growing metrics data.
4. **Data Retention Policy**: Develop a data storage duration policy.
5. **Data Aggregation Strategies**: Consider pre-aggregating data at the time of insertion for optimized query performance.
6. **Evaluating Redis for Caching**: Assess the use of Redis for caching to improve application performance.







