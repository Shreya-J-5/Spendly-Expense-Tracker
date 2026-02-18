import base64
import io
import json
from datetime import datetime

from flask import Blueprint, Response, render_template, request, flash, jsonify, send_file, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import or_

from models import Note, Expense, Account
from __init__ import db
from ai_models import generate_all_charts, render_pie_chart, render_bar_chart, render_line_chart, get_expense_category_totals, get_income_category_totals, render_merged_bar_chart, render_merged_line_chart

views = Blueprint('views', __name__)


@views.route('/profile')
@login_required
def profile():
    # Use a fixed dark anonymous avatar so it stays consistent across reloads.
    profile_pic_url = url_for('static', filename='anonymous-avatar.svg')
    return render_template(
        'profile.html',
        user=current_user,
        profile_pic_url=profile_pic_url
    )


@views.route('/charts')
@login_required
def charts():
    chart_data = generate_all_charts(current_user.id)
    return render_template('charts.html', user=current_user, **chart_data)


@views.route('/expense_pie_chart')
@login_required
def expense_pie_chart():
    totals = get_expense_category_totals(current_user.id)
    return send_file(io.BytesIO(render_pie_chart(totals)), mimetype='image/png')


@views.route('/expense_bar_chart')
@login_required
def expense_bar_chart():
    totals = get_expense_category_totals(current_user.id)
    return send_file(io.BytesIO(render_bar_chart(totals)), mimetype='image/png')


@views.route('/expense_line_chart')
@login_required
def expense_line_chart():
    totals = get_expense_category_totals(current_user.id)
    return send_file(io.BytesIO(render_line_chart(totals)), mimetype='image/png')


@views.route('/merged_bar_chart')
@login_required
def merged_bar_chart():
    exp_totals = get_expense_category_totals(current_user.id)
    inc_totals = get_income_category_totals(current_user.id)
    return send_file(io.BytesIO(render_merged_bar_chart(exp_totals, inc_totals)), mimetype='image/png')


@views.route('/merged_line_chart')
@login_required
def merged_line_chart():
    exp_totals = get_expense_category_totals(current_user.id)
    inc_totals = get_income_category_totals(current_user.id)
    return send_file(io.BytesIO(render_merged_line_chart(exp_totals, inc_totals)), mimetype='image/png')





@views.route('/accounts', methods=['GET', 'POST'])
@login_required
def accounts():
    if request.method == 'POST':
        name = request.form.get('name')
        number = request.form.get('number') or '—'
        acc_type = request.form.get('type') or 'General'
        balance = request.form.get('balance')
        if not name or not balance:
            flash('Please fill in name and balance!', category='error')
        else:
            try:
                balance = float(balance)
                new_account = Account(name=name, number=number, type=acc_type, balance=balance, user_id=current_user.id)
                db.session.add(new_account)
                db.session.commit()
                flash('Account added!', category='success')
                return redirect(request.url)
            except Exception as e:
                db.session.rollback()
                flash(f'Error: {str(e)}', category='error')
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('accounts.html', user=current_user, accounts=accounts)


@views.route('/accounts/update/<int:account_id>', methods=['POST'])
@login_required
def update_account(account_id):
    account = Account.query.get(account_id)
    if not account or account.user_id != current_user.id:
        flash('Account not found.', category='error')
        return redirect(url_for('views.accounts'))
    name = request.form.get('name')
    number = request.form.get('number') or '—'
    acc_type = request.form.get('type') or 'General'
    balance = request.form.get('balance')
    if not name or not balance:
        flash('Please fill in name and balance!', category='error')
        return redirect(url_for('views.accounts'))
    try:
        balance = float(balance)
        account.name = name
        account.number = number
        account.type = acc_type
        account.balance = balance
        db.session.commit()
        flash('Account updated!', category='success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', category='error')
    return redirect(url_for('views.accounts'))


@views.route('/accounts/delete/<int:account_id>', methods=['POST'])
@login_required
def delete_account(account_id):
    account = Account.query.get(account_id)
    if not account or account.user_id != current_user.id:
        flash('Account not found.', category='error')
        return redirect(url_for('views.accounts'))
    try:
        db.session.delete(account)
        db.session.commit()
        flash('Account deleted.', category='success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', category='error')
    return redirect(url_for('views.accounts'))


@views.route('/accounts/<int:account_id>/history', methods=['GET'])
@login_required
def account_history(account_id):
    account = Account.query.get(account_id)
    if not account or account.user_id != current_user.id:
        flash('Account not found.', category='error')
        return redirect(url_for('views.accounts'))

    # Primary match uses account id stored in payment_mode; name fallback keeps older data visible.
    transactions = (Expense.query
                    .filter(Expense.user_id == current_user.id)
                    .filter(or_(Expense.payment_mode == str(account.id),
                                Expense.payment_mode == account.name))
                    .order_by(Expense.date.desc())
                    .all())

    total_income = sum(t.amount for t in transactions if t.type == 'Income')
    total_expense = sum(t.amount for t in transactions if t.type == 'Expense')

    return render_template(
        'account_history.html',
        user=current_user,
        account=account,
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        net_balance=total_income - total_expense,
    )


@views.route('/reports')
@login_required
def reports():
    transactions = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    total_income = sum(t.amount for t in transactions if t.type == 'Income')
    total_expense = sum(t.amount for t in transactions if t.type == 'Expense')
    return render_template(
        'reports.html',
        user=current_user,
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        total_balance=total_income - total_expense,
    )


@views.route('/', methods=['GET'])
def landing():
    return render_template("landingpage.html")


@views.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')
        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    total_income = sum(e.amount for e in expenses if e.type == 'Income')
    total_expense = sum(e.amount for e in expenses if e.type == 'Expense')
    total_balance = total_income - total_expense

    return render_template("dashboard.html",
                         user=current_user,
                         expenses=expenses,
                         accounts=accounts,
                         total_income=total_income,
                         total_expense=total_expense,
                         total_balance=total_balance)


@views.route('/api/accounts', methods=['GET'])
@login_required
def get_accounts():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': account.id,
        'name': account.name,
        'type': account.type
    } for account in accounts])


@views.route('/add-expense', methods=['POST'])
@login_required
def add_expense():
    try:
        amount = request.form.get('amount')
        category = request.form.get('category')
        expense_type = request.form.get('type')
        payment_mode = request.form.get('paymentMode')
        description = request.form.get('description')

        if not amount or not category or not expense_type:
            flash('Please fill in all required fields!', category='error')
            return jsonify({'success': False})

        try:
            amount = float(amount)
            if amount <= 0:
                flash('Amount must be greater than 0!', category='error')
                return jsonify({'success': False})
        except ValueError:
            flash('Invalid amount!', category='error')
            return jsonify({'success': False})

        new_expense = Expense(
            amount=amount,
            category=category,
            type=expense_type,
            description=description,
            payment_mode=payment_mode,
            user_id=current_user.id
        )

        db.session.add(new_expense)
        db.session.commit()
        flash('Expense added successfully!', category='success')
        return jsonify({'success': True})

    except Exception as e:
        db.session.rollback()
        flash(f'Error adding expense: {str(e)}', category='error')
        return jsonify({'success': False})


@views.route('/delete-expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get(expense_id)

    if expense:
        if expense.user_id == current_user.id:
            db.session.delete(expense)
            db.session.commit()
            flash('Expense deleted!', category='error')
            return jsonify({'success': True})
        else:
            flash('Unauthorized!', category='error')
            return jsonify({'success': False})

    flash('Expense not found!', category='error')
    return jsonify({'success': False})


@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
