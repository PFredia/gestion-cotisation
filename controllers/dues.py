from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.due import Due, DueType
from models.member import Member
from extensions import db
from datetime import datetime  # Ajout de l'importation manquante
import re

# Create dues blueprint
dues = Blueprint('dues', __name__, url_prefix='/dues')

# List all dues
# In the index function, modify how we display the dues
@dues.route('/')
@login_required
def index():
    # Get all dues
    dues_list = Due.query.all()
    
    # Create dictionaries for efficient lookups
    member_ids = [due.member_id for due in dues_list if due.member_id]
    due_type_ids = [due.due_type_id for due in dues_list if due.due_type_id]
    
    member_dict = {m.id: m for m in Member.query.filter(Member.id.in_(member_ids)).all()} if member_ids else {}
    due_type_dict = {dt.id: dt for dt in DueType.query.filter(DueType.id.in_(due_type_ids)).all()} if due_type_ids else {}
    
    # Calculate suggested amounts and remaining amounts
    for due in dues_list:
        if due.due_type_id in due_type_dict:
            due.suggested_amount = due_type_dict[due.due_type_id].amount
            due.remaining_amount = due.suggested_amount - due.amount_paid
        else:
            due.suggested_amount = due.total_amount
            due.remaining_amount = due.total_amount - due.amount_paid
    
    return render_template('dues/index.html', 
                          dues=dues_list,
                          member_dict=member_dict,
                          due_type_dict=due_type_dict)

# In the add function, add a check for already paid dues in the same year
# In the add function, we need to handle None values properly
@dues.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    members = Member.query.all()
    due_types = DueType.query.all()
    
    if request.method == 'POST':
        # Get form values
        member_id = request.form.get('member_id')
        due_type_id = request.form.get('due_type_id')
        amount = request.form.get('amount', '0')
        total_amount = request.form.get('total_amount', '0')
        payment_date = request.form.get('payment_date')
        
        # Check if member has already paid this type of due for the current year
        if member_id and due_type_id and payment_date:
            payment_year = datetime.strptime(payment_date, '%Y-%m-%d').year
            existing_due = Due.query.filter_by(
                member_id=member_id,
                due_type_id=due_type_id
            ).filter(
                db.extract('year', Due.payment_date) == payment_year
            ).first()
            
            if existing_due and existing_due.amount_paid >= existing_due.total_amount:
                flash(f'Ce membre a déjà soldé cette cotisation pour l\'année {payment_year}', 'warning')
                return render_template('dues/add.html', members=members, due_types=due_types)
        
        # Validate form data
        if not member_id or not due_type_id or not amount:
            flash('Tous les champs sont obligatoires', 'danger')
            return render_template('dues/add.html', members=members, due_types=due_types)
        
        # Get the suggested amount from the due type
        due_type = DueType.query.get(due_type_id)
        suggested_amount = due_type.amount if due_type else float(total_amount or 0)
        
        # Create new due with correct parameter names
        new_due = Due()
        new_due.member_id = int(member_id) if member_id else None
        new_due.due_type_id = int(due_type_id) if due_type_id else None
        new_due.amount_paid = float(amount or 0)
        new_due.total_amount = suggested_amount
        new_due.payment_date = payment_date
        new_due.payment_method = request.form.get('payment_method', 'cash')
        new_due.notes = request.form.get('notes', '')
        new_due.recorded_by = current_user.id
        
        db.session.add(new_due)
        db.session.commit()
        
        flash('Cotisation enregistrée avec succès', 'success')
        return redirect(url_for('dues.index'))
        
    return render_template('dues/add.html', members=members, due_types=due_types)

# Also fix the edit function to handle None values properly
@dues.route('/edit/<int:due_id>', methods=['GET', 'POST'])
@login_required
def edit(due_id):
    due = Due.query.get_or_404(due_id)
    members = Member.query.all()
    due_types = DueType.query.all()
    
    if request.method == 'POST':
        # Get form values with None checks
        member_id = request.form.get('member_id')
        due_type_id = request.form.get('due_type_id')
        amount = request.form.get('amount', '0')
        total_amount = request.form.get('total_amount', '0')
        
        # Convert values to appropriate types with None checks
        due.member_id = int(member_id) if member_id else None
        due.due_type_id = int(due_type_id) if due_type_id else None
        due.amount_paid = float(amount or 0)
        
        # Get the suggested amount from the due type if available
        if due_type_id:
            due_type = DueType.query.get(int(due_type_id))
            if due_type:
                due.total_amount = due_type.amount
            else:
                due.total_amount = float(total_amount or 0)
        else:
            due.total_amount = float(total_amount or 0)
            
        due.payment_date = request.form.get('payment_date')
        due.payment_method = request.form.get('payment_method', 'cash')
        due.notes = request.form.get('notes', '')
        
        db.session.commit()
        flash('Cotisation mise à jour avec succès', 'success')
        return redirect(url_for('dues.index'))
        
    return render_template('dues/edit.html', due=due, members=members, due_types=due_types)

# Fix the complete_payment function as well
@dues.route('/complete_payment/<int:due_id>', methods=['GET', 'POST'])
@login_required
def complete_payment(due_id):
    due = Due.query.get_or_404(due_id)
    due_type = DueType.query.get(due.due_type_id)
    member = Member.query.get(due.member_id) if due.member_id else None
    
    # Calculer le montant restant
    suggested_amount = due_type.amount if due_type else due.total_amount
    remaining_amount = suggested_amount - due.amount_paid
    
    if request.method == 'POST':
        # Récupérer le montant saisi par l'utilisateur
        payment_amount_str = request.form.get('payment_amount', '0')
        payment_amount = float(payment_amount_str or 0)
        
        # Récupérer la date de versement
        payment_date_str = request.form.get('payment_date')
        payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d') if payment_date_str else datetime.now()
        
        # Vérifier que le montant est valide
        if payment_amount <= 0 or payment_amount > remaining_amount:
            flash('Montant invalide. Veuillez entrer un montant entre 1 et ' + str(remaining_amount) + ' FCFA.', 'danger')
            return render_template('dues/complete_payment.html', 
                                  due=due, 
                                  due_type=due_type,
                                  member=member,
                                  remaining_amount=remaining_amount,
                                  today=datetime.now().strftime('%Y-%m-%d'))
        
        # Get payment method
        payment_method = request.form.get('payment_method', 'cash')
        payment_method_text = {
            'cash': 'Espèces',
            'mobile_money': 'Mobile Money',
            'bank_transfer': 'Virement bancaire',
            'check': 'Chèque'
        }.get(payment_method, payment_method)
        
        # Mettre à jour le montant payé
        due.amount_paid += payment_amount
        due.payment_date = payment_date
        due.payment_method = payment_method
        
        # Ajouter une note pour le paiement avec méthode de paiement
        payment_note = f"\n[{payment_date.strftime('%Y-%m-%d')}] Paiement de {payment_amount} FCFA effectué par {payment_method_text}."
        if due.amount_paid >= due.total_amount:
            payment_note += " Cotisation soldée."
        
        due.notes = (due.notes or '') + payment_note
        
        db.session.commit()
        
        if due.amount_paid >= due.total_amount:
            flash('Cotisation complétée avec succès!', 'success')
        else:
            flash(f'Paiement de {payment_amount} FCFA enregistré. Il reste {due.total_amount - due.amount_paid} FCFA à payer.', 'success')
            
        return redirect(url_for('dues.view', due_id=due.id))
    
    return render_template('dues/complete_payment.html', 
                          due=due, 
                          due_type=due_type,
                          member=member,
                          remaining_amount=remaining_amount,
                          today=datetime.now().strftime('%Y-%m-%d'))

# Manage due types
@dues.route('/types')
@login_required
def types():
    due_types = DueType.query.all()
    return render_template('admin/dues_types.html', due_types=due_types)

# Add a new due type
@dues.route('/types/add', methods=['POST'])
@login_required
def add_type():
    name = request.form.get('name')
    description = request.form.get('description')
    amount = request.form.get('amount')
    frequency = request.form.get('frequency')
    
    # Validate form data
    if not name:
        flash('Le nom du type de cotisation est obligatoire', 'danger')
        return redirect(url_for('dues.types'))
    
    # Create new due type using attribute assignment
    new_type = DueType()
    new_type.name = name
    new_type.description = description
    
    # Set both amount and suggested_amount to the same value if amount is provided
    if amount:
        amount_value = float(amount)
        new_type.amount = amount_value
        new_type.suggested_amount = amount_value
    else:
        # Set a default amount if none provided
        new_type.amount = 0.0
        new_type.suggested_amount = None
        
    new_type.frequency = frequency or 'monthly'  # Default to monthly if not provided
    
    db.session.add(new_type)
    db.session.commit()
    
    flash('Type de cotisation ajouté avec succès', 'success')
    return redirect(url_for('dues.types'))

# Edit a due type
@dues.route('/types/edit/<int:type_id>', methods=['GET', 'POST'])
@login_required
def edit_type(type_id):
    due_type = DueType.query.get_or_404(type_id)
    
    if request.method == 'POST':
        due_type.name = request.form.get('name')
        due_type.description = request.form.get('description')
        amount = request.form.get('amount')
        due_type.suggested_amount = float(amount) if amount else None
        due_type.frequency = request.form.get('frequency')
        
        db.session.commit()
        
        flash('Type de cotisation modifié avec succès', 'success')
        return redirect(url_for('dues.types'))
        
    return render_template('dues/edit_type.html', due_type=due_type)

# Delete a due type
@dues.route('/types/delete/<int:type_id>')
@login_required
def delete_type(type_id):
    due_type = DueType.query.get_or_404(type_id)
    
    # Check if there are dues using this type
    if Due.query.filter_by(due_type_id=type_id).first():
        flash('Impossible de supprimer ce type de cotisation car il est utilisé', 'danger')
        return redirect(url_for('dues.types'))
    
    db.session.delete(due_type)
    db.session.commit()
    
    flash('Type de cotisation supprimé avec succès', 'success')
    return redirect(url_for('dues.types'))

# Helper function to parse transaction notes
def parse_transactions(notes):
    if not notes:
        return []
    
    transactions = []
    # Pattern to match transaction entries with payment method
    pattern = r'\[([\d-]+)\]\s+Paiement de (\d+(?:\.\d+)?) FCFA effectué(?: par (\w+(?:\s+\w+)*))?\.(.*)$'
    
    # Split notes by newline and process each line
    for line in notes.split('\n'):
        if not line.strip():
            continue
            
        match = re.search(pattern, line.strip())
        if match:
            date_str = match.group(1)
            amount = match.group(2)
            payment_method = match.group(3) or "Espèces"  # Default to cash if method not specified
            additional_info = match.group(4).strip()
            
            description = f"Paiement de {amount} FCFA effectué"
            if additional_info:
                description += f" {additional_info}"
                
            transactions.append({
                'date': date_str,
                'description': description,
                'amount': amount + " FCFA",
                'payment_method': payment_method
            })
        else:
            # For lines that don't match the pattern, add them as general notes
            if line.strip():
                transactions.append({
                    'date': '',
                    'description': line.strip(),
                    'amount': '',
                    'payment_method': ''
                })
    
    # Sort transactions by date (newest first)
    transactions.sort(key=lambda x: x['date'] if x['date'] else '', reverse=True)
    
    return transactions

# View a due
@dues.route('/view/<int:due_id>')
@login_required
def view(due_id):
    due = Due.query.get_or_404(due_id)
    
    # Get the related member and due type
    member = Member.query.get(due.member_id) if due.member_id else None
    due_type = DueType.query.get(due.due_type_id) if due.due_type_id else None
    
    # Calculate remaining amount
    suggested_amount = due_type.amount if due_type else due.total_amount
    remaining = suggested_amount - due.amount_paid
    
    # Get the name of the user who recorded this due
    from models.user import User
    recorder = User.query.get(due.recorded_by) if due.recorded_by else None
    
    # Fix: Use the correct attribute names for the User model
    # The error indicates that 'first_name' doesn't exist, so we need to check the actual attribute names
    if recorder:
        # Check which attributes are available on the User model
        if hasattr(recorder, 'name'):
            recorder_name = recorder.name
        elif hasattr(recorder, 'username'):
            recorder_name = recorder.username
        else:
            # Fallback to using the ID if no name attributes are found
            recorder_name = f"ID: {recorder.id}"
    else:
        recorder_name = "Utilisateur inconnu"
    
    return render_template('dues/view.html', 
                          due=due, 
                          member=member, 
                          due_type=due_type,
                          remaining=remaining,
                          recorder_name=recorder_name,
                          parse_transactions=parse_transactions)

# Delete a due
@dues.route('/delete/<int:due_id>')
@login_required
def delete(due_id):
    due = Due.query.get_or_404(due_id)
    
    db.session.delete(due)
    db.session.commit()
    
    flash('Cotisation supprimée avec succès', 'success')
    return redirect(url_for('dues.index'))