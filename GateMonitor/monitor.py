import os
import yaml
import urllib.request
import urllib.error
from pathlib import Path
from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify, g
from data.models import SessionLocal, User, Parameter
from functools import wraps

Monitor = Blueprint('Monitor', __name__)

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config" / "gateway.yml"

def get_db():
    if 'db' not in g:
        g.db = SessionLocal()
    return g.db

@Monitor.teardown_request
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'danger')
            return redirect(url_for('Monitor.login'))
        return f(*args, **kwargs)
    return decorated_function

def load_gateway_config():
    if not CONFIG_FILE.exists():
        return {"gateway": {"host": "0.0.0.0", "port": 8000}, "routes": []}
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}
    except Exception:
        return {"gateway": {"host": "0.0.0.0", "port": 8000}, "routes": []}

@Monitor.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('Monitor.monitoring'))
    return redirect(url_for('Monitor.login'))

@Monitor.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('Monitor.monitoring'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = get_db()
        user = db.query(User).filter(User.username == username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('Monitor.monitoring'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
            
    return render_template('login.html')

@Monitor.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('Monitor.login'))

@Monitor.route('/monitoring')
@login_required
def monitoring():
    config = load_gateway_config()
    gateway = config.get("gateway", {})
    routes = config.get("routes", [])
    return render_template('monitoring.html', gateway=gateway, routes=routes)

@Monitor.route('/monitoring/status')
@login_required
def monitoring_status():
    config = load_gateway_config()
    routes = config.get("routes", [])
    
    status_results = []
    for route in routes:
        name = route.get("name")
        target = route.get("target")
        path = route.get("path")
        
        status, detail = "Offline", "Unreachable"
        try:
            req = urllib.request.Request(target, method='GET')
            # set a short timeout of 1 second for local checks
            with urllib.request.urlopen(req, timeout=1.0) as response:
                status = "Online"
                detail = f"HTTP {response.status}"
        except urllib.error.HTTPError as e:
            status = "Online"
            detail = f"HTTP {e.code}"
        except urllib.error.URLError as e:
            status = "Offline"
            detail = str(e.reason)
        except Exception as e:
            status = "Offline"
            detail = str(e)
            
        status_results.append({
            "name": name,
            "target": target,
            "path": path,
            "status": status,
            "detail": detail
        })
        
    return jsonify({"services": status_results})

@Monitor.route('/parameters')
@login_required
def parameters():
    db = get_db()
    params = db.query(Parameter).all()
    # Separate parameters by category
    system_params = [p for p in params if p.category == 'system']
    project_params = [p for p in params if p.category == 'project']
    return render_template('parameters.html', system_params=system_params, project_params=project_params)

@Monitor.route('/parameters/add', methods=['POST'])
@login_required
def parameters_add():
    key = request.form.get('key')
    value = request.form.get('value')
    category = request.form.get('category', 'system')
    description = request.form.get('description', '')
    
    if not key or not value:
        flash('Chave e valor são obrigatórios.', 'danger')
        return redirect(url_for('Monitor.parameters'))
        
    db = get_db()
    # Check if key already exists
    existing = db.query(Parameter).filter(Parameter.key == key).first()
    if existing:
        flash(f'Parâmetro com a chave "{key}" já existe.', 'danger')
        return redirect(url_for('Monitor.parameters'))
        
    try:
        param = Parameter(key=key, value=value, category=category, description=description)
        db.add(param)
        db.commit()
        flash('Parâmetro adicionado com sucesso!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Erro ao adicionar parâmetro: {e}', 'danger')
        
    return redirect(url_for('Monitor.parameters'))

@Monitor.route('/parameters/update/<int:param_id>', methods=['POST'])
@login_required
def parameters_update(param_id):
    value = request.form.get('value')
    description = request.form.get('description', '')
    
    db = get_db()
    param = db.query(Parameter).filter(Parameter.id == param_id).first()
    
    if not param:
        flash('Parâmetro não encontrado.', 'danger')
        return redirect(url_for('Monitor.parameters'))
        
    try:
        param.value = value
        param.description = description
        db.commit()
        flash('Parâmetro atualizado com sucesso!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Erro ao atualizar parâmetro: {e}', 'danger')
        
    return redirect(url_for('Monitor.parameters'))

@Monitor.route('/parameters/delete/<int:param_id>', methods=['POST'])
@login_required
def parameters_delete(param_id):
    db = get_db()
    param = db.query(Parameter).filter(Parameter.id == param_id).first()
    
    if not param:
        flash('Parâmetro não encontrado.', 'danger')
        return redirect(url_for('Monitor.parameters'))
        
    try:
        db.delete(param)
        db.commit()
        flash('Parâmetro removido com sucesso!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Erro ao remover parâmetro: {e}', 'danger')
        
    return redirect(url_for('Monitor.parameters'))

@Monitor.route('/parameters/change_password', methods=['POST'])
@login_required
def parameters_change_password():
    new_username = request.form.get('username')
    new_password = request.form.get('password')
    
    if not new_username:
        flash('Usuário não pode ser vazio.', 'danger')
        return redirect(url_for('Monitor.parameters'))
        
    db = get_db()
    user = db.query(User).filter(User.id == session['user_id']).first()
    
    if not user:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('Monitor.parameters'))
        
    try:
        # Check if username is changing and if new username is already taken
        if new_username != user.username:
            existing = db.query(User).filter(User.username == new_username).first()
            if existing:
                flash('Este nome de usuário já está em uso.', 'danger')
                return redirect(url_for('Monitor.parameters'))
            user.username = new_username
            session['username'] = new_username
            
        if new_password:  # Only change password if provided
            user.set_password(new_password)
            
        db.commit()
        flash('Dados de acesso atualizados com sucesso!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Erro ao atualizar dados: {e}', 'danger')
        
    return redirect(url_for('Monitor.parameters'))

@Monitor.route('/docs', methods=['GET'])
def docs():
    return render_template('docs.html')

@Monitor.route('/docs/<page>', methods=['GET'])
def docs_page(page):
    return render_template("/docs/"+page+'.html')