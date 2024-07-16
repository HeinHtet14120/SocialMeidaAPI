from model.DatabasePool import DatabasePool

class Payment:
    @classmethod
    def get_next_invoice_number(cls):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = "SELECT invoice_number FROM invoices ORDER BY invoice_number DESC LIMIT 1"
            cursor.execute(sql)

            result = cursor.fetchone()

            if result and 'invoice_number' in result:
                invoice_number = result['invoice_number']
                if invoice_number:
                    last_invoice_number = int(invoice_number[3:])
                    new_invoice_number = "INV" + str(last_invoice_number + 1)
            else:
                # If no invoice number exists yet, start from INV1000000001
                new_invoice_number = "INV1000000001"

            return new_invoice_number

        except Exception as e:
            print("Error:", e)

        finally:
            dbConn.close()
            print("Connection released")

    @classmethod
    def get_next_ticket_number(cls, ticket_number):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = "SELECT ticket_number FROM tickets WHERE ticket_number = %s"
            cursor.execute(sql, (ticket_number,))

            result = cursor.fetchone()

            return result

        except Exception as e:
            print("Error:", e)

        finally:
            dbConn.close()
            print("Connection released")

    @classmethod
    def addPayment(cls, invoice_number, payment_intent_id, user_id, event_id, client_ip, address_line_1, city, state, postal_code,
                                                        country_code, address_source, number_of_tickets, amount_total, event_cost, nett_amount, tax):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            sql = """
                INSERT INTO invoices (invoice_number, payment_intent_id, user_id, event_id, ip_address, 
                address_line_1, city, postal_code, state, country, address_source, event_cost, number_of_tickets, 
                invoice_amount, nett_amount, tax)
                VALUES (%s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s)
                """

                 # Create a list of tuples for executemany
            data = (invoice_number, payment_intent_id, user_id, event_id, client_ip, 
                    address_line_1, city, postal_code, state, country_code, address_source, event_cost, number_of_tickets,
                    amount_total, nett_amount, tax)

            cursor.execute(sql, data)
            dbConn.commit()
            paymentId = cursor.lastrowid
            return paymentId

        except Exception as e:
            print("Error while inserting payment:", e)
        finally:
            cursor.close()
            dbConn.close()
            print("Connection released")


    @classmethod
    def addTicket(cls, invoice_number, tickets):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            sql = "INSERT INTO tickets (invoice_number, ticket_number, image) VALUES (%s, %s, %s)"

            if not isinstance(tickets, list):
                tickets = [tickets]

            # Create a list of tuples for executemany
            data = [(invoice_number, ticket['ticket_number'], ticket['qr_image']) for ticket in tickets]

            cursor.executemany(sql, data)
            dbConn.commit()

            return invoice_number 
        
        except Exception as e:
            print("Error while inserting tickets:", e)

        finally:
            cursor.close()
            dbConn.close()
            print("Connection released")

    @classmethod
    def getInvoiceDetails(cls, payment_intent_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            sql = "SELECT invoice_number, invoice_amount, user_id, event_id from invoices where payment_intent_id = %s"
            cursor.execute(sql, (payment_intent_id,))

            result = cursor.fetchone()
            return result
        
        except Exception as e:
            print("Error while getting invoice details:", e)

        finally:
            cursor.close()
            dbConn.close()
            print("Connection released")

    @classmethod
    def getTickets(cls, invoice_number):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            sql = "SELECT * from tickets where invoice_number = %s"
            cursor.execute(sql, (invoice_number,))

            result = cursor.fetchall()
            return result
        
        except Exception as e:
            print("Error while getting tickets details:", e)

        finally:
            cursor.close()
            dbConn.close()
            print("Connection released")

    
    @classmethod
    def updatePaidStatus(cls, payment_intent_id, invoice_number, amount):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)


            sql = "INSERT INTO payments (invoice_number, payment_intent_id, amount_paid) VALUES (%s, %s, %s)"

            cursor.execute(sql, (invoice_number, payment_intent_id, amount))
            dbConn.commit()
            paymentId = cursor.lastrowid
            return paymentId
        
        except Exception as e:
            print("Error while inserting paid status:", e)

        finally:
            cursor.close()
            dbConn.close()
            print("Connection released")

    
    @classmethod
    def has_user_already_bought(cls, user_id, event_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = "SELECT id FROM payments WHERE user_id = %s AND event_id = %s"
            cursor.execute(sql, (user_id, event_id))

            results = cursor.fetchone()

            return results

        except Exception as e:
            print(f"Error reading data from MySQL table: {e}")

        finally:
                cursor.close()
                dbConn.close()
                print("Connection released")
