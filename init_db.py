import config
import database


def main(db_file=None):
    database.init_db(db_file)
    print("Database created:", db_file or config.DB_FILE)


if __name__ == "__main__":
    main()