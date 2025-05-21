**SupportApp** is a prototype of a web application for group management of Telegram support-service bots.  
The project allows you to:
- organize bots into logical groups
- manage their list of chats via a single web interface
- later receive real-time notifications about new messages over WebSocket
### Project Structure
1. **Backend**
    - Python  + Django
    - Django REST Framework (API)
    - PostgreSQL (+ psycopg2)
2. **Frontend**
    - TypeScript + React
    - MobX (state management)
    - Nginx (static build)
3. **Telegram-bot**
    - Python + Aiogram
    - Data exchange with the server over WebSocket
### Quick Start
1. Install Docker and Docker Compose.
2. Open the file `.env` and set:
    ```dotenv
    BOT_TOKEN=<your BotFather token>
    ```
3. In your terminal, from the folder containing `docker-compose.yml`, run:
    ```bash
    docker-compose up -d
    ```
4. Open [http://localhost](http://localhost/) in your browser and log in with:
    ```
    username: admin  
    password: superuser
    ```
5. Start a chat with the bot in Telegram and send any message—it will create a new support request.
6. Refresh the page in your browser: your conversation will appear in the chat list.
### Technologies Used

| Component    | Technologies                    |
| ------------ | ------------------------------- |
| Backend      | Python, Django, DRF, PostgreSQL |
| Telegram Bot | Python, Aiogram, WebSocket      |
| Frontend     | TypeScript, React, MobX, Nginx  |
### Features
- **Real-Time WebSocket Connection**
  WebSocket technology enables near-instantaneous message transmission from the bot to the backend server and then to the frontend client. This ensures smooth and fast communication without the need to manually refresh the page or send constant requests to the server.
- **Secure Message Exchange**
  Communication between the Telegram bot and the backend server is secured using a token generated from the user’s `telegram_id` and a unique key assigned to the bot. The data exchange between the frontend client and the server is protected via JWT authentication, ensuring request authenticity and preventing unauthorized access.
- **[ProjectLogger](https://github.com/joshvoron/projectlogger)**
  A custom logging system designed to conveniently segment logs from various Python application components. It supports color tagging and source naming, making debugging and monitoring easier and more efficient.

### Project Status
This is an early prototype: the core functionality for grouping bots and viewing conversations is ready. Planned features include:
- The ability to create custom groups
- Adding and removing bots within groups
- Real-time notifications for new messages (WebSocket)
- Search functionality for chats and messages
- UI for editing groups and bots
- A more flexible access control system
*These plans are tentative and may change during development.*

If you have any questions or suggestions, please write to **[ilyavoronovwork@gmail.com](mailto:ilyavoronovwork@gmail.com)** or message **[@nusquamcurrere](https://t.me/nusquamcurrere)**. Thank you!
