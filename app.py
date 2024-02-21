import aiohttp
import asyncio
from flask import Flask, render_template, request, redirect, url_for
from telegram import Bot
from datetime import datetime, timedelta
from threading import Thread

app = Flask(__name__)

# Ganti TOKEN_BOT dengan token Telegram bot Anda
TOKEN_BOT = '7165588372:AAHxRHnKET5gbIFZ4dw1zYRHGqbrnIkkxbk'
chat_id = '1884067981'

bot = Bot(token=TOKEN_BOT)
tasks = []

async def send_notification(message):
    async with aiohttp.ClientSession() as session:
        async with session.post(f'https://api.telegram.org/bot{TOKEN_BOT}/sendMessage', json={'chat_id': chat_id, 'text': message}) as response:
            if response.status != 200:
                print(f"Failed to send notification: {response.status}")
            else:
                print(f"Notification sent: {message}")

async def schedule_task(account, task_name, end_time):
    now = datetime.now()
    end_datetime = datetime.combine(end_time['date'], end_time['time'])
    
    while datetime.now() < end_datetime:
        await asyncio.sleep(1)

    await send_notification(f"""
                            RDP Expired Alert!
IP Address '{task_name}' Telah Expired!
Account : {account}
                            """)

def run_schedule_task(account, task_name, end_time):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(schedule_task(account, task_name, end_time))

@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    account = request.form['account']
    task_name = request.form['task_name']
    end_date = request.form['end_date']
    end_time = request.form['end_time']
    
    end_time_obj = {
        'date': datetime.strptime(end_date, '%Y-%m-%d').date(),
        'time': datetime.strptime(end_time, '%H:%M').time()
    }

    tasks.append({'account': account, 'name': task_name, 'end_time': end_time_obj})
    
    # Running the schedule_task in a separate thread
    thread = Thread(target=run_schedule_task, args=(account, task_name, end_time_obj))
    thread.start()

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
