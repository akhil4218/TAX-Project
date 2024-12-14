from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, get_jwt_identity
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os, re
from bson.objectid import ObjectId
from gridfs import GridFS
import datetime

TESTING_MODE = True

app = Flask(__name__)

CORS(app)

client = MongoClient("mongodb://localhost:27017/")
db = client['user_db']
user_collection = db['users']
ticket_collection = db['tickets']
fs = GridFS(db)
app.config["JWT_SECRET_KEY"] = "your_secret_key"  # Change this to a strong secret key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=1)
jwt = JWTManager(app)

# Blacklist for logged-out tokens
blacklist = set()

UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    username = data.get('username')  # Include username in signup
    password = data.get('password')
    role = data.get('role')

    if not TESTING_MODE:
        # Validate email format using regular expression
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"error": "Invalid email format"}), 400

        # Validate password format
        if not password or len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[\W_]', password):
            return jsonify({"error": "Password must be at least 8 characters long, contain one uppercase letter and one special character"}), 400

    # Validate presence of role and username
    if not role or not username:
        return jsonify({"error": "Username, password, and role are required"}), 400

    # Check if email or username already exists in the database
    if user_collection.find_one({"email": email}) or user_collection.find_one({"username": username}):
        return jsonify({"error": "Email or username already exists"}), 400

    # Hash the password and insert the user into the database
    hashed_password = generate_password_hash(password)
    user_collection.insert_one({
        "email": email,
        "username": username,
        "password": hashed_password,
        "role": role
    })
    
    return jsonify({"message": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')  # Use email as the unique identifier
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = user_collection.find_one({"email": email})  # Search by email
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    if not check_password_hash(user['password'], password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Generate JWT token
    access_token = create_access_token(identity=email)  # Using email as identity
    return jsonify({"message": "Login successful", "username": user["username"], "access_token": access_token}), 200

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # Get the unique identifier of the JWT token
    blacklist.add(jti)  # Add the token to the blacklist
    return jsonify({"message": "Logout successful"}), 200

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in blacklist  # Return True if the token is blacklisted

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()  # Get the email of the current user
    return jsonify({"message": f"Welcome {current_user}, you accessed a protected route!"}), 200

@app.route('/tickets', methods=['POST'])
def create_ticket():
    data = request.json
    username = data.get('username')
    title = data.get('title')
    description = data.get('description')

    if not username or not title or not description:
        return jsonify({"error": "Username, title, and description are required"}), 400

    ticket = {
        "username": username,
        "title": title,
        "description": description,
        "status": "Open",
        "messages": [],
        "files": []
    }

    ticket_id = ticket_collection.insert_one(ticket).inserted_id
    return jsonify({"message": "Ticket created successfully", "ticket_id": str(ticket_id)}), 201


@app.route('/tickets/<ticket_id>', methods=['GET'])
def view_ticket(ticket_id):
    ticket = ticket_collection.find_one({"_id": ObjectId(ticket_id)})
    
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    
    # Convert ObjectId to string for JSON serialization
    ticket['_id'] = str(ticket['_id'])
    
    return jsonify({"ticket": ticket}), 200

# Edit a specific ticket by ID
@app.route('/tickets/<ticket_id>', methods=['PUT'])
def edit_ticket(ticket_id):
    data = request.json
    title = data.get('title')
    description = data.get('description')

    if not title and not description:
        return jsonify({"error": "Title or description is required to update"}), 400

    ticket = ticket_collection.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    update_fields = {}
    if title:
        update_fields['title'] = title
    if description:
        update_fields['description'] = description

    ticket_collection.update_one(
        {"_id": ObjectId(ticket_id)},
        {"$set": update_fields}
    )

    return jsonify({"message": "Ticket updated successfully"}), 200

# Delete a specific ticket by ID
@app.route('/tickets/<ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    ticket = ticket_collection.find_one({"_id": ObjectId(ticket_id)})
    
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    
    # Delete the ticket from the collection
    ticket_collection.delete_one({"_id": ObjectId(ticket_id)})
    
    return jsonify({"message": "Ticket deleted successfully"}), 200
    

@app.route('/tickets/<ticket_id>/upload', methods=['POST'])
def upload_file(ticket_id):
    # Check if the ticket exists
    ticket = ticket_collection.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    # Check if a file is provided in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Save the file to MongoDB GridFS
    file_id = fs.put(file, filename=file.filename)

    # Add the file ID to the ticket in MongoDB
    ticket_collection.update_one(
        {"_id": ObjectId(ticket_id)},
        {"$push": {"files": str(file_id)}}
    )

    return jsonify({"message": "File uploaded successfully", "file_id": str(file_id)}), 200

@app.route('/tickets/<file_id>/download', methods=['GET'])
def download_file(file_id):
    try:
        file_data = fs.get(ObjectId(file_id))
        
        response = app.response_class(
            file_data.read(),
            mimetype=file_data.content_type if file_data.content_type else 'application/octet-stream',
        )
        response.headers["Content-Disposition"] = f"attachment; filename={file_data.filename}"
        
        return response, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404



@app.route('/tickets/<ticket_id>/message', methods=['POST'])
def add_message(ticket_id):
    data = request.json
    message = data.get('message')

    if not message:
        return jsonify({"error": "Message is required"}), 400

    ticket = ticket_collection.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    ticket_collection.update_one(
        {"_id": ObjectId(ticket_id)},
        {"$push": {"messages": message}}
    )

    return jsonify({"message": "Message added successfully"}), 200

@app.route('/tickets/<ticket_id>/status', methods=['PATCH'])
def change_status(ticket_id):
    data = request.json
    status = data.get('status')

    if not status:
        return jsonify({"error": "Status is required"}), 400

    ticket = ticket_collection.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    ticket_collection.update_one(
        {"_id": ObjectId(ticket_id)},
        {"$set": {"status": status}}
    )

    return jsonify({"message": "Status updated successfully"}), 200

@app.route('/tickets', methods=['GET'])
def view_tickets():
    username = request.args.get('username')

    if not username:
        return jsonify({"error": "Username is required"}), 400

    if username == 'admin':
        tickets = list(ticket_collection.find())
    else:
        tickets = list(ticket_collection.find({"username": username}))

    for ticket in tickets:
        ticket['_id'] = str(ticket['_id'])

    return jsonify({"tickets": tickets}), 200

if __name__ == '__main__':
    app.run(debug=True)
