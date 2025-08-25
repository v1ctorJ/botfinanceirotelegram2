import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import csv
from datetime import datetime

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CSV_FILE = "gastos_telegram.csv"

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["data", "descricao", "valor"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Envie um gasto no formato: gasolina 100")

async def registrar_gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    partes = texto.split()
    if len(partes) < 2:
        await update.message.reply_text("Formato inválido. Use: descrição valor\nEx: pizza 40")
        return

    descricao = " ".join(partes[:-1])
    try:
        valor = float(partes[-1])
    except ValueError:
        await update.message.reply_text("O último item precisa ser um número (valor).")
        return

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d"), descricao, valor])

    await update.message.reply_text(f"Gasto registrado: {descricao} - R$ {valor:.2f}")

async def total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_gastos = 0
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_gastos += float(row["valor"])
    await update.message.reply_text(f"Total de gastos: R$ {total_gastos:.2f}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("total", total))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registrar_gasto))

    print("🤖 Bot rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()

