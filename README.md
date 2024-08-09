# Document Query Application

## Overview

This application allows users to upload, query, and manage documents through a web interface. It supports PDF, DOCX, and TXT files. Users can register, log in, upload documents, search within their documents, view their query history, and download their chat history. The application uses encryption to securely store document content.

## Features

- **User Authentication**: Register and log in to access your document management features.
- **Document Upload**: Upload PDF, DOCX, and TXT files.
- **Document Query**: Search through uploaded documents based on query strings.
- **Query History**: View a history of your queries and responses.
- **Download History**: Download your query history as a text file.

## Requirements

- Python 3.x
- Streamlit
- SQLite3
- hashlib
- cryptography
- PyPDF2
- python-docx
- pandas

## Usage
### Register: 
Create a new account by entering a username and password.
### Login: 
Access your account with your username and password.
### Upload Document: 
Upload PDF, DOCX, or TXT files to the system.
### Query Document: 
Search for specific text within your uploaded documents.
### History: 
View and manage your query history.
### Download History: 
Download your query history as a .txt file.
## Encryption
The application uses cryptography.fernet for encrypting and decrypting document content. This ensures that documents are stored securely in the database.

## Database
The application uses an SQLite database (app.db) to store:

### Users: 
User credentials (hashed passwords).
### Documents: 
Encrypted document content.
### Queries: 
Query history and responses.
## Contributing
Feel free to fork the repository and submit pull requests. Issues and suggestions are welcome.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
