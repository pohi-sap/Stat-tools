import sqlite3

class _sqlite(object):

    #def __init__(self, ):
    #    pass
    def giveinfo():
        print("successfully instantiated db obj")

def make_table(cur, source):
    print(f"Creating {source} table")
    cur.execute(f'CREATE TABLE {source}(statute,text)')
    print("Done")

def check_table_exists(cur):
    print("Checking sqlite_master for table, found:",end=' ')
    res = cur.execute("SELECT name FROM sqlite_master")
    print(res.fetchone()[0])


def insert_into_table(con, cur, source, statute, statute_text):
    insert_values = (f"""

                INSERT INTO {source} VALUES
                ('{statute}', '{statute_text}')

                """)
    cur.execute(insert_values)
    con.commit()

def peek_source_table(cur, source):
    res = cur.execute(f"SELECT * FROM {source}")
    print(res.fetchall())

def main(source, statute, statute_text):
    con = sqlite3.connect(":memory:")

    cur = con.cursor()

    # Minimum viable product is
    # get output of current thing and put it in db.
    # use source as table, then full statute [11.21] as row entry
    # |    TN(table)    |
    # | statute(char) ,  text(char) |

    #source = 'tax_code'
    #statute = '11.23'
    #statute_text = 'statute text goes here'
    make_table(cur, source)
    check_table_exists(cur)
    insert_into_table(con, cur, source, statute, statute_text)
    peek_source_table(cur, source)

source = 'tax_code'
statute = '11.23'
statute_text = 'statute text goes here'
if __name__ == '__main__':
    main(source, statute, statute_text)

# find out how to handle connection + cursor in the correct way, using this file for clean operations.
