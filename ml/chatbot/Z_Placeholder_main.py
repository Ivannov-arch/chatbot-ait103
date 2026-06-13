# placeholder_main.py
# chatbot/main.py
#
# Terminal entry point for the XMUM Campus Chatbot.
# Run with:  python -m chatbot.main
#
# Responsibilities:
#   - Load .env configuration
#   - Instantiate the Bot from bot.py
#   - Run an interactive REPL loop in the terminal
#   - Handle graceful exit (Ctrl+C / "exit" / "quit")
#
# TODO: implement the terminal REPL loop.
# TODO: load env with python-dotenv.
# TODO: import Bot from chatbot.bot and call bot.chat(user_input).

def main():
    """Entry point: start the terminal chatbot loop."""
    # PLACEHOLDER — replace with actual implementation
    print("[PLACEHOLDER] XMUM Campus Chatbot terminal is not yet implemented.")
    print("Type 'exit' to quit.")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        print(f"Bot: [PLACEHOLDER] You said: {user_input!r}")

if __name__ == "__main__":
    main()
