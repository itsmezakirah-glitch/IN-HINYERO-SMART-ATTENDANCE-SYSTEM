from login import (
    student_login,
    admin_login
)

from attendance import (
    create_session,
    generate_qr_session,
    mark_attendance,
    manual_tagging,
    change_admin_username,
    change_admin_password
)

from report import generate_report

while True:

    print("""
========== ATTENDANCE SYSTEM ==========

1. Student Login
2. Admin Login
3. Exit
""")

    choice = input(
        "Enter choice: "
    ).strip()

    if choice not in [
        "1",
        "2",
        "3"
    ]:

        print(
            "\nERROR: Invalid choice."
        )

        continue

    # STUDENT LOGIN
    if choice == "1":

        student = student_login()

        if student:

            print("\n========== QR CODE SCAN ==========")
            print("Please scan the QR code to continue...")
            input("Press Enter after scanning QR code: ")

            print("\n========== FACIAL RECOGNITION ==========")
            print("Please look at the camera for facial recognition...")
            input("Press Enter after facial recognition is complete: ")

            mark_attendance(student)

    # ADMIN LOGIN
    elif choice == "2":

        if admin_login():

            while True:

                print("""
========== ADMIN PANEL ==========

1. Create Attendance Session
2. Generate QR Code Session
3. Generate Attendance Report
4. Manual Tagging
5. Change Admin Username
6. Change Admin Password
7. Logout
""")

                admin_choice = input(
                    "Enter choice: "
                ).strip()

                if admin_choice not in [
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7"
                ]:

                    print(
                        "\nERROR: Invalid choice."
                    )

                    continue

                # CREATE SESSION
                if admin_choice == "1":

                    create_session()

                # GENERATE QR SESSION
                elif admin_choice == "2":

                    generate_qr_session()

                # GENERATE REPORT
                elif admin_choice == "3":

                    generate_report()

                # MANUAL TAGGING
                elif admin_choice == "4":

                    manual_tagging()

                # CHANGE USERNAME
                elif admin_choice == "5":

                    change_admin_username()

                # CHANGE PASSWORD
                elif admin_choice == "6":

                    change_admin_password()

                # LOGOUT
                elif admin_choice == "7":

                    print(
                        "\nAdmin Logged Out."
                    )

                    break

    # EXIT
    elif choice == "3":

        print(
            "\nSystem Closed."
        )

        break