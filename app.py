from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import os
import boto3
from botocore.exceptions import ClientError
import uuid

app = Flask(__name__)
app.secret_key = 'capture_moments_secret_key_2024'

# Initialize DynamoDB client
# Ensure your AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)
# are configured in your environment or ~/.aws/credentials
dynamodb = boto3.resource('dynamodb')

# DynamoDB table names
PHOTOGRAPHERS_TABLE = dynamodb.Table('photographers')
GALLERY_IMAGES_TABLE = dynamodb.Table('gallery_images')
BOOKINGS_TABLE = dynamodb.Table('bookings')

# Sample data (for initial population if tables are empty, or to demonstrate structure)
# In a real app, you might have a script to populate this once.
initial_photographers_data = [
    {
        'id': 1,
        'name': 'Rajesh Kumar',
        'specialty': 'Wedding Photography',
        'location': 'Hyderabad',
        'experience': '8 years',
        'rating': 4.9,
        'image': 'https://images.pexels.com/photos/1222271/pexels-photo-1222271.jpeg?auto=compress&cs=tinysrgb&w=300&h=300&fit=crop'
    },
    {
        'id': 2,
        'name': 'Priya Sharma',
        'specialty': 'Portrait & Fashion',
        'location': 'Visakhapatnam',
        'experience': '6 years',
        'rating': 4.8,
        'image': 'https://images.pexels.com/photos/1239291/pexels-photo-1239291.jpeg?auto=compress&cs=tinysrgb&w=300&h=300&fit=crop'
    },
    {
        'id': 3,
        'name': 'Arjun Reddy',
        'specialty': 'Event Photography',
        'location': 'Vijayawada',
        'experience': '5 years',
        'rating': 4.7,
        'image': 'https://images.pexels.com/photos/1681010/pexels-photo-1681010.jpeg?auto=compress&cs=tinysrgb&w=300&h=300&fit=crop'
    }
]

initial_gallery_images_data = [
    {'image_url': 'https://images.pexels.com/photos/1024993/pexels-photo-1024993.jpeg?auto=compress&cs=tinysrgb&w=400&h=600&fit=crop'},
    {'image_url': 'https://images.pexels.com/photos/1043474/pexels-photo-1043474.jpeg?auto=compress&cs=tinysrgb&w=400&h=600&fit=crop'},
    {'image_url': 'https://images.pexels.com/photos/1729931/pexels-photo-1729931.jpeg?auto=compress&cs=tinysrgb&w=400&h=600&fit=crop'},
    {'image_url': 'https://images.pexels.com/photos/1444442/pexels-photo-1444442.jpeg?auto=compress&cs=tinysrgb&w=400&h=600&fit=crop'},
    {'image_url': 'https://images.pexels.com/photos/1616470/pexels-photo-1616470.jpeg?auto=compress&cs=tinysrgb&w=400&h=600&fit=crop'},
    {'image_url': 'https://images.pexels.com/photos/1024960/pexels-photo-1024960.jpeg?auto=compress&cs=tinysrgb&w=400&h=600&fit=crop'}
]

# Helper function to populate data (run once if tables are empty)
def populate_dynamodb_tables():
    # Populate photographers
    try:
        response = PHOTOGRAPHERS_TABLE.scan()
        if not response['Items']:
            print("Populating photographers table...")
            for photographer in initial_photographers_data:
                PHOTOGRAPHERS_TABLE.put_item(Item=photographer)
            print("Photographers populated.")
    except ClientError as e:
        print(f"Error checking/populating photographers table: {e.response['Error']['Message']}")

    # Populate gallery images
    try:
        response = GALLERY_IMAGES_TABLE.scan()
        if not response['Items']:
            print("Populating gallery images table...")
            for image in initial_gallery_images_data:
                GALLERY_IMAGES_TABLE.put_item(Item=image)
            print("Gallery images populated.")
    except ClientError as e:
        print(f"Error checking/populating gallery images table: {e.response['Error']['Message']}")

# Call population on startup (can be removed after initial setup)
with app.app_context():
    populate_dynamodb_tables()


# Remaining static data (can also be moved to DynamoDB if preferred)
locations = [
    'Hyderabad', 'Visakhapatnam', 'Vijayawada', 'Guntur', 'Nellore',
    'Kurnool', 'Rajahmundry', 'Tirupati', 'Eluru', 'Anantapur'
]

pricing_packages = [
    {
        'name': 'Basic Package',
        'price': '₹15,000',
        'duration': '4 hours',
        'photos': '100 edited photos',
        'features': ['Online gallery', 'High-resolution images', 'Basic editing']
    },
    {
        'name': 'Premium Package',
        'price': '₹25,000',
        'duration': '8 hours',
        'photos': '200 edited photos',
        'features': ['Online gallery', 'High-resolution images', 'Advanced editing', 'USB drive', 'Photobook']
    },
    {
        'name': 'Luxury Package',
        'price': '₹40,000',
        'duration': '12 hours',
        'photos': '300 edited photos',
        'features': ['Online gallery', 'High-resolution images', 'Advanced editing', 'USB drive', 'Photobook', 'Same-day highlights', 'Drone shots']
    }
]

@app.route('/')
def home():
    try:
        response = PHOTOGRAPHERS_TABLE.scan(Limit=3) # Get first 3 photographers
        photographers = response['Items']
    except ClientError as e:
        print(f"Error retrieving photographers for home page: {e.response['Error']['Message']}")
        photographers = [] # Fallback to empty list
    return render_template('index.html', photographers=photographers)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/portfolio')
def portfolio():
    try:
        response = GALLERY_IMAGES_TABLE.scan()
        gallery_images = [item['image_url'] for item in response['Items']]
    except ClientError as e:
        print(f"Error retrieving gallery images: {e.response['Error']['Message']}")
        gallery_images = [] # Fallback to empty list
    return render_template('portfolio.html', gallery_images=gallery_images)

@app.route('/photographers')
def photographers_page():
    try:
        response = PHOTOGRAPHERS_TABLE.scan()
        photographers = response['Items']
    except ClientError as e:
        print(f"Error retrieving all photographers: {e.response['Error']['Message']}")
        photographers = [] # Fallback to empty list
    return render_template('photographers.html', photographers=photographers)

@app.route('/photographer/<int:photographer_id>')
def photographer_detail(photographer_id):
    try:
        response = PHOTOGRAPHERS_TABLE.get_item(Key={'id': photographer_id})
        photographer = response.get('Item')
    except ClientError as e:
        print(f"Error retrieving photographer {photographer_id}: {e.response['Error']['Message']}")
        photographer = None

    if not photographer:
        flash('Photographer not found', 'error')
        return redirect(url_for('photographers_page'))
    return render_template('photographer_detail.html', photographer=photographer)

@app.route('/booking')
def booking():
    return render_template('booking.html', locations=locations, packages=pricing_packages)

@app.route('/book', methods=['POST'])
def book_session():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    event_type = request.form.get('event_type')
    location = request.form.get('location')
    date = request.form.get('date')
    package = request.form.get('package')
    message = request.form.get('message')

    booking_id = str(uuid.uuid4()) # Generate a unique ID for the booking
    booking_time = datetime.now().isoformat() # Timestamp for the booking

    try:
        BOOKINGS_TABLE.put_item(
            Item={
                'booking_id': booking_id,
                'name': name,
                'email': email,
                'phone': phone,
                'event_type': event_type,
                'location': location,
                'event_date': date, # Renamed to avoid conflict with 'date' type
                'package': package,
                'message': message,
                'booking_time': booking_time
            }
        )
        flash(f'Thank you {name}! Your booking request has been submitted. We will contact you soon.', 'success')
    except ClientError as e:
        print(f"Error saving booking to DynamoDB: {e.response['Error']['Message']}")
        flash('There was an error processing your booking. Please try again.', 'error')

    return redirect(url_for('booking'))

@app.route('/pricing')
def pricing():
    return render_template('pricing.html', packages=pricing_packages)

@app.route('/locations')
def locations_page():
    return render_template('locations.html', locations=locations)

@app.route('/events')
def events():
    return render_template('events.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')

    # In a real app, send email or save to database (e.g., another DynamoDB table for contacts)
    flash(f'Thank you {name}! Your message has been sent successfully.', 'success')
    return redirect(url_for('contact'))

if __name__ == '__main__':
    app.run(debug=True)