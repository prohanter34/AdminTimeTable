import psycopg2


conn = psycopg2.connect(database="raspisanie",
                                     user="postgres",
                                     password="pretki23",
                                     host="localhost",
                                     port="5432")
cursor = conn.cursor()