import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def generate_test_invoice():
    """
    Gera um arquivo PDF de fatura de cartão de crédito para testes.
    """
    # Cria o diretório para testes se não existir
    os.makedirs("app/static/test_data", exist_ok=True)
    
    output_file = "app/static/test_data/fatura_teste.pdf"
    
    # Cria um buffer para o PDF
    buffer = io.BytesIO()
    
    # Cria o PDF
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Adiciona cabeçalho
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "BANCO XYZ")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 70, "FATURA DO CARTÃO DE CRÉDITO")
    
    # Adiciona informações do cliente
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 100, "Nome:")
    c.setFont("Helvetica", 10)
    c.drawString(100, height - 100, "JOÃO DA SILVA")
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 120, "Cartão:")
    c.setFont("Helvetica", 10)
    c.drawString(100, height - 120, "•••• •••• •••• 1234")
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 140, "Fechamento:")
    c.setFont("Helvetica", 10)
    c.drawString(120, height - 140, "15/06/2025")
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 160, "Vencimento:")
    c.setFont("Helvetica", 10)
    c.drawString(120, height - 160, "22/06/2025")
    
    # Adiciona linha separadora
    c.line(50, height - 180, width - 50, height - 180)
    
    # Adiciona cabeçalho da tabela de transações
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 200, "Data")
    c.drawString(100, height - 200, "Descrição")
    c.drawString(400, height - 200, "Valor (R$)")
    
    # Adiciona linha separadora
    c.line(50, height - 210, width - 50, height - 210)
    
    # Adiciona transações
    transactions = [
        ("01/06", "SUPERMERCADO XYZ", "150,00"),
        ("05/06", "RESTAURANTE ABC", "85,50"),
        ("07/06", "POSTO DE GASOLINA", "200,00"),
        ("10/06", "FARMACIA 123", "45,75"),
        ("12/06", "UBER", "30,00"),
        ("14/06", "NETFLIX", "39,90"),
        ("15/06", "LIVRARIA", "120,00")
    ]
    
    y_position = height - 230
    for date, desc, value in transactions:
        c.setFont("Helvetica", 10)
        c.drawString(50, y_position, date)
        c.drawString(100, y_position, desc)
        c.drawString(400, y_position, value)
        y_position -= 20
    
    # Adiciona linha separadora
    c.line(50, y_position - 10, width - 50, y_position - 10)
    
    # Adiciona total
    c.setFont("Helvetica-Bold", 12)
    c.drawString(300, y_position - 30, "Total:")
    c.drawString(400, y_position - 30, "R$ 671,15")
    
    # Finaliza o PDF
    c.showPage()
    c.save()
    
    # Salva o buffer em um arquivo
    with open(output_file, "wb") as f:
        f.write(buffer.getvalue())
    
    print(f"Arquivo de teste gerado: {output_file}")
    return output_file

if __name__ == "__main__":
    generate_test_invoice()
