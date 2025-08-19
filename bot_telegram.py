from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import pandas as pd
import os
from datetime import datetime

# Nome do arquivo baseado no mês atual
def get_data_file():
    mes_atual = datetime.now().strftime("%Y_%m")
    return f"gastos_{mes_atual}.csv"

# Garantir que existe arquivo CSV do mês
def init_csv():
    data_file = get_data_file()
    if not os.path.exists(data_file):
        df = pd.DataFrame(columns=["ChatID", "Categoria", "Valor", "Data"])
        df.to_csv(data_file, index=False)
    return data_file

# Registrar gasto no CSV
def registrar_gasto(chat_id, categoria, valor):
    data_file = init_csv()
    df = pd.read_csv(data_file)

    novo_gasto = pd.DataFrame(
        [[chat_id, categoria, float(valor), datetime.now().strftime("%Y-%m-%d")]],
        columns=["ChatID", "Categoria", "Valor", "Data"]
    )

    df = pd.concat([df, novo_gasto], ignore_index=True)
    df.to_csv(data_file, index=False)

# Calcular total de gastos no mês atual
def total_gastos(chat_id):
    data_file = init_csv()
    df = pd.read_csv(data_file)
    df_usuario = df[df["ChatID"] == chat_id]

    if df_usuario.empty:
        return "Nenhum gasto encontrado para você neste mês."
    
    total = df_usuario["Valor"].sum()
    return f"💰 Seu total de gastos em {datetime.now().strftime('%m/%Y')} é: R$ {total:.2f}"

# Relatório por categoria do mês atual
def relatorio_gastos(chat_id):
    data_file = init_csv()
    df = pd.read_csv(data_file)
    df_usuario = df[df["ChatID"] == chat_id]

    if df_usuario.empty:
        return "Nenhum gasto encontrado para gerar relatório deste mês."

    resumo = df_usuario.groupby("Categoria")["Valor"].sum().reset_index()
    total = df_usuario["Valor"].sum()

    texto = f"📊 Relatório de Gastos - {datetime.now().strftime('%m/%Y')}\n\n"
    for _, row in resumo.iterrows():
        texto += f"- {row['Categoria']}: R$ {row['Valor']:.2f}\n"
    texto += f"\n💰 Total geral: R$ {total:.2f}"

    return texto

# Comandos do bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! 👋 Eu sou seu bot de controle de gastos.\n\n"
        "📌 Comandos disponíveis:\n"
        "👉 /gasto <categoria> <valor> → Registrar um gasto\n"
        "👉 /total → Ver total acumulado do mês\n"
        "👉 /relatorio → Ver resumo por categoria do mês atual"
    )

async def gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        categoria = context.args[0]
        valor = context.args[1]
        registrar_gasto(update.effective_chat.id, categoria, valor)
        await update.message.reply_text(f"✅ Gasto de R$ {valor} em {categoria} registrado com sucesso!")
    except (IndexError, ValueError):
        await update.message.reply_text("⚠️ Uso incorreto!\nExemplo: /gasto mercado 250")

async def total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resposta = total_gastos(update.effective_chat.id)
    await update.message.reply_text(resposta)

async def relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resposta = relatorio_gastos(update.effective_chat.id)
    await update.message.reply_text(resposta)

def main():
    # 🔴 Substitua pelo TOKEN do BotFather
    TOKEN = "8377569836:AAEdm-61MdfPF1McSczrzdiAMoBiOjgzAeE"

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gasto", gasto))
    app.add_handler(CommandHandler("total", total))
    app.add_handler(CommandHandler("relatorio", relatorio))

    print("🤖 Bot rodando... Pressione CTRL+C para parar.")
    app.run_polling()

if __name__ == "__main__":
    main()
