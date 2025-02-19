# Projeto Mini-Cassino
#### Video Demo:  <https://youtu.be/cndcIOK5eqw>
#### Description:
The **Mini Casino** is a web project developed as part of the CS50 course. It offers three classic casino games: **Blackjack**, **Roulette**, and **Slot Machine**. The project is built using **Flask** for the backend, **SQLite** for the database, and **HTML/CSS/JavaScript** for the frontend. The goal is to provide an interactive and fun experience while exploring web development concepts such as user authentication, session management, and game logic.
---
## Key Features

### 1. **User Authentication**
- **Registration**: Users can register by providing a username and password. Passwords are securely stored using hashing with Flask's `generate_password_hash` and `check_password_hash` functions. This ensures that sensitive user data is protected.
- **Login**: Users can log in to access games and manage their balance. The login process validates credentials against the database and creates a session for authenticated users.
- **Logout**: Users can log out, which clears their session and ensures the security of their accounts.

### 2. **Available Games**
- **Blackjack**:
  - Users place bets and play against the dealer. The game follows traditional Blackjack rules, with options to "Hit" (request another card) or "Stand" (end their turn).
  - The dealer automatically draws cards until their hand reaches a score of at least 17.
  - The user's balance is updated based on the game's outcome, with payouts for wins and deductions for losses.
- **Roulette**:
  - Users can bet on numbers (0-15), colors (red, black, or green), odd/even, or low/high (0-7 or 8-15).
  - The roulette wheel is animated using JavaScript, and the winning number is determined randomly.
  - Payouts are calculated based on the type of bet, with multipliers for higher-risk bets (e.g., betting on a specific number pays 15x).
- **Slot Machine**:
  - Users spin a 3x3 grid of symbols (e.g., cherries, stars, bells) and win prizes based on matching combinations in rows, columns, or diagonals.
  - Payouts are calculated using predefined multipliers for different combinations (e.g., matching a row pays 2x the bet).

### 3. **Balance Management**
- **Add Chips**: Users can add chips to their balance by entering a value and submitting the form. The balance is updated in real-time and stored in the database.
- **History**: Users can view their win/loss history and net balance. The history page displays total wins, losses, and the overall result (profit or loss).

### 4. **Responsive Design**
- The project is fully responsive, working well on both mobile and desktop devices. The use of **Bootstrap** ensures that the layout adapts to different screen sizes.
- Custom CSS styles, such as neon borders and animations, create a visually appealing casino-like atmosphere.
---
## Project Files

### 1. **`app.py`**
- The core of the project, containing all backend logic.
- Manages routes, authentication, games, and database interactions.
- Includes functions to:
  - Decide the winner on each game.
  - Handle bets and update user balances.
  - Generate random outcomes for Roulette and the Slot Machine.

### 2. **`help.py`**
- Contains reusable helper functions, such as:
  - `login_required`: A decorator to protect routes that require authentication.
  - `create_deck`: Creates and shuffles a deck of cards for Blackjack.
  - `calculate_score`: Calculates the score of a hand in Blackjack, adjusting for the value of Aces.
  - `calcular_premiacao`: Calculates payouts in the Slot Machine based on matching combinations.

### 3. **Templates (`layout.html`, `index.html`, `login.html`, `register.html`, etc.)**
- **`layout.html`**: The base template that defines the common structure for all pages. It includes the logo, navigation bar, header, and footer.
- **`index.html`**: The homepage for unauthenticated visitors, with a welcome message and links to login or register.
- **`login.html`**: The login page, featuring a form for users to enter their credentials.
- **`register.html`**: The registration page, where new users can create an account.
- **`homepage.html`**: The homepage for authenticated users, displaying their username and current balance.
- **`blackjack.html`**: The Blackjack game page, featuring the user's hand, the dealer's hand, and buttons to "Hit" or "Stand."
- **`roleta.html`**: The Roulette game page, featuring an animated wheel and a form to place bets.
- **`niquel.html`**: The Slot Machine game page, featuring a 3x3 grid of symbols and a form to place bets.
- **`add.html`**: The page to add chips, featuring a form to enter the desired amount.
- **`historico.html`**: The win/loss history page, displaying total wins, losses, and net balance.

### 4. **`style.css`**
- Defines the visual styles for the project, including colors, animations, and layout.
- Uses CSS variables to manage colors consistently across the project.
- Includes specific styles for each game and component, such as:
  - Neon borders and shadows for a casino-like aesthetic.
  - Animations for the Roulette wheel and Slot Machine symbols.
  - Responsive layouts for mobile and desktop devices.

### 5. **Database (`tigrinho.db`)**
- Stores user information, such as username, password (hash), balance, wins, and losses.
- The `users` table is used to manage authentication and user data.
- The database is accessed using the `cs50.SQL` library, which simplifies SQL queries and interactions.

---

## Design Choices

### 1. **Use of Flask and SQLite**
- I chose **Flask** for its simplicity and flexibility, making it ideal for small to medium-sized projects. Flask's lightweight nature allowed me to focus on building features without unnecessary complexity.
- **SQLite** was selected for its lightweight nature and seamless integration with Flask. It requires no additional setup, making it perfect for a project of this scale.

### 2. **Modern and Responsive Design**
- I used **Bootstrap** to ensure a responsive and consistent design across different devices. Bootstrap's grid system and prebuilt components saved time and ensured a professional look.
- Added visual effects, such as neon borders and animations, to create a casino-like atmosphere. These effects were implemented using custom CSS and JavaScript.

### 3. **Security**
- Passwords are stored using hashing with Flask's `generate_password_hash` and `check_password_hash` functions. This ensures that sensitive user data is protected.
- Sensitive routes are protected with the `login_required` decorator, which redirects unauthenticated users to the login page.

### 4. **Interactivity**
- Roulette and Blackjack include animations and visual feedback to enhance the user experience. For example, the Roulette wheel spins smoothly, and the Blackjack cards are displayed with a flipping animation.
- The use of AJAX in Roulette provides a smoother experience without page reloads. This was implemented using JavaScript's `fetch` API to send and receive data asynchronously.

---

## How to Run the Project

1. **Install dependencies**:
   ```bash
   pip install Flask
   pip install cs50
