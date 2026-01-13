from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from groq import Groq
import secrets
import json
import os
import smtplib
from email.message import EmailMessage
import random
import string
import uuid
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Pull the secret key from the environment
# Change this line:
app.secret_key = "skill_swap_permanent_key_2026"

# Also, add this to ensure cookies are handled correctly by the browser
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(days=7)
)

# Pull the Groq key from the environment
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Updated Email Helper using Environment Variables
def send_verification_email(user_email, token):
    sender = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASS')
    
    msg = EmailMessage()
    msg['From'] = f"SKILL SWAP <{sender}>"
    msg['To'] = user_email
    # ... (rest of your email logic stays the same)
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

# --- CONFIGURATION ---
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# --- DATABASE PERSISTENCE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'database.json')

def load_db():
    # Start with the absolute default state
    default_users = {
        "demo@test.com": {
            "email": "demo@test.com", "name": "Design Guru", 
            "password": "123", "skill": "Photoshop", 
            "credits": 50, "verified": True, "email_verified": True, 
            "goals": [], "history": [], "ratings": [], "avg_rating": 5.0,
            "streak": 0, "last_quiz_date": "", "active_projects": []
        }
    }
    default_bounties = [
    {
        "id": "ai-sys-303",
        "type": "ai",
        "title": "Neural Link Calibration",
        "description": "The AI core requires a manual frequency sync. Match the system oscillation to earn credits.",
        "reward": 150,
        "status": "Open",
        "progress": 0,
        "posted_by": "system",   # Added this
        "accepted_by": None      # Added this
    },
    {
        "id": "ai-sys-404",
        "type": "ai",
        "title": "Database Optimization",
        "description": "Identify and prune redundant nodes in the neural cluster. High precision required.",
        "reward": 300,
        "status": "Open",
        "progress": 0,
        "posted_by": "system",   # Added this
        "accepted_by": None      # Added this
    }
]
    
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            try:
                data = json.load(f)
                users = data.get("users", default_users)
                requests = data.get("requests", [])
                notifications = data.get("notifications", [])
                # Ensure bounties are loaded or use defaults
                bounties = data.get("bounties", default_bounties)
                return users, requests, notifications, bounties
            except:
                return default_users, [], [], default_bounties
    return default_users, [], [], default_bounties
    

def save_db():
    data_to_save = {
        "users": users_db, 
        "requests": swap_requests, 
        "notifications": notifications_db,
        "bounties": bounties_db
    }
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(data_to_save, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving database: {e}")
        return False
    
# Initialize global databases
users_db, swap_requests, notifications_db, bounties_db = load_db()

# --- HELPERS ---

# In get_current_user() helper:
def get_current_user():
    email = session.get('email')  # Changed from 'user_email'
    return users_db.get(email) if email else None

# In /login route:
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = users_db.get(email)
    
    if user and user['password'] == password:
        session.clear()
        session.permanent = True
        session['email'] = email # Use 'email' to match auth route
        session.modified = True 
        return jsonify({"status": "success", "redirect": "/dashboard"})
    return jsonify({"status": "error", "message": "Invalid Credentials"}), 401

def send_verification_email(user_email, token):
    msg = EmailMessage()
    
    # 1. CHANGE SENDER NAME
    # Format: "Name <email@address.com>"
    msg['From'] = "SKILL SWAP <prajaktav416@gmail.com>"
    msg['To'] = user_email
    msg['Subject'] = '🚀 Welcome to Skill Swap - Verify Your Identity'

    # 2. IMPROVED WELCOMING MESSAGE (HTML Version)
    html_content = f"""
    <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
                <h2 style="color: #6366f1;">Welcome to the Studio!</h2>
                <p>Hello,</p>
                <p>We're thrilled to have you join <b>Skill Swap</b>. You're one step away from connecting with experts and mastering new intelligence.</p>
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                    <p style="font-size: 14px; color: #64748b; margin-bottom: 10px;">YOUR VERIFICATION CODE</p>
                    <h1 style="letter-spacing: 5px; color: #1e293b; margin: 0;">{token}</h1>
                </div>
                <p>Enter this code in your browser to activate your account and claim your starting credits.</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #94a3b8;">If you did not request this, please ignore this email.</p>
                <p style="font-size: 12px; font-weight: bold; color: #6366f1;">Team Skill Swap</p>
            </div>
        </body>
    </html>
    """
    
    msg.set_content(f"Welcome to Skill Swap! Your verification code is: {token}") # Plain text fallback
    msg.add_alternative(html_content, subtype='html') # High-quality HTML version

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('prajaktav416@gmail.com', 'hmaz itdp ajlm vdiz')
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False
    
def generate_secure_room():
    parts = [''.join(secrets.choice(string.ascii_lowercase) for _ in range(n)) for n in [3, 4, 3]]
    return '-'.join(parts)

def add_notification(email, message, type="info"):
    notifications_db.append({
        "id": str(uuid.uuid4())[:8],
        "email": email,
        "message": message,
        "type": type,
        "timestamp": datetime.now().strftime("%H:%M"),
        "read": False
    })
    # MUST pass the globals to save_db
    save_db()

def ask_ai(prompt):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"AI Error: {e}")
        return "ERROR"

def get_all_swaps_for_user(email):
    results = []
    for s in swap_requests:
        if s['from'] == email or s['to'] == email:
            partner_email = s['to'] if s['from'] == email else s['from']
            partner = users_db.get(partner_email, {"name": "User"})
            swap_copy = s.copy()
            swap_copy['partner_name'] = partner.get('name')
            results.append(swap_copy)
    return results

# --- AUTHENTICATION ROUTES ---

@app.route('/auth', methods=['POST'])
def auth():
    data = request.form
    action, email, password = data.get('action'), data.get('email'), data.get('password')
    
    if action == 'register':
        if email in users_db: return jsonify({"status": "error", "message": "User exists!"})
        otp = str(random.randint(100000, 999999))
        if send_verification_email(email, otp):
            users_db[email] = {
                "email": email, "name": data.get('name', 'New Member'),
                "password": password, "skill": data.get('skill', 'Learning'),
                "credits": 20, "verified": False, "email_verified": False, 
                "otp": otp, "goals": [], "history": [], "ratings": [], "avg_rating": 0.0,
                "streak": 0, "last_quiz_date": "", "active_projects": []
            }
            save_db()
            session.permanent = True
            session['email'] = email # CONSISTENT KEY
            return jsonify({"status": "pending_verification", "email": email, "redirect": "/verify_page"})
            
    else: # Login logic
        user = users_db.get(email)
        if user and user['password'] == password:
            session.permanent = True
            session['email'] = email # CONSISTENT KEY
            target = "/dashboard" if user.get('email_verified') else "/onboarding"
            return jsonify({"status": "success", "redirect": target})
            
    return jsonify({"status": "error", "message": "Invalid credentials."})

@app.route('/confirm_email', methods=['POST'])
def confirm_email():
    email = request.form.get('email') or session.get('user_email')
    user = users_db.get(email)
    if user and user.get('otp') == request.form.get('code'):
        user['email_verified'] = True
        save_db()
        return jsonify({"status": "success", "redirect": "/onboarding"})
    return jsonify({"status": "error", "message": "Invalid code."})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- NAVIGATION & DASHBOARD ---

@app.route('/')
def index():
    if get_current_user(): return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    user = get_current_user()
    if not user: 
        return redirect(url_for('index'))
    if not user.get('email_verified'): 
        return redirect(url_for('verify_page', email=user['email']))
    
    # Sort bounties to show the 3 most recent 'Open' ones on the dashboard
    recent_bounties = [b for b in bounties_db if b.get('status') == 'Open']
    recent_bounties = recent_bounties[-3:] # Get the last 3 added
    
    greeting = f"Ready to master something new, {user['name']}?"
    
    return render_template('dashboard.html', 
                           user=user, 
                           bounties=recent_bounties, 
                           greeting=greeting)

@app.route('/debug_session')
def debug_session():
    return {
        "session_content": dict(session),
        "secret_key_present": app.secret_key is not None,
        "permanent": session.permanent
    }

@app.route('/connections')
def connections():
    user = get_current_user()
    if not user: 
        return redirect(url_for('auth_page'))
    
    # 1. Filter swaps from the global swap_requests list
    # We only want swaps where the current user is either the sender or receiver
    active = [
        s for s in swap_requests 
        if s.get('status') == 'matched' and (s.get('from') == user['email'] or s.get('to') == user['email'])
    ]
    
    # 2. Get history from user dict
    history = user.get('history', [])
    
    # 3. Calculate dynamic stats for the cards
    # Yield = total credits earned (positive amounts in history)
    yield_val = sum(h.get('amount', 0) for h in history if h.get('amount', 0) > 0)
    
    # Expenditure = total credits spent (negative amounts in history)
    spent_val = abs(sum(h.get('amount', 0) for h in history if h.get('amount', 0) < 0))
    
    return render_template('connections.html', 
                           user=user, 
                           active_swaps=active, 
                           scheduled_swaps=[], 
                           history_data=history,
                           yield_val=yield_val,
                           spent_val=spent_val)
# --- PROFILE MANAGEMENT ---

@app.route('/profile')
def profile():
    user = get_current_user()
    if not user: return redirect(url_for('auth_page'))
    return render_template('profile.html', user=user)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    user = get_current_user()
    if not user: return jsonify({"status": "error"}), 401
    new_name, new_skill = request.form.get('name'), request.form.get('skill')
    if new_name and new_skill:
        user['name'], user['skill'], user['verified'] = new_name, new_skill, False
        save_db()
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Missing fields"})

@app.route('/add_goal', methods=['POST'])
def add_goal():
    user = get_current_user()
    if not user: return jsonify({"status": "error"}), 401
    
    goal = request.form.get('goal') # This comes from the profile page input
    if goal:
        if 'goals' not in user:
            user['goals'] = []
            
        if goal not in user['goals']:
            user['goals'].append(goal)
            save_db() # Saves to database.json
            return jsonify({"status": "success"})
            
    return jsonify({"status": "error", "message": "Invalid goal"})

@app.route('/delete_goal', methods=['POST'])
def delete_goal():
    user = get_current_user()
    if not user: return jsonify({"status": "error"}), 401
    
    goal_to_remove = request.form.get('goal')
    if 'goals' in user and goal_to_remove in user['goals']:
        user['goals'].remove(goal_to_remove)
        save_db() # Syncs to database.json
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Goal not found"})

# --- SWAP ENGINE & WORKSPACE ---

@app.route('/send_swap_request', methods=['POST'])
def send_swap_request():
    sender = get_current_user()
    receiver_email, message = request.form.get('receiver_email'), request.form.get('message')
    if not sender: return jsonify({"status": "error"}), 401
    if sender['credits'] < 5: return jsonify({"status": "error", "message": "Need 5 credits!"})
    
    new_req = {
        "id": str(uuid.uuid4())[:8], 
        "from": sender['email'], 
        "to": receiver_email, 
        "message": message, 
        "status": "pending",
        "timestamp": datetime.now().strftime("%Y-%m-%d")
    }
    swap_requests.append(new_req)
    sender['credits'] -= 5
    add_notification(receiver_email, f"New Mastery Swap requested by {sender['name']}", "info")
    save_db()
    return jsonify({"status": "success", "message": "Request Sent!"})

@app.route('/accept_request', methods=['POST'])
def accept_request():
    user = get_current_user()
    swap_id = request.form.get('swap_id')
    sender_email = request.form.get('sender_email')
    
    if not user: return jsonify({"status": "error"}), 401
    for req in swap_requests:
        if (req.get('id') == swap_id) or (req['from'] == sender_email and req['to'] == user['email']):
            req['status'] = 'matched'
            
            # --- UPDATED: Professional Room ID ---
            req['room_id'] = generate_secure_room() 
            
            req['scheduled_time'] = (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")
            add_notification(req['from'], f"Match Confirmed! Join Workspace: {req['room_id']}", "success")
            save_db()
            return jsonify({"status": "success", "room_id": req['room_id']})
    return jsonify({"status": "error", "message": "Request not found"})

@app.route('/api/finalize-session/<room_id>', methods=['POST'])
def api_finalize_session(room_id):
    """Handles the credit transfer and rating when 'End & Rate' is clicked."""
    rating = request.json.get('rating', 5)
    current_user_email = session.get('user_email')
    
    if not current_user_email:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    # 1. Find the swap in the global list
    target_swap = next((s for s in swap_requests if s.get('room_id') == room_id and s.get('status') == 'matched'), None)
    
    if not target_swap:
        return jsonify({"status": "error", "message": "Active session not found"}), 404

    # 2. Determine Roles
    # Logic: 'from' initiated, 'to' accepted. 
    # Usually, the person who initiates ('from') is paying for the skill.
    learner_email = target_swap['from']
    teacher_email = target_swap['to']
    cost = float(target_swap.get('cost', 5.0)) # Use 5.0 as default to match your request logic

    # 3. Transfer Credits
    if learner_email in users_db and teacher_email in users_db:
        users_db[learner_email]['credits'] -= cost
        users_db[teacher_email]['credits'] += cost
        
        # 4. Update History Entry
        history_entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "topic": target_swap.get('message', 'Skill Exchange'),
            "status": "Completed",
            "rating": int(rating)
        }

        # Add to Learner's history (Negative amount)
        learner_history = history_entry.copy()
        learner_history["partner"] = users_db[teacher_email]['name']
        learner_history["amount"] = -cost
        users_db[learner_email].setdefault('history', []).insert(0, learner_history)

        # Add to Teacher's history (Positive amount)
        teacher_history = history_entry.copy()
        teacher_history["partner"] = users_db[learner_email]['name']
        teacher_history["amount"] = cost
        users_db[teacher_email].setdefault('history', []).insert(0, teacher_history)

        # 5. Handle Rating
        users_db[teacher_email].setdefault('ratings', []).append(int(rating))
        r_list = users_db[teacher_email]['ratings']
        users_db[teacher_email]['avg_rating'] = round(sum(r_list) / len(r_list), 1)

    # 6. Mark swap as completed and remove from active list
    target_swap['status'] = 'completed'
    
    # 7. Persist to database.json
    save_db()
    
    return jsonify({
        "status": "success", 
        "message": f"Session closed. {cost} credits transferred to expert."
    })

@app.route('/workspace/<project_id>')
def workspace(project_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth_page'))
    
    # 1. Check if this is a Bounty (System or Human)
    project = next((b for b in bounties_db if b['id'] == project_id), None)
    mode = 'bounty'

    # 2. If not a bounty, check the user's manual active_projects
    if not project:
        project = next((p for p in user.get('active_projects', []) if p['id'] == project_id), None)
        mode = 'solo'

    # 3. Security Check: Does the user have access?
    # Either they are the one who accepted the bounty, or they created the manual project.
    if project:
        # If it's a bounty, ensure the current user is the one who accepted it
        if mode == 'bounty' and project.get('accepted_by') != user['email']:
             return "Access Denied: You have not accepted this mission.", 403
             
        return render_template('workspace.html', 
                               project=project, 
                               mode=mode,
                               title=project.get('title', 'Neural Workspace'))

    return "Project not found", 404

# --- AI & NOTIFICATIONS ---

@app.route('/get_notifications')
def get_notifications():
    user = get_current_user()
    if not user: return jsonify([])
    return jsonify([n for n in notifications_db if n['email'] == user['email'] and not n['read']])

@app.route('/mark_read', methods=['POST'])
def mark_read():
    user = get_current_user()
    for n in notifications_db:
        if n['email'] == user['email']: n['read'] = True
    save_db()
    return jsonify({"status": "success"})

@app.route('/magic_search', methods=['POST'])
def magic_search():
    query = request.form.get('query')
    context = "".join([f"Name: {u['name']}, Teaches: {u['skill']}\n" for u in users_db.values()])
    prompt = f"Query: '{query}'. Teachers:\n{context}\nReturn ONLY a JSON list of objects with 'name', 'skill', and 'reason'."
    try:
        res = ask_ai(prompt).replace('```json', '').replace('```', '').strip()
        return jsonify({"status": "success", "matches": res})
    except: return jsonify({"status": "error"})

@app.route('/get_verification_challenge', methods=['POST'])
def get_verification_challenge():
    user = get_current_user()
    skill = request.form.get('skill') or user.get('skill')
    prompt = f"Generate one fundamental question to test a beginner's knowledge in {skill}. Return ONLY the question."
    return jsonify({"status": "success", "question": ask_ai(prompt)})

@app.route('/verify_answer', methods=['POST'])
def verify_answer():
    user = get_current_user()
    prompt = f"Skill: {user['skill']}. Answer: '{request.form.get('answer')}'. Return 'PASS' or 'FAIL' only."
    if "PASS" in ask_ai(prompt).upper():
        user['credits'] += 10; user['verified'] = True; save_db()
        return jsonify({"status": "success", "message": "Expertise Verified!"})
    return jsonify({"status": "fail"})

# --- STATIC VIEW ROUTES & NEW LOGIC ---

@app.route('/auth_page')
def auth_page(): return render_template('auth.html', mode=request.args.get('mode', 'login'))


@app.route('/verify_page')
def verify_page(): return render_template('verify.html', email=request.args.get('email'))

@app.route('/onboarding')
def onboarding():
    user = get_current_user()
    if not user or user.get('verified'): return redirect(url_for('dashboard'))
    return render_template('onboarding.html')

@app.route('/resend_otp', methods=['POST'])
def resend_otp():
    email = request.form.get('email') or session.get('user_email')
    user = users_db.get(email)
    
    if user:
        new_otp = str(random.randint(100000, 999999))
        user['otp'] = new_otp
        save_db()
        
        if send_verification_email(email, new_otp):
            return jsonify({"status": "success", "message": "New code sent!"})
    
    return jsonify({"status": "error", "message": "Failed to resend. Try again later."})

@app.route('/my_projects')
def my_projects():
    # 1. Properly unpack the tuple into individual lists/dicts
    users_list, swap_requests_list, notifications_list, bounties_list = load_db()
    
    # 2. MATCH THE SESSION KEY: Your login uses 'email', not 'user_email'
    user_email = session.get('email') 
    
    # 3. Lookup user in the dictionary returned by load_db
    user = users_list.get(user_email)

    if not user:
        return redirect(url_for('auth_page'))

    # 4. Get manual projects from user dict
    manual_projects = user.get('active_projects', [])

    # 5. Get bounties the user has accepted from the global bounties_list
    accepted_bounties = [
        b for b in bounties_list 
        if b.get('accepted_by') == user_email and b.get('status') == 'Active'
    ]

    return render_template('my_projects.html', 
                           user=user, 
                           projects=manual_projects, 
                           active_bounties=accepted_bounties)

@app.route('/create_project', methods=['POST'])
def create_project():
    user = get_current_user()
    data = request.json
    
    new_bounty = {
        "id": str(uuid.uuid4())[:8],
        "creator_email": user['email'], # Essential for Step 3 (Filtering)
        "title": data.get('title'),
        "skill": data.get('skill'),
        "description": data.get('goal'),
        "reward": data.get('reward', 50), # The credit reward
        "status": "Open", # Makes it visible on the board
        "accepted_by": None,
        "progress": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    bounties_db.append(new_bounty)
    save_db()
    
    return jsonify({"status": "success", "message": "Mission Broadcasted to Marketplace"})

@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    user = get_current_user()
    if not user:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    # Check if already completed today
    today_str = str(date.today())
    if user.get('last_quiz_date') == today_str:
        return jsonify({
            "status": "error", 
            "message": "Directive already cleared for today. Return in 24h."
        })
    
    data = request.json
    skill = data.get('skill')
    domain = data.get('domain')
    level = data.get('level')
    
    streak_mod = (user.get('streak', 0) * 0.05)
    
    prompt = f"""
    Create a multiple-choice quiz question for:
    Skill: {skill}
    Domain: {domain}
    Difficulty Level: {level} (Adjusted by streak: {streak_mod})
    
    Return ONLY JSON format:
    {{
      "question": "The question text",
      "options": ["A", "B", "C", "D"],
      "answer": "The correct option index (0-3)",
      "explanation": "Brief context why"
    }}
    """
    
    try:
        quiz_json = ask_ai(prompt)
        quiz_data = json.loads(quiz_json.replace('```json', '').replace('```', '').strip())
        
        session['current_quiz_answer'] = str(quiz_data['answer'])
        session['quiz_points'] = 5 if level == "Easy" else 10 if level == "Mid" else 20
        
        return jsonify({"status": "success", "quiz": quiz_data})
    except Exception as e:
        return jsonify({"status": "error", "message": "AI generation failed."})

@app.route('/verify_quiz', methods=['POST'])
def verify_quiz():
    user = get_current_user()
    user_choice = request.form.get('choice')
    correct_choice = session.get('current_quiz_answer')
    
    if user_choice == correct_choice:
        points = session.get('quiz_points', 5)
        user['credits'] += points
        user['streak'] = user.get('streak', 0) + 1
        user['last_quiz_date'] = str(date.today()) 
        
        save_db()
        return jsonify({
            "status": "success", 
            "message": f"Correct! +{points} Credits. Streak: {user['streak']}!", 
            "new_streak": user['streak']
        })
    
    user['streak'] = 0 
    user['last_quiz_date'] = str(date.today())
    save_db()
    return jsonify({"status": "fail", "message": "Incorrect. Streak reset to 0."})

@app.route('/leaderboard')
def leaderboard_view():
    user = get_current_user()
    return render_template('leaderboard.html', user=user)

@app.route('/leaderboard_data')
def leaderboard_data():
    # Sort users by streak first, then credits
    all_users = list(users_db.values())
    ranked = sorted(all_users, key=lambda x: (x.get('streak', 0), x.get('credits', 0)), reverse=True)
    return jsonify(ranked[:10])

# --- CONSOLIDATED PROJECT & WORKSPACE LOGIC ---

# --- CLEANED PROJECT & WORKSPACE LOGIC ---


@app.route('/get_project/<id>')
def get_project(id):
    user = get_current_user()
    
    # Check Bounties first
    project = next((b for b in bounties_db if b['id'] == id), None)
    
    # If not a bounty, check user's manual projects
    if not project:
        project = next((p for p in user.get('active_projects', []) if p['id'] == id), None)
    
    if project:
        return jsonify({
            "status": "success",
            "project": {
                "learning": project.get('title') or project.get('learning'),
                "progress": project.get('progress', 0)
            }
        })
    return jsonify({"status": "error", "message": "Project not found"}), 404

@app.route('/update_project/<id>', methods=['POST'])
def update_project(id):
    user = get_current_user()
    data = request.json
    new_progress = int(data.get('progress', 0))

    # 1. Try Bounty Update
    bounty = next((b for b in bounties_db if b['id'] == id), None)
    if bounty and bounty.get('accepted_by') == user['email']:
        # Prevent double-payouts if already completed
        if bounty.get('status') == 'Completed':
            return jsonify({"status": "error", "message": "Already rewarded"})

        bounty['progress'] = new_progress
        
        if new_progress == 100:
            bounty['status'] = 'Completed'
            # PAYOUT LOGIC:
            reward = int(bounty.get('reward', 0))
            user['credits'] = user.get('credits', 0) + reward
            message = f"Operation Cleared. {reward} Credits deposited."
        else:
            message = "Ledger Updated."

        save_db()
        return jsonify({"status": "success", "message": message})

    # 2. Try Manual Project Update (No rewards for solo projects)
    manual = next((p for p in user.get('active_projects', []) if p['id'] == id), None)
    if manual:
        manual['progress'] = new_progress
        save_db()
        return jsonify({"status": "success", "message": "Progress Saved."})

    return jsonify({"status": "error"}), 404

@app.route('/delete_project/<id>', methods=['DELETE'])
def delete_project(id):
    user = get_current_user()
    if not user:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    # 1. Check if it's a Bounty the user has accepted
    bounty = next((b for b in bounties_db if b['id'] == id), None)
    if bounty and bounty.get('accepted_by') == user['email']:
        # Reset the bounty so it returns to the Marketplace
        bounty['status'] = 'Open'
        bounty['accepted_by'] = None
        bounty['progress'] = 0
        save_db()
        return jsonify({"status": "success", "message": "Mission released back to board."})

    # 2. Check if it's a Manual Project in the user's private list
    if 'active_projects' in user:
        initial_count = len(user['active_projects'])
        user['active_projects'] = [p for p in user['active_projects'] if p['id'] != id]
        
        if len(user['active_projects']) < initial_count:
            save_db()
            return jsonify({"status": "success", "message": "Project deleted permanently."})

    return jsonify({"status": "error", "message": "Project not found or access denied."}), 404

@app.route('/api/finalize-session/<room_id>', methods=['POST'])
def finalize_session(room_id):
    # 1. Load your database (assuming a function load_db() exists)
    db = load_db() 
    rating = request.json.get('rating', 5)
    
    # 2. Find the active swap by room_id in the 'requests' list
    # We look for swaps with status 'matched' or 'active'
    target_swap = None
    for swap in db['requests']:
        if swap.get('room_id') == room_id and swap.get('status') == 'matched':
            target_swap = swap
            break
            
    if not target_swap:
        return jsonify({"status": "error", "message": "Session not found"}), 404

    # 3. Identify Teacher and Learner
    # In a typical swap: 'from' is the person who initiated, 'to' is the acceptor.
    # Logic: Whoever's 'mode' was 'teaching' gets the credits.
    teacher_email = target_swap['from'] if target_swap.get('mode') == 'teaching' else target_swap['to']
    learner_email = target_swap['to'] if target_swap.get('mode') == 'teaching' else target_swap['from']
    
    cost = float(target_swap.get('cost', 2.5)) # Default cost if not specified

    # 4. Perform the Credit Transfer
    if learner_email in db['users'] and teacher_email in db['users']:
        # Deduct from Learner
        db['users'][learner_email]['credits'] -= cost
        # Add to Teacher
        db['users'][teacher_email]['credits'] += cost
        
        # 5. Update History for both users
        history_entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "partner": db['users'][teacher_email]['name'] if session.get('email') == learner_email else db['users'][learner_email]['name'],
            "topic": target_swap.get('topic', 'Skill Swap'),
            "amount": -cost if session.get('email') == learner_email else +cost,
            "status": "Completed"
        }
        
        # Ensure 'history' key exists
        if 'history' not in db['users'][learner_email]: db['users'][learner_email]['history'] = []
        if 'history' not in db['users'][teacher_email]: db['users'][teacher_email]['history'] = []
        
        db['users'][learner_email]['history'].append(history_entry)
        db['users'][teacher_email]['history'].append(history_entry)

        # 6. Update Teacher Rating
        db['users'][teacher_email]['ratings'].append(int(rating))
        ratings_list = db['users'][teacher_email]['ratings']
        db['users'][teacher_email]['avg_rating'] = sum(ratings_list) / len(ratings_list)

    # 7. Mark swap as completed
    target_swap['status'] = 'completed'
    target_swap['completed_at'] = datetime.now().isoformat()

    # 8. Save the database (assuming a function save_db() exists)
    save_db(db)
    
    return jsonify({
        "status": "success", 
        "message": "Credits transferred and rating recorded"
    })

# --- FINAL CONSOLIDATED MISSION & BOUNTY ROUTES ---

@app.route('/bounties')
def bounties():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth_page'))

    # AI Bounties (System generated, everyone sees these)
    ai_list = [b for b in bounties_db if b.get('type') == 'ai' and b.get('status') == 'Open']

    # Human Missions (Step 3: FILTERING)
    # 1. Must be 'human' type
    # 2. Must be 'Open'
    # 3. Creator cannot be the current logged-in user
    human_list = [
        b for b in bounties_db 
        if b.get('type') == 'human' 
        and b.get('status') == 'Open' 
        and b.get('creator_email') != user.get('email')
    ]

    return render_template('bounties.html', 
                           user=user, 
                           ai_bounties=ai_list, 
                           human_bounties=human_list)


@app.route('/accept_bounty', methods=['POST'])
def accept_bounty():
    global bounties_db  # Reference the global list initialized at startup
    
    # 1. Consistent Session Check
    # We use 'email' to match your /auth and /get_current_user logic
    user_email = session.get('email')
    
    if not user_email:
        print("!!! [AUTH ERROR]: session['email'] is empty.")
        return jsonify({"status": "error", "message": "Neural Link Lost: Please Re-login"}), 401

    # 2. Get ID from Form
    bounty_id = request.form.get('bounty_id')
    print(f"--- [MISSION START]: User {user_email} claiming {bounty_id}")

    # 3. Find the bounty in the global bounties_db list
    bounty = next((b for b in bounties_db if b['id'] == bounty_id), None)

    if not bounty:
        return jsonify({"status": "error", "message": "Bounty ID not found"}), 404
    
    if bounty.get('status') != 'Open':
        return jsonify({"status": "error", "message": "Mission already claimed"}), 400

    # 4. Update Bounty State directly in the global list
    bounty['status'] = 'Active'
    bounty['accepted_by'] = user_email
    bounty['progress'] = 0
    bounty['accepted_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 5. Save the state to database.json
    if save_db():
        print(f"+++ [SUCCESS]: {bounty_id} assigned to {user_email}")
        return jsonify({
            "status": "success", 
            "message": "Mission Synchronized", 
            "redirect": "/my_projects"
        })
    else:
        return jsonify({"status": "error", "message": "Failed to commit to ledger"}), 500
    

@app.route('/finalize_mission', methods=['POST'])
def finalize_mission():
    user = get_current_user()
    if not user: return jsonify({"status": "error"}), 401

    project_id = request.form.get('project_id')
    
    # 1. BOUNTY VERIFICATION
    bounty = next((b for b in bounties_db if b['id'] == project_id), None)
    
    if bounty and bounty.get('accepted_by') == user['email']:
        if bounty.get('status') == 'Completed':
            return jsonify({"status": "error", "message": "Already finalized"}), 400

        reward = int(bounty.get('reward', 0))

        # Human Bounty Credit Transfer Logic
        if bounty.get('type') == 'human':
            creator = users_db.get(bounty.get('creator_email'))
            if creator:
                if creator.get('credits', 0) < reward:
                    return jsonify({"status": "error", "message": "Creator has insufficient credits"}), 400
                creator['credits'] -= reward
        
        # System/AI Bounties just add credits to user
        user['credits'] = user.get('credits', 0) + reward
        bounty['status'] = 'Completed'
        bounty['progress'] = 100
        
        # Log to History
        user.setdefault('history', []).insert(0, {
            "date": str(date.today()),
            "topic": f"Bounty: {bounty['title']}",
            "amount": reward,
            "status": "Completed"
        })
        
        save_db()
        return jsonify({"status": "success", "message": f"Operation Cleared. +{reward} Credits."})

    # 2. PEER-TO-PEER SWAP LOGIC
    # Handles the 5-credit transfer for regular skill swaps
    match = next((r for r in swap_requests if r.get('room_id') == project_id), None)
    if match:
        learner = users_db.get(match['from'])
        teacher = users_db.get(match['to'])
        
        if learner and teacher and learner.get('credits', 0) >= 5:
            learner['credits'] -= 5
            teacher['credits'] += 5
            match['status'] = 'completed'
            save_db()
            return jsonify({"status": "success", "message": "Peer Swap Ledger Updated"})

    return jsonify({"status": "error", "message": "Invalid Session"}), 404

if __name__ == '__main__':
    # Ensure the DB file exists before running
    if not os.path.exists(DB_FILE):
        save_db()
    app.run(host='127.0.0.1', port=5000, debug=True)