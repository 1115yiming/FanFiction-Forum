import pymysql
import sys

def get_database_connection(username, password):
    try:
        connection = pymysql.connect(
            host='localhost',
            user=username,
            password=password,
            db='Fanfiction_Forum',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def check_account():
    has_account = input("Do you already have an account with our forum? (yes/no): ").lower()
    return has_account == 'yes'


def register_user(connection):
    email = input("Enter your email: ")
    user_name = input("Enter your username: ")
    password = input("Enter your password: ")
    try:
        with connection.cursor() as cursor:
            cursor.callproc('create_new_user', (email, user_name, password))
            connection.commit()
            print("Registration successful!")
            return email  # Returning the email of the registered user
    except Exception as e:
        print(f"Error registering user: {e}")
        return None

def delete_book(connection, author_email):
    try:
        with connection.cursor() as cursor:
            # Retrieve the user_name associated with the author_email
            cursor.execute("SELECT user_name FROM user WHERE email = %s", (author_email,))
            result = cursor.fetchone()
            if result:
                user_name = result['user_name']
            else:
                print("User not found.")
                return

            # Retrieve and display the books written by the author
            cursor.callproc('get_books_by_author', [user_name])
            books = cursor.fetchall()
            if not books:
                print("You have not written any books.")
                return

            print("Books you've written:")
            for book in books:
                print(f"Book ID: {book['book_id']}, Book Name: {book['book_name']}")

            # Prompt the user to select a book to delete
            book_id = input("Enter the ID of the book you want to delete: ")

            # Call the stored procedure to delete the book
            cursor.callproc('delete_book', [book_id])
            connection.commit()
            print("Book deleted successfully.")

    except Exception as e:
        print(f"Error deleting book: {e}")


def actions_to_book(connection, user_email, book_id):
    while True:
        print("\nChoose an action for the selected book:")
        print("1) Comment on the book")
        print("2) Update your comment")
        print("3) Delete your comment")
        print("4) Like the book")
        print("5) Unlike the book")
        print("6) Go back")
        action = input("Enter the number of your choice: ")

        try:
            with connection.cursor() as cursor:
                if action == '1':
                    comment_text = input("Enter your comment: ")
                    cursor.callproc('add_book_comment', [book_id, comment_text, user_email])
                    connection.commit()
                    print("Comment added successfully.")

                elif action in ['2', '3']:
                    cursor.callproc('get_user_comments_on_book', [user_email, book_id])
                    comments = cursor.fetchall()
                    if not comments:
                        print("No comments found.")
                        continue
                    for comment in comments:
                        print(f"Timestamp: {comment['comment_time']}, Comment: {comment['comment_text']}")

                    comment_time = input("Enter the timestamp of the comment you want to update/delete (YYYY-MM-DD HH:MM:SS): ")
                    if action == '2':
                        new_comment_text = input("Enter your new comment: ")
                        cursor.callproc('update_comment', [comment_time, user_email, book_id, new_comment_text])
                        connection.commit()
                        print("Comment updated successfully.")
                    else:
                        cursor.callproc('delete_comment', [comment_time, user_email, book_id])
                        connection.commit()
                        print("Comment deleted successfully.")

                elif action == '4':
                    # Check if the user already likes the book
                    cursor.execute("SELECT COUNT(*) AS count FROM user_favorites_book WHERE email = %s AND book_id = %s", (user_email, book_id))
                    result = cursor.fetchone()
                    if result['count'] > 0:
                        print("You have already liked this book.")
                    else:
                        cursor.callproc('like_book', [user_email, book_id])
                        connection.commit()
                        print("Book liked successfully.")

                elif action == '5':
                    # Check if the user has not liked the book yet
                    cursor.execute("SELECT COUNT(*) AS count FROM user_favorites_book WHERE email = %s AND book_id = %s", (user_email, book_id))
                    result = cursor.fetchone()
                    if result['count'] == 0:
                        print("You haven't liked this book yet.")
                    else:
                        cursor.callproc('unlike_book', [user_email, book_id])
                        connection.commit()
                        print("Book unliked successfully.")

                elif action == '6':
                    break
                else:
                    print("Invalid option, please try again.")

        except Exception as e:
            print(f"An error occurred: {e}")


def login_user(connection):
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    try:
        with connection.cursor() as cursor:
            cursor.callproc('check_password', (email, password))
            result = cursor.fetchone()
            if result['is_correct']:
                print("Login successful!")
                return email  # Returning the email of the logged-in user
            else:
                print("Incorrect email or password.")
                return None
    except Exception as e:
        print(f"Error logging in: {e}")
        return None


def main_page_options():
    print("Choose an option:")
    print("1) Search a book")
    print("2) Get my favorite book list")
    print("3) Publish a book")
    print("4) Update a book")
    print("5) Delete a book")
    option = input("Enter the number of your choice: ")
    return option

def recover_password(connection):
    email = input("Enter your email for password recovery: ")
    try:
        with connection.cursor() as cursor:
            cursor.callproc('get_user_password', [email])
            result = cursor.fetchone()
            if result and 'password' in result:
                print(f"Your password is: {result['password']}")
            else:
                print("No account found with that email.")
                return False
    except Exception as e:
        print(f"Error during password recovery: {e}")
        return False
    return True

def search_book(connection):
    print("Choose an option for searching a book:")
    print("1) Through title")
    print("2) Through keyword")
    print("3) Through book genre")
    search_option = input("Enter the number of your choice: ")

    try:
        with connection.cursor() as cursor:
            if search_option == '1':
                search_word = input("Enter book title: ")
                cursor.callproc('get_books_by_name', [search_word])
            elif search_option == '2':
                keyword = input("Enter a keyword: ")
                cursor.callproc('get_book_with_keyword', [keyword])
            elif search_option == '3':
                cursor.execute("SELECT genre_name FROM bookgenre")
                genres = cursor.fetchall()
                if not genres:
                    print("No book genres found.")
                    return

                print("Available Book Genres:")
                for genre in genres:
                    print(genre['genre_name'])

                genre = input("Enter a genre: ")
                cursor.callproc('get_book_with_genre', [genre])
            else:
                print("Invalid option.")
                return

            # Fetch and display the results
            results = cursor.fetchall()
            if results:
                print("Search Results:")
                for book in results:
                    print(f"Book ID: {book['book_id']},Book Name: {book['book_name']}")
                    return True
            else:
                print("No books found.")
                return False

    except Exception as e:
        print(f"Error during searching: {e}")
        return False

def get_favorite_books(connection, user_email):
    try:
        with connection.cursor() as cursor:
            cursor.callproc('get_user_favorite_books', [user_email])
            results = cursor.fetchall()
            if results:
                print("Your Favorite Books:")
                for book in results:
                    print(f"Book ID: {book['book_id']},Book Name: {book['book_name']}")
                    return True
            else:
                print("You have no favorite books.")
                return False
    except Exception as e:
        print(f"Error retrieving favorite books: {e}")
        return False

def publish_book(connection, user_email):
    try:
        with connection.cursor() as cursor:
            # Retrieve and display all available book genres
            cursor.execute("SELECT genre_name FROM bookgenre")
            genres = cursor.fetchall()
            if not genres:
                print("No book genres found.")
                return

            print("Available Book Genres:")
            for genre in genres:
                print(genre['genre_name'])

            # Prompt the user to enter book details
            book_name = input("Enter book name: ")
            book_text = input("Enter book text: ")
            genre_name = input("Enter genre name: ")
            keyword_text = input("Enter a keyword for the book: ")

            # Retrieve the user_name associated with the user_email
            cursor.execute("SELECT user_name FROM user WHERE email = %s", (user_email,))
            result = cursor.fetchone()
            if result:
                user_name = result['user_name']
            else:
                print("User not found.")
                return

            # Call the create_book procedure with the retrieved user_name
            cursor.callproc('create_book', [book_name, book_text, genre_name, user_name, user_email, keyword_text])
            connection.commit()
            print("Book published successfully.")
    except Exception as e:
        print(f"Error publishing book: {e}")



def update_book(connection, author_email):
    try:
        with connection.cursor() as cursor:
            # First, get the books written by the author
            cursor.execute("SELECT user_name FROM user WHERE email = %s", (author_email,))
            result = cursor.fetchone()
            if result:
                user_name = result['user_name']
            else:
                print("User not found.")
                return
            cursor.callproc('get_books_by_author', [user_name])
            books = cursor.fetchall()
            if not books:
                print("You have not written any books.")
                return

            print("Books you've written:")
            for book in books:
                print(f"Book ID: {book['book_id']}, Book Name: {book['book_name']}")

            # Then, ask the author to choose one to update
            book_id = input("Enter the ID of the book you want to update: ")
            new_text = input("Enter the new text for the book: ")

            # Update the book
            cursor.callproc('update_book_text', [book_id, new_text])
            connection.commit()
            print("Book updated successfully.")

    except Exception as e:
        print(f"Error updating book: {e}")




def main():
    print("Welcome to the Fanfiction Forum!")

    username = input("Enter your MySQL username: ")
    password = input("Enter your MySQL password: ")
    connection = get_database_connection(username, password)

    if connection is None:
        print("Failed to connect to the database.")
        sys.exit(1)  # Exit the program if the database connection fails


    user_email = None
    if check_account():
        while not user_email:
            user_email = login_user(connection)
            if not user_email:
                choice = input("Choose an option: 1) Try again, 2) Find your password, 3) Register instead: ")
                if choice == '1':
                    continue

                elif choice == '2':
                    if not recover_password(connection):
                        register_choice = input("Do you want to register an account? (yes/no): ").lower()
                        if register_choice == 'yes':
                            user_email = register_user(connection)
                            break
                        else:
                            print("we have to register your account")
                            user_email = register_user(connection)
                            break


                elif choice == '3':
                    user_email = register_user(connection)
    else:
        user_email = register_user(connection)

    # User is now logged in
    if user_email:
        while True:
            option = main_page_options()

            if option == '1':
                if search_book(connection):
                    chosen_book_id = input("Enter the book ID you want to interact with: ")
                    actions_to_book(connection, user_email, chosen_book_id)
            elif option == '2':
                if get_favorite_books(connection, user_email):
                    chosen_book_id = input("Enter the book ID you want to interact with: ")
                    actions_to_book(connection, user_email, chosen_book_id)
            elif option == '3':
                publish_book(connection, user_email)
            elif option == '4':
                update_book(connection, user_email)
            elif option == '5':
                delete_book(connection, user_email)
            else:
                print("Invalid option, please try again.")

            go_back = input("Do you want to go back to the main menu? If no, sign out (yes/no): ").lower()
            if go_back != 'yes':
                print("Signing out...")
                break

    # Close the database connection before exiting
    connection.close()

if __name__ == "__main__":
    main()
