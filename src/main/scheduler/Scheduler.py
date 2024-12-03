from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Create patient failed")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again")
        return
    
    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Create patient failed")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Create patient failed")
        print(e)
        return
    print("Created user ", username)

def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in, try again")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login patient failed")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login patient failed")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login patient failed")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login patient failed")
    else:
        print("Logged in as " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    global current_caregiver
    global current_patient

    # check if a user has already logged in
    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return
    
    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again")
        return
    
    date = tokens[1]
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_date = "SELECT Username FROM Availabilities WHERE Time = %s ORDER BY Username"
    select_vaccines = "SELECT Name, Doses FROM Vaccines"
    try:
        cursor = conn.cursor(as_dict=True)
        # query caregivers
        cursor.execute(select_date, date)
        caregivers = [row['Username'] for row in cursor]

        # query vaccines
        cursor.execute(select_vaccines)
        vaccines = [(row['Name'], row['Doses']) for row in cursor]

        # print caregivers
        for caregiver in caregivers:
            print(caregiver)
        
        # print vaccines
        for name, doses in vaccines:
            print(f"{name} {doses}")
        
    except pymssql.Error as e:
        print("Please try again")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please try again")
        return
    except Exception as e:
        print("Please try again")
        print("Error:", e)
        return
    finally:
        cm.close_connection()

def reserve(tokens):
    global current_patient
    # check 1: check if a user's already logged in
    if current_patient is None and current_caregiver is None:
        print("Please login first")
        return
    
    #  check 2: check if the current logged-in user is a patient
    if current_patient is None:
        print("Please login as a patient")
        return

    # check 3: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again")
        return

    date = tokens[1]
    vaccine_name = tokens[2]
    
    cm = ConnectionManager()
    conn = cm.create_connection()

    try:
        cursor = conn.cursor(as_dict=True)

        select_caregiver = "SELECT TOP 1 Username FROM Availabilities WHERE Time = %s ORDER BY Username"
        cursor.execute(select_caregiver, date)
        caregiver = cursor.fetchone()

        # Check caregiver availability
        if not caregiver:
            print("No caregiver is available")
            return
        
        caregiver_name = caregiver['Username']

        select_vaccine = "SELECT Doses FROM Vaccines WHERE Name = %s"
        cursor.execute(select_vaccine, vaccine_name)
        vaccine = cursor.fetchone()
        # Check vaccine availability
        if not vaccine or vaccine['Doses'] < 1:
            print("Not enough available doses")
            return 
        
        # Create appointment
        create_appointment_id = "SELECT NEXT VALUE FOR AppointmentSeq AS AppointmentID"
        cursor.execute(create_appointment_id)
        appointment_id = cursor.fetchone()['AppointmentID']

        insert_appointment = "INSERT INTO Reservations (ID, PatientName, CaregiverName, VaccineName, Time) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_appointment, (appointment_id, current_patient.username, caregiver_name, vaccine_name, date))

        # Update caregiver availability and vaccine doses
        delete_availability = "DELETE FROM Availabilities WHERE Username = %s AND Time = %s"
        cursor.execute(delete_availability, (caregiver_name, date))

        update_vaccines = "UPDATE Vaccines SET Doses = Doses - 1 WHERE Name = %s"
        cursor.execute(update_vaccines, vaccine_name)

        conn.commit()

        print(f"Appointment ID {appointment_id}, Caregiver username {caregiver_name}")

    except pymssql.Error as e:
        print("Please try again")
        print("Db-Error:", e)
        conn.rollback()
    except ValueError:
        print("Please try again")
        return
    except Exception as e:
        print("Please try again")
        print("Error:", e)
        conn.rollback()
    finally:
        cm.close_connection()

def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    global current_caregiver, current_patient
    # check 1: check if a user's already logged in
    if current_patient is None and current_caregiver is None:
        print("Please login first")
        return
    
    # check 3: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    try:
        appointment_id = int(tokens[1])
    except ValueError:
        print("Invalid appointment ID format!")
        return
    
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    try:
        select_appointment = "SELECT ID, Time, CaregiverName, PatientName FROM Reservations WHERE ID = %s"
        cursor.execute(select_appointment, appointment_id)
        appointment = cursor.fetchone()

        if appointment is None:
            print("Appointment not found!")
            return
        
        # Check if the current user is authorized to cancel this appointment
        if current_caregiver is not None and appointment["CaregiverName"] != current_caregiver.username:
            print("You are not authorized to cancel this appointment.")
            return
        if current_patient is not None and appointment["PatientName"] != current_patient.username:
            print("You are not authorized to cancel this appointment.")
            return
        
         # Delete the appointment from the Reservations table
        delete_appointment = "DELETE FROM Reservations WHERE ID = %s"
        cursor.execute(delete_appointment, appointment_id)

        # Update the caregiver's availability
        update_availability = "INSERT INTO Availabilities (Username, Time) VALUES (%s, %s)"
        cursor.execute(update_availability, (appointment["CaregiverName"], appointment["Time"]))

        conn.commit()
        print(f"Appointment {appointment_id} has been canceled successfully.")

    except pymssql.Error as e:
        print("An error occurred while processing the cancellation.")
        print("Db-Error:", e)
        conn.rollback()
    except Exception as e:
        print("An unexpected error occurred.")
        print("Error:", e)
        conn.rollback()
    finally:
        cm.close_connection()

def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    global current_caregiver, current_patient
    # check 1: check if a user's already logged in
    if current_patient is None and current_caregiver is None:
        print("Please login first")
        return
    
    # check 1: the length for tokens need to be exactly 1 to include all information (with the operation name)
    if len(tokens) != 1:
        print("Please try again")
        return
    
    cm = ConnectionManager()
    conn = cm.create_connection()

    try:
        cursor = conn.cursor(as_dict=True)

        if current_caregiver:
            select_appointments = "SELECT ID, VaccineName, Time, PatientName FROM Reservations WHERE CaregiverName = %s ORDER BY ID"
            cursor.execute(select_appointments, current_caregiver.username)
            appointments = cursor.fetchall()
            for appt in appointments:
                print(f"{appt['ID']} {appt['VaccineName']} {appt['Time']} {appt['PatientName']}")

        elif current_patient:
            select_appointments = "SELECT ID, VaccineName, Time, CaregiverName FROM Reservations WHERE PatientName = %s ORDER BY ID"
            cursor.execute(select_appointments, current_patient.username)
            appointments = cursor.fetchall()
            for appt in appointments:
                print(f"{appt['ID']} {appt['VaccineName']} {appt['Time']} {appt['CaregiverName']}")

    except pymssql.Error as e:
        print("Please try again")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Please try again")
        print("Error:", e)
        return
    finally:
        cm.close_connection()    

def logout(tokens):
    global current_patient, current_caregiver
    
    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return
    
    if len(tokens) != 1:
        print("Please try again")
        return
    
    current_patient = None
    current_caregiver = None
    print('Successfully logged out')


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
