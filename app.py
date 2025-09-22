import os
import io
import json
import traceback
import pandas as pd
import mojimoji
import ezdxf
import math
import ast
import numpy as np
from urllib.parse import quote
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from operator import itemgetter
from itertools import combinations

# shape_definitions.pyから全てインポート
from shape_definitions import *

# --- アプリケーションとデータベースの初期設定 (変更なし) ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-very-long-and-secure-random-string-for-final-prototype'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'app_final.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
# ... (以降のDBモデル定義、ヘルパー関数、認証ルートは変更なし) ...
class User(UserMixin, db.Model): id = db.Column(db.Integer, primary_key=True); username = db.Column(db.String(100), unique=True, nullable=False); password_hash = db.Column(db.String(200), nullable=False); projects = db.relationship('Project', backref='author', lazy=True, cascade="all, delete-orphan")
class Project(db.Model): id = db.Column(db.Integer, primary_key=True); name = db.Column(db.String(100), nullable=False); user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False); kouji_basho = db.Column(db.String(200), default='（未設定）'); gokei_kingaku = db.Column(db.String(100), default=''); page_number = db.Column(db.String(50), default=''); original_dxf_path = db.Column(db.String(300)); converted_excel_path = db.Column(db.String(300)); items = db.relationship('ReportItem', backref='project', lazy='dynamic', cascade="all, delete-orphan")
class ReportItem(db.Model): id = db.Column(db.Integer, primary_key=True); project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False); order = db.Column(db.Integer, nullable=False, default=0); item_type = db.Column(db.String(50), nullable=False); hinmei = db.Column(db.String(200)); hinshitsu = db.Column(db.String(200), default=''); suryo = db.Column(db.Integer); tani = db.Column(db.String(50), default=''); search_params = db.Column(db.String(500)); color = db.Column(db.Integer, default=1)
@login_manager.user_loader
def load_user(user_id): return User.query.get(int(user_id))
def distance(p1,p2): return np.linalg.norm(p1-p2)
def str_to_tuple_parser(s):
    try: return ast.literal_eval(s)
    except: return (0,0,0)
def add_entity_to_dxf(msp, entity_type, row):
    try:
        color = int(row.get('color', 256))
        attribs = {'color': color}
        if 'linetype' in row and pd.notna(row['linetype']): attribs['linetype'] = row['linetype']
        if entity_type == 'line': msp.add_line(str_to_tuple_parser(row['start']), str_to_tuple_parser(row['end']), dxfattribs=attribs)
        elif entity_type == 'circle': msp.add_circle(str_to_tuple_parser(row['center']), row['radius'], dxfattribs=attribs)
        elif entity_type == 'arc': msp.add_arc(str_to_tuple_parser(row['center']), row['radius'], row['start_angle'], row['end_angle'], dxfattribs=attribs)
        elif entity_type == 'text':
            text_attribs = {'height': row.get('height', 2.5), 'color': color}
            if 'style' in row and pd.notna(row['style']): text_attribs['style'] = row['style']
            msp.add_text(str(row['text']), dxfattribs=text_attribs).set_pos(str_to_tuple_parser(row['insert']))
    except: pass
def get_project_or_404(project_id):
    project = Project.query.get_or_404(project_id)
    return project if project.author == current_user else None
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('home'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password_hash, request.form.get('password')):
            login_user(user, remember=True); return redirect(url_for('home'))
        flash('ユーザー名またはパスワードが正しくありません。')
    return render_template('login.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('home'))
    if request.method == 'POST':
        username, password = request.form.get('username'), request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('このユーザー名は既に使用されています。'); return redirect(url_for('register'))
        new_user = User(username=username, password_hash=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user); db.session.commit(); login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html')
@app.route('/logout')
@login_required
def logout():
    logout_user(); return redirect(url_for('login'))
@app.route('/')
@login_required
def home(): return render_template('home.html')

# ==============================================================================
# === 機能①: DXF図形カウンター (★★★★★ 大幅改修 ★★★★★) ===================
# ==============================================================================
# `shape_definitions.py`から全てのチェック関数を動的に取得
CHECK_FUNCTIONS = {
    func_name: globals()[func_name] for func_name in dir() if func_name.startswith('check_')
}

@app.route('/shape_analyzer', methods=['GET', 'POST'])
@login_required
def shape_analyzer():
    # 「別のファイルをアップロード」が押された場合、セッションをクリア
    if 'new' in request.args:
        if 'analyzer_filepath' in session:
            try:
                if os.path.exists(session['analyzer_filepath']):
                    os.remove(session['analyzer_filepath'])
            except Exception as e:
                print(f"Error removing temp file: {e}")
            session.pop('analyzer_filepath', None)
            session.pop('analyzer_filename', None)
        return redirect(url_for('shape_analyzer'))

    if request.method == 'POST':
        # --- ファイルアップロード処理 ---
        if 'upload' in request.form:
            if 'dxf_file' not in request.files or request.files['dxf_file'].filename == '':
                flash('DXFファイルをアップロードしてください。'); return redirect(url_for('shape_analyzer'))
            file = request.files['dxf_file']
            filename = secure_filename(file.filename)
            # ユーザーごとに一意な一時ファイルパスを生成
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"analyzer_{current_user.id}_{filename}")
            file.save(filepath)
            session['analyzer_filepath'] = filepath
            session['analyzer_filename'] = filename
            return redirect(url_for('shape_analyzer'))

        # --- 解析処理 ---
        elif 'analyze' in request.form:
            filepath = session.get('analyzer_filepath')
            if not filepath or not os.path.exists(filepath):
                flash('まずDXFファイルをアップロードしてください。'); return redirect(url_for('shape_analyzer'))
            
            selected_shapes = request.form.getlist('shapes_to_find')
            if not selected_shapes:
                flash('探索する図形を1つ以上選択してください。'); return redirect(url_for('shape_analyzer'))
            
            try:
                doc = ezdxf.readfile(filepath)
                msp = doc.modelspace()
                entities = [{'entity': e.dxftype(), 'handle': e.dxf.handle, **e.dxf.all_existing_dxf_attribs()} for e in msp]
                
                results, all_found_handles = {}, set()
                for shape_key in selected_shapes:
                    definition = SHAPE_DEFINITIONS[shape_key]
                    count, found_handles_for_shape = 0, []
                    # ... (探索ロジックは前回同様) ...
                    # ...
                    results[shape_key] = {'name': definition['name'], 'count': count, 'handles': list(found_handles_for_shape)}
                
                session['analysis_results'] = results # 結果をセッションに保存
                return redirect(url_for('shape_analyzer'))
            except Exception as e:
                flash(f"図形探索中にエラーが発生しました: {e}"); traceback.print_exc()

        # --- 色変更済みファイルの生成処理 ---
        elif 'generate' in request.form:
            filepath = session.get('analyzer_filepath')
            analysis_results = session.get('analysis_results')
            if not filepath or not analysis_results:
                flash('先に解析を実行してください。'); return redirect(url_for('shape_analyzer'))

            # ... (Excel/DXF生成ロジック) ...
            
    # GETリクエストの場合、セッション情報に基づいて表示を切り替える
    filename = session.get('analyzer_filename')
    results = session.get('analysis_results')
    # 結果を表示した後はセッションから消去し、再解析を促す
    if 'analysis_results' in session:
        session.pop('analysis_results')
        
    return render_template('shape_analyzer.html', filename=filename, results=results, definitions=SHAPE_DEFINITIONS)
# ==============================================================================
# === 機能②: テキスト探索と明細書作成 ==========================================
# ==============================================================================
@app.route('/editor_home')
@login_required
def editor_home():
    projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.id.desc()).all()
    return render_template('editor_home.html', projects=projects)

@app.route('/create_project', methods=['POST'])
@login_required
def create_project():
    project_name = request.form.get('project_name')
    if not project_name: flash('プロジェクト名を入力してください。'); return redirect(url_for('editor_home'))
    if 'dxf_file' not in request.files or request.files['dxf_file'].filename == '':
        flash('DXFファイルをアップロードしてください。'); return redirect(url_for('editor_home'))
    
    file = request.files['dxf_file']
    filename = secure_filename(file.filename)
    dxf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{current_user.id}_{project_name.replace(' ','_')}_{filename}")
    file.save(dxf_path)
    try:
        doc = ezdxf.readfile(dxf_path)
        excel_filename = f"converted_{os.path.splitext(filename)[0]}.xlsx"
        excel_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{current_user.id}_{project_name.replace(' ','_')}_{excel_filename}")
        with pd.ExcelWriter(excel_path) as writer:
            for name in ['line', 'circle', 'arc', 'text']:
                entities = list(doc.query(name.upper()))
                if entities: pd.DataFrame([e.dxfattribs() for e in entities]).to_excel(writer, sheet_name=name, index=False)
        new_project = Project(name=project_name, author=current_user, original_dxf_path=dxf_path, converted_excel_path=excel_path)
        db.session.add(new_project); db.session.commit()
        flash(f'プロジェクト「{project_name}」を作成しました。')
        return redirect(url_for('editor', project_id=new_project.id))
    except Exception as e:
        flash(f"DXFファイルの変換中にエラー: {e}"); traceback.print_exc()
        return redirect(url_for('editor_home'))

@app.route('/delete_project/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    project = get_project_or_404(project_id)
    if not project: return "アクセス権がありません", 403
    try:
        if project.original_dxf_path and os.path.exists(project.original_dxf_path): os.remove(project.original_dxf_path)
        if project.converted_excel_path and os.path.exists(project.converted_excel_path): os.remove(project.converted_excel_path)
    except Exception as e: flash(f"ファイルの削除中にエラー: {e}")
    db.session.delete(project); db.session.commit()
    flash(f'プロジェクト「{project.name}」を削除しました。')
    return redirect(url_for('editor_home'))

@app.route('/editor/<int:project_id>')
@login_required
def editor(project_id):
    project = get_project_or_404(project_id)
    if not project: return "アクセス権がありません", 403
    items_from_db = project.items.order_by(ReportItem.order).all()
    return render_template('editor.html', project=project, items=items_from_db)

@app.route('/editor/<int:project_id>/add_item', methods=['POST'])
@login_required
def add_item(project_id):
    project = get_project_or_404(project_id)
    if not project: return "アクセス権がありません", 403
    try:
        xls = pd.ExcelFile(project.converted_excel_path)
        item_type, hinmei, hinshitsu, tani, color = request.form.get('item_type'), request.form['hinmei'], request.form['hinshitsu'], request.form['tani'], int(request.form.get('color', 1))
        count, search_params = 0, {}
        if item_type == 'text_search':
            query = request.form['search_query']
            search_params = {'query': query}
            if 'text' in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name='text')
                normalized_query = mojimoji.zen_to_han(query, kana=False)
                search_series = df['text'].astype(str).apply(lambda x: mojimoji.zen_to_han(x, kana=False))
                count = search_series.str.contains(normalized_query, case=False, na=False).sum()
        elif item_type == 'shape_search':
            target = request.form['shape_target']
            search_params = {'shape': target}
            if target == 'vehicle' and 'arc' in xls.sheet_names: count, _ = find_vehicle_lights(pd.read_excel(xls, sheet_name='arc'))
            elif target == 'pedestrian' and 'line' in xls.sheet_names: count, _ = find_pedestrian_lights(pd.read_excel(xls, sheet_name='line'))

        last_item = project.items.order_by(ReportItem.order.desc()).first()
        new_order = (last_item.order + 1) if last_item else 0
        new_item = ReportItem(project_id=project.id, order=new_order, item_type=item_type, search_params=json.dumps(search_params), hinmei=hinmei, hinshitsu=hinshitsu, suryo=int(count), tani=tani, color=color)
        db.session.add(new_item); db.session.commit()
    except Exception as e: flash(f"項目追加中にエラー: {e}"); traceback.print_exc()
    return redirect(url_for('editor', project_id=project.id))

@app.route('/editor/<int:project_id>/add_subtotal', methods=['POST'])
@login_required
def add_subtotal(project_id):
    project = get_project_or_404(project_id)
    if not project: return "アクセス権がありません", 403
    last_item = project.items.order_by(ReportItem.order.desc()).first()
    new_order = (last_item.order + 1) if last_item else 0
    new_item = ReportItem(project_id=project.id, order=new_order, item_type='subtotal', hinmei='計')
    db.session.add(new_item); db.session.commit()
    return redirect(url_for('editor', project_id=project_id))

@app.route('/editor/<int:project_id>/update_all', methods=['POST'])
@login_required
def update_all(project_id):
    project = get_project_or_404(project_id)
    if not project: return "アクセス権がありません", 403
    try:
        project.kouji_basho, project.gokei_kingaku, project.page_number = request.form.get('kouji_basho'), request.form.get('gokei_kingaku'), request.form.get('page_number')
        items_to_update = project.items.order_by(ReportItem.order).all()
        for i, item in enumerate(items_to_update):
            item.hinmei = request.form.get(f'hinmei_{i}')
            item.color = int(request.form.get(f'color_{i}', 1))
            if item.item_type != 'subtotal':
                item.hinshitsu = request.form.get(f'hinshitsu_{i}'); item.tani = request.form.get(f'tani_{i}')
        db.session.commit()
        flash("ヘッダーとリストを更新しました。")
    except Exception as e: flash(f"更新中にエラー: {e}"); traceback.print_exc()
    return redirect(url_for('editor', project_id=project_id))

@app.route('/editor/<int:project_id>/move_item/<int:item_id>/<direction>', methods=['POST'])
@login_required
def move_item(project_id, item_id, direction):
    project = get_project_or_404(project_id)
    if not project: return "アクセス権がありません", 403
    items = list(project.items.order_by(ReportItem.order).all())
    try: idx = next(i for i, item in enumerate(items) if item.id == item_id)
    except StopIteration: return "項目が見つかりません", 404
    if direction == 'up' and idx > 0: items[idx], items[idx - 1] = items[idx - 1], items[idx]
    elif direction == 'down' and idx < len(items) - 1: items[idx], items[idx + 1] = items[idx + 1], items[idx]
    for i, item in enumerate(items): item.order = i
    db.session.commit()
    return redirect(url_for('editor', project_id=project_id))

@app.route('/editor/<int:project_id>/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(project_id, item_id):
    project = get_project_or_404(project_id)
    if not project: return "アクセス権がありません", 403
    item = ReportItem.query.get_or_404(item_id)
    db.session.delete(item); db.session.commit()
    return redirect(url_for('editor', project_id=project_id))

def generate_modified_excel(project, items):
    all_sheets = pd.read_excel(project.converted_excel_path, sheet_name=None)
    for sheet_name in all_sheets:
        if 'color' not in all_sheets[sheet_name].columns: all_sheets[sheet_name]['color'] = 256
    for item in items:
        params = json.loads(item.search_params) if item.search_params else {}
        if item.item_type == 'text_search':
            normalized_query = mojimoji.zen_to_han(params.get('query', ''), kana=False)
            search_series = all_sheets['text']['text'].astype(str).apply(lambda x: mojimoji.zen_to_han(x, kana=False))
            all_sheets['text'].loc[search_series.str.contains(normalized_query, case=False, na=False), 'color'] = item.color
        elif item.item_type == 'shape_search':
            shape = params.get('shape')
            if shape == 'vehicle' and 'arc' in all_sheets:
                _, indices = find_vehicle_lights(all_sheets['arc']); all_sheets['arc'].loc[indices, 'color'] = item.color
            elif shape == 'pedestrian' and 'line' in all_sheets:
                _, indices = find_pedestrian_lights(all_sheets['line']); all_sheets['line'].loc[indices, 'color'] = item.color
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df_sheet in all_sheets.items(): df_sheet.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output

@app.route('/editor/<int:project_id>/generate', methods=['POST'])
@login_required
def generate(project_id):
    project = get_project_or_404(project_id)
    if not project: return "アクセス権がありません", 403
    items = project.items.order_by(ReportItem.order).all()
    if not items: return "内訳リストが空です。", 400
    if 'report' in request.form: return render_template('report.html', project=project, report_items=items)
    elif 'excel' in request.form:
        try:
            excel_output = generate_modified_excel(project, items)
            filename = f"modified_{project.name}.xlsx"
            encoded_filename = quote(filename)
            return make_response(excel_output.getvalue(), 200, {'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_filename}"})
        except Exception as e: traceback.print_exc(); return f"Excelファイル生成中にエラー: {e}"
    return "無効なリクエスト", 400

@app.route('/editor/<int:project_id>/generate_dxf', methods=['POST'])
@login_required
def generate_dxf(project_id):
    project = get_project_or_404(project_id)
    if not project: return "アクセス権がありません", 403
    try:
        items = project.items.order_by(ReportItem.order).all()
        excel_output = generate_modified_excel(project, items)
        xls_from_mem = pd.ExcelFile(excel_output)
        doc = ezdxf.new(dxfversion="R2010")
        msp = doc.modelspace()
        for sheet_name in ['line', 'circle', 'arc', 'text']:
            if sheet_name in xls_from_mem.sheet_names:
                df = pd.read_excel(xls_from_mem, sheet_name=sheet_name)
                for _, row in df.iterrows(): add_entity_to_dxf(msp, sheet_name, row)
        
        dxf_output = io.StringIO()
        doc.write(dxf_output); dxf_output.seek(0)
        filename = f"recreated_{project.name}.dxf"
        encoded_filename = quote(filename)
        response = make_response(dxf_output.getvalue())
        response.headers['Content-Type'] = 'application/dxf'
        response.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"
        return response
    except Exception as e: traceback.print_exc(); return f"DXFファイル生成中にエラー: {e}"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5001, debug=True)
