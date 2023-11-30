from login import LoginManager


def main():
    login_manager = LoginManager()
    login_manager.login()
    # Add further steps here after logging in, such as searching for trains, booking, etc.
    login_manager.close_browser()


if __name__ == "__main__":
    main()
