import psycopg
from faker import Faker
import random
from datetime import timedelta, date


"""
Daily busssiness is the goal
    -Books checked out and in.
     +Either random amounts of specified for check in and out.
     +Fines are calculated in PSQL
     +Option for new customers to check out books. For better knowlege of joins.

    -Lets doccument as we go. Have things explanatory for others. AKA job interviews.

    ?Have books returned to differnet libraries than they were checked out form. Set up a min and max at all locations and have them shipped back. 
"""


fake = Faker()


#connecting to PSQL
conn = psycopg.connect(
    dbname="library",
    user="malachi",
    password="otheroldguys1",
    host="localhost"
)
cur = conn.cursor()

#AI CODE for fetching book and customer info. I don't understand it yet. Need to update variables
def get_ids(table, id_col):
    cur.execute(f"SELECT {id_col} FROM {table}")
    return [row[0] for row in cur.fetchall()]


#New customer enrollment by day. Lots of AI help for psycopg syntax. 
def new_customer(sim_date, chance=0.2):
    if random.random() < chance:
        count = random.randint(1, 3)
        data  = [
            (fake.first_name(), fake.last_name(),
             fake.unique.email(), sim_date)
            for _ in range(count)
        ]
        cur.executemany(cur, """
            INSERT INTO customers (first_name, last_name, email, joined_date)
            VALUES %s
        """, data)
        print(f"  {sim_date} → {count} new member(s) joined")


#Check out simulation. Less AI for syntax. Still using above funtion for reference.
def members_checkout_books(sim_date, customers, books, chance=0.6):
    """Some members check out books today."""
    if random.random() < chance:
        count = random.randint(1, 8)
        checkouts = []

        for _ in range(count):
            checkouts.append((
                random.choice(customers),
                random.choice(books),
                sim_date,
                sim_date + timedelta(days=14)
            ))

        cur.executemany("""
            INSERT INTO check_out
              (customer_id, bookid, order_date, due_date)
            VALUES (%s, %s, %s, %s)
        """, checkouts)
        print(f"  {sim_date} → {count} book(s) checked out")


#Return book simulation. No AI this time. I lied. Used AI again for random.choices wieght help. Didn't know about that.
#Made a change on return dates. It had a random day choices outside of sim_date. So, I went with returns happen in sim time.
#Using top syntax for refference. Gotta know how its written to think about solutions.
def members_return_books(sim_date):

    cur.execute("""
        SELECT id, due_date
        FROM check_out
        WHERE return_date IS NULL AND due_date BETWEEN %s AND %s
    """, (sim_date - timedelta(days=7), sim_date + timedelta(days=3)))

    due_soon = cur.fetchall()
    if not due_soon:
        return


    returns = []
    for checkout_id, due_date in due_soon:
            scenario = random.choices(
                ["return today", "skip"],
                weights=[70, 30]
            )[0]

            if scenario == "return today":
                returns.append((sim_date, checkout_id))

            if returns:
                cur.executemany("""
                    UPDATE check_out
                    SET return_date = %s
                    WHERE id = %s
                """, returns)
                print(f"  {sim_date} → {len(returns)} book(s) returned")


#Making a changes for pays to be paid each day. 
#There's a trigger in database to add fines to books.
def pay_outstanding_fines(sim_date, chance=0.4):

    if random.random() < chance:
        cur.execute("""
            UPDATE fines
            SET status = 'paid'
            WHERE fine_id IN(
                SELECT fine_id
                FROM fines
                WHERE status = 'unpaid'
                ORDER BY RANDOM()
                LIMIT %s
            )
        """, (random.randint(1, 5),))
        paid = cur.rowcount
        if paid:
            print(f"  {sim_date} → {paid} fine(s) paid")

#Runs the simulation. 
#Kept print from Claude.
def run_simulation(start_date, end_date):
    print(f"\n📚 Library simulation: {start_date} → {end_date}\n")

    sim_date = start_date
    while sim_date <= end_date:
        if sim_date.weekday() < 5:  
            customers = get_ids("customers", "id")
            books     = get_ids("books", "bookid")
            members_checkout_books(sim_date, customers, books)
            members_return_books(sim_date)
            pay_outstanding_fines(sim_date)

            conn.commit()

        sim_date += timedelta(days=1)

        conn.commit()

        print("\n✅ Simulation complete!")
        print(f"\n📚 Library simulation day {sim_date}\n")
        print_summary()


def print_summary():
    cur.execute("SELECT COUNT(*) FROM customers")
    print(f"\n  Total customers : {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM books")
    print(f"  Total books     : {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM check_out")
    print(f"  Total checkouts : {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM check_out WHERE return_date IS NULL")
    print(f"  Still checked out: {cur.fetchone()[0]}")


    cur.execute("""
        SELECT COUNT(*) FROM check_out
        WHERE return_date IS NULL
          AND due_date < CURRENT_DATE
    """)
    print(f"  Currently overdue: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*), SUM(amount) FROM fines WHERE status = 'unpaid'")
    row = cur.fetchone()
    print(f"  Unpaid fines    : {row[0]} totalling ${row[1] or 0:.2f}")




if __name__ == "__main__":
    run_simulation(
        start_date=date(2025, 8, 29),
        end_date=date(2026, 9, 30)
    )





