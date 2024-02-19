# GoIT_Web_homework_14
### REST API for saving your contacts

### https://contactsapi.fly.dev/docs - swagger docs
### https://contactsapi.fly.dev/redoc - documentation

- The FastAPI framework was used to create the API;
- SQLAlchemy ORM was used to work with the database;
- PostgreSQL was used as a database;
- Support for CRUD operations for contacts;
- Support for storing a contact's date of birth;
- API documentation provided;
- The Pydantic data validation module is used;
- An authentication mechanism has been implemented in the application;
- An authorization mechanism using JWT tokens has been implemented so that all operations with contacts are performed only by registered users;
- The user has access only to his contacts operations;
- A mechanism for verifying the registered user's e-mail has been implemented;
- The number of requests to your contact routes is limited. the speed of creating contacts for the user is limited;
- CORS enabled for REST API;
- The ability to update the user's avatar has been implemented.
- The Cloudinary service was used;
- Documentation created using Sphinx. For this, docstrings have been added to the necessary functions and class methods in the main modules.
- Unit tests the repository modules using the Unittest framework.
- Routes are covered with functional tests using the pytest framework.