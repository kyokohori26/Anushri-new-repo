from flask import Flask, render_template, request, session, redirect, url_for
import random
import time
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize session variables
@app.before_request
def init_session():
    # Essential session variables
    if 'attempts' not in session:
        session['attempts'] = 0
    if 'booking_token' not in session:
        session['booking_token'] = None
    if 'selected_seat' not in session:
        session['selected_seat'] = None
    
    # New variables for better state management
    if 'otp_attempts' not in session:
        session['otp_attempts'] = 0
    if 'payment_completed' not in session:
        session['payment_completed'] = False

# Homepage Route
@app.route('/')
def homepage():
    session.clear()
    session['attempts'] = session.get('attempts', 0) + 1
    return render_template('homepage.html', attempts=session['attempts'])

# Search Page Route
@app.route('/search', methods=['POST'])
def search():
    destinations = {
        "Delhi": ["Lulla Nagar, Maharashtra", "Bhosari, Pune", "Mumbai"],
        "Mumbai": ["Dharavi Slum Tour", "Bandra Underwater", "Delhi"]
    }
    origin = request.form.get('origin', 'Delhi')
    autocorrect_target = destinations.get(origin, ["Unknown"])[session['attempts'] % 3]
    
    # Simulate absurd loading process
    time.sleep(2)
    
    return render_template('search.html', 
                          origin=origin,
                          autocorrect_target=autocorrect_target)

# Seat Selection Route
@app.route('/seat_selection')
def seat_selection():
    # Generate random seat statuses
    seats = {}
    for row in ['A', 'B', 'C', 'D', 'E', 'F']:
        for num in range(1, 15):
            seat_id = f"{row}-{num}"
            status = random.choices(
                ['available', 'taken', 'mla_quota', 'bad_vastu', 'cursed', 'vacation'],
                weights=[0.1, 0.3, 0.1, 0.1, 0.1, 0.1]
            )[0]
            seats[seat_id] = status
    
    # Ensure at least one haunted seat
    seats['F-13'] = 'haunted'
    
    # Add at least one available seat
    available_seats = [seat for seat, status in seats.items() if status == 'available']
    if not available_seats:
        seats[random.choice(list(seats.keys()))] = 'available'
    
    return render_template('seat_selection.html', seats=seats)

# Cart Route
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    session['selected_seat'] = request.form['seat_id']
    
    # Generate absurd fees
    fees = {
        'base_fare': random.randint(1000, 1500),
        'chair_usage': random.randint(100, 200),
        'digital_ink': random.randint(50, 100),
        'convenience_fee': random.randint(70, 100),
        'convenience_fee_fee': random.randint(20, 50),
        'emotional_damage': random.randint(150, 250)
    }
    session['fees'] = fees
    session['otp_attempts'] = 0  # Reset OTP attempts for new payment
    
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    return render_template('cart.html', 
                          seat=session['selected_seat'],
                          fees=session.get('fees', {}))

# Payment Route
@app.route('/payment')
def payment():
    # Reset payment state if coming from error
    session['payment_completed'] = False
    return render_template('payment.html')

# OTP Verification Route
@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    user_otp = request.form['otp']
    session['otp_attempts'] = session.get('otp_attempts', 0) + 1
    
    # Always fail first 3 attempts, succeed on 4th
    if session['otp_attempts'] < 4:
        # Generate a fake failure reason
        failure_reasons = [
            "OTP expired before it arrived",
            "Pigeon got lost carrying your OTP",
            "Stranger forgot to whisper the numbers",
            "Server was on chai break"
        ]
        session['error_message'] = random.choice(failure_reasons)
        return redirect(url_for('payment_error'))
    else:
        # On 4th attempt, success!
        session['payment_completed'] = True
        return redirect(url_for('confirmation'))

@app.route('/payment_error')
def payment_error():
    # Show different Bunty GIFs for each attempt
    bunty_gifs = [
        "https://media.giphy.com/media/l0HlG8vJXW0q5Q5iU/giphy.gif",  # Mild crying
        "https://media.giphy.com/media/3o7TKsQ8UQ4l4LhGz6/giphy.gif",  # Moderate crying
        "https://media.giphy.com/media/3o7TKYnjG9bcRA5nD2/giphy.gif"   # Extreme sobbing
    ]
    
    gif_index = min(session['otp_attempts'] - 1, len(bunty_gifs) - 1)
    
    return render_template('payment_error.html',
                          error_message=session.get('error_message', 'Unknown error'),
                          bunty_gif=bunty_gifs[gif_index])

# Confirmation Route
@app.route('/confirmation')
def confirmation():
    if not session.get('payment_completed', False):
        return redirect(url_for('homepage'))
    
    # Generate absurd token number
    token = f"#{random.randint(1000,9999)}{chr(random.randint(65,90))}"
    session['booking_token'] = token
    
    return render_template('confirmation.html', token=token)

# Session Timeout Route
@app.route('/session_timeout')
def session_timeout():
    return render_template('session_timeout.html')

if __name__ == '__main__':
    app.run(debug=True)