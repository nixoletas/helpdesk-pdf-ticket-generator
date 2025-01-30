from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import io

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chamados.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo do Chamado
class Chamado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data = db.Column(db.String(20), nullable=False)
    problema = db.Column(db.String(255), nullable=False)
    operador = db.Column(db.String(100), nullable=False)

# Criar banco de dados
with app.app_context():
    db.create_all()

# =========== CRIAR CHAMADO ===============

@app.route('/api/chamados', methods=['POST'])
def criar_chamado():
    data = request.json
    novo_chamado = Chamado(
        nome=data['nome'],
        data=data['data'],
        problema=data['problema'],
        operador=data['operador']
    )
    db.session.add(novo_chamado)
    db.session.commit()
    
    return jsonify({
        "message": "Chamado criado com sucesso!", "ID": novo_chamado.id, 
        "Nome":novo_chamado.nome}), 201

# ============= OBTER CHAMADOS =================

@app.route('/api/chamados', methods=['GET'])
def obter_chamados():
    chamados = Chamado.query.all()
    chamados_list = [{
        "id": chamado.id, 
        "nome": chamado.nome, 
        "data": chamado.data, 
        "problema": chamado.problema, 
        "operador": chamado.operador
        }
        for chamado in chamados
    ]
    return jsonify(chamados_list)
    

# ================ PDF ================
@app.route('/api/chamados/recibo/<int:chamado_id>', methods=['GET'])
def gerar_pdf(chamado_id):
    fonte_jetbrains = "./jetbrains/JetBrainsMono-Regular.ttf"
    font_jetbrainsBold = "./jetbrains/JetBrainsMono-Bold.ttf"
    chamado = Chamado.query.get(chamado_id)

    if not chamado:
        return jsonify({"error": "Chamado não encontrado"}), 404

    # Definir fonte e A4
    pdf_buffer = io.BytesIO()
    pdfmetrics.registerFont(TTFont('JetBrainsMono', fonte_jetbrains))
    pdfmetrics.registerFont(TTFont('JetBrainsMono-Bold', font_jetbrainsBold))
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    
    # Definir borda
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.rect(50, 580, 500, 200)

    # ========== Etiqueta de Manutenção ================
    c.setFont("JetBrainsMono", 18)
    c.drawString(180, 800, "Etiqueta de Manutenção")

    # ================================
    c.setFont("JetBrainsMono-Bold", 12)
    c.drawString(100, 750, "P/G Nome:")
    c.setFont("JetBrainsMono", 12)
    c.drawString(200, 750, f"{chamado.nome}")

    y_position = 730

    # ================================
    c.setFont("JetBrainsMono-Bold", 12)
    c.drawString(100, y_position, "Problema:")
    c.setFont("JetBrainsMono", 12)
    c.drawString(200, y_position, f"{chamado.problema}")

    y_position -= 20

    # ==========================
    c.setFont("JetBrainsMono-Bold", 12)
    c.drawString(100, y_position, "Responsável:")
    c.setFont("JetBrainsMono", 12)
    c.drawString(200, y_position, f"{chamado.operador}")

    y_position -= 60

    # =========================
    c.setFont("JetBrainsMono", 14)
    c.drawString(200,y_position, f"Gerado em: {chamado.data}")

    # linha cinza
    c.setStrokeColor(colors.grey)
    c.setLineWidth(1)
    c.line(100, 520, 500, 520)

#========================================================

    # ========== Recibo de Manutenção ================
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.rect(50, 260, 500, 200)
 
    c.setFont("JetBrainsMono", 18)
    c.drawString(180, 480, "Recibo de Manutenção")

    c.setFont("JetBrainsMono-Bold", 12)
    c.drawString(100, 420, "P/G Nome:")
    c.setFont("JetBrainsMono", 12)
    c.drawString(200, 420, f"{chamado.nome}")
    y_position = 420

    y_position -= 20

    c.setFont("JetBrainsMono-Bold", 12)
    c.drawString(100, y_position, "Data:")
    c.setFont("JetBrainsMono", 12)
    c.drawString(200, y_position, f"{chamado.data}")

    y_position -= 20  # Reduzir para a próxima linha

    c.setFont("JetBrainsMono-Bold", 12)
    c.drawString(100, y_position, "Problema:")
    c.setFont("JetBrainsMono", 12)
    c.drawString(200, y_position, f"{chamado.problema}")

    y_position -= 60

    c.setFont("JetBrainsMono-Bold", 12)
    c.drawString(100, y_position, "Entregue para:")
    c.setFont("JetBrainsMono", 12)
    c.drawString(220, y_position, f"{chamado.operador}")

    # === Assinatura Responsável
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(200, 333, 400, 333) 

    c.save()

    pdf_buffer.seek(0)

    return Response(pdf_buffer, mimetype='application/pdf', headers={'Content-Disposition': 'inline; filename="recibo.pdf"'})

if __name__ == '__main__':
    app.run(debug=True)