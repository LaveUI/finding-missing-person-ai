# missing-person-ai/missing-person-ai/README.md

# Missing Person AI

This project is a Flask application designed to assist in the search for missing persons. It provides a web interface and an API for users to report and search for missing individuals.

## Features

- User-friendly web interface for reporting missing persons.
- API endpoints for integrating with other services.
- Search functionality to find missing persons based on various criteria.

## Project Structure

```
missing-person-ai
├── app
│   ├── __init__.py
│   ├── routes.py
│   ├── models
│   │   └── person.py
│   ├── api
│   │   └── v1.py
│   ├── services
│   │   └── search.py
│   ├── utils
│   │   └── helpers.py
│   ├── templates
│   │   └── index.html
│   └── static
│       ├── css
│       │   └── main.css
│       └── js
│           └── main.js
├── tests
│   ├── conftest.py
│   └── test_routes.py
├── migrations
│   └── README
├── instance
│   └── config.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
├── run.py
├── wsgi.py
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/LaveUI/missing-person-ai.git
   cd missing-person-ai
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up the environment variables in the `.env` file.

5. Run the application:
   ```
   python run.py
   ```

## Usage

- Access the web interface at `http://localhost:5000`.
- Use the API endpoints for programmatic access to the application's features.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
