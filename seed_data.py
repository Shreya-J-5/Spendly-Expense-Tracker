
from __init__ import create_app, db
from models import User, Expense
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Check if test user exists
    user = User.query.filter_by(email='test@test.com').first()
    if not user:
        user = User(
            email='test@test.com',
            first_name='TestUser',
            password=generate_password_hash('password'),
            gender='Male',
            number='1234567890'
        )
        db.session.add(user)
        db.session.commit()
        print("Created test user (test@test.com / password)")
    
    # Generate expenses for the last 60 days to show a trend
    categories = ['Food', 'Transport', 'Utilities', 'Entertainment', 'Shopping']
    payment_modes = ['Cash', 'Credit Card', 'UPI']
    
    expenses = []
    base_date = datetime.now()
    
    # Message
    print("Seeding expenses...")
    
    for i in range(60):
        # Create a slight upward trend in spending for 'Food' to demo the AI
        date_offset = base_date - timedelta(days=(60-i))
        
        # Daily random expense
        amount = random.uniform(10, 50) + (i * 0.5) # Slight trend upwards
        category = random.choice(categories)
        if category == 'Food':
            amount += 20 # Food is more expensive
            
        # Add an anomaly
        if i == 50:
            amount = 500 # Anomaly!
            category = 'Shopping'
            description = 'AI Anomaly Detection Test (Big Purchase)'
        else:
            description = f'Seeded expense {i}'

        expense = Expense(
            amount=round(amount, 2),
            category=category,
            type='Expense',
            description=description,
            payment_mode=random.choice(payment_modes),
            date=date_offset,
            user_id=user.id
        )
        expenses.append(expense)

    db.session.add_all(expenses)
    db.session.commit()
    print(f"Added {len(expenses)} expenses.")
