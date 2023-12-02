from datetime import datetime

"""
For api_admin_set_categories
"""

correct_categories = {
    "categories": [
        {
            "categoryId": "a",
            "color": "#FF0000",
            "maxPoints": 1500,
            "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime(
                "%Y-%m-%dT%H:%M:%S",
            ),
            "entryFee": 10,
            "rewardFirst": 200,
            "rewardSecond": 100,
            "rewardSemi": 50,
            "maxPlayers": 40,
        },
        {
            "categoryId": "b",
            "color": "#FFFF00",
            "minPoints": 800,
            "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime(
                "%Y-%m-%dT%H:%M:%S",
            ),
            "entryFee": 20,
            "rewardFirst": 200,
            "rewardSecond": 100,
            "rewardSemi": 50,
            "maxPlayers": 40,
        },
        {
            "categoryId": "c",
            "color": "#FFFFFF",
            "minPoints": 800,
            "maxPoints": 2000,
            "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime(
                "%Y-%m-%dT%H:%M:%S",
            ),
            "womenOnly": True,
            "entryFee": 20,
            "rewardFirst": 200,
            "rewardSecond": 100,
            "rewardSemi": 50,
            "maxPlayers": 40,
            "overbookingPercentage": 10,
        },
        {
            "categoryId": "d",
            "maxPoints": 1500,
            "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime(
                "%Y-%m-%dT%H:%M:%S",
            ),
            "entryFee": 10,
            "rewardFirst": 200,
            "rewardSecond": 100,
            "rewardSemi": 50,
            "maxPlayers": 40,
        },
    ],
}

correct_categories_response = [
    {
        "categoryId": "a",
        "color": "#FF0000",
        "entryCount": 0,
        "entryFee": 10,
        "maxPlayers": 40,
        "maxPoints": 1500,
        "minPoints": 0,
        "overbookingPercentage": 0,
        "rewardFirst": 200,
        "rewardQuarter": None,
        "rewardSecond": 100,
        "rewardSemi": 50,
        "startTime": "2023-12-20T10:00:00",
        "womenOnly": False,
    },
    {
        "categoryId": "b",
        "color": "#FFFF00",
        "entryCount": 0,
        "entryFee": 20,
        "maxPlayers": 40,
        "maxPoints": 4000,
        "minPoints": 800,
        "overbookingPercentage": 0,
        "rewardFirst": 200,
        "rewardQuarter": None,
        "rewardSecond": 100,
        "rewardSemi": 50,
        "startTime": "2023-12-20T10:00:00",
        "womenOnly": False,
    },
    {
        "categoryId": "c",
        "color": "#FFFFFF",
        "entryCount": 0,
        "entryFee": 20,
        "maxPlayers": 40,
        "maxPoints": 2000,
        "minPoints": 800,
        "overbookingPercentage": 10,
        "rewardFirst": 200,
        "rewardQuarter": None,
        "rewardSecond": 100,
        "rewardSemi": 50,
        "startTime": "2023-12-20T10:00:00",
        "womenOnly": True,
    },
    {
        "categoryId": "d",
        "color": None,
        "entryCount": 0,
        "entryFee": 10,
        "maxPlayers": 40,
        "maxPoints": 1500,
        "minPoints": 0,
        "overbookingPercentage": 0,
        "rewardFirst": 200,
        "rewardQuarter": None,
        "rewardSecond": 100,
        "rewardSemi": 50,
        "startTime": "2023-12-20T10:00:00",
        "womenOnly": False,
    },
]

incorrect_categories_missing_categories_field = {}

incorrect_categories_missing_badly_formatted_data = {
    "categories": [
        {
            "categoryId": "a",
            "color": "#FF0000",
            "maxPoints": 1500,
            "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime(
                "%Y-%m-%dT%H:%M:%S",
            ),
            "rewardFirst": 200,
            "rewardSecond": 100,
            "rewardSemi": 50,
            "maxPlayers": 40,
        },
        {
            "categoryId": "b",
            "color": "#FFFF00",
            "minPoints": 800,
            "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime(
                "%Y-%m-%dT%H:%M:%S",
            ),
            "entryFee": 20,
            "rewardFirst": 200,
            "rewardSecond": 100,
            "rewardSemi": 50,
            "maxPlayers": "aa",
        },
    ],
}

incorrect_categories_duplicate = {
    "categories": [
        {
            "categoryId": "a",
            "color": "#FF0000",
            "maxPoints": 1500,
            "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime(
                "%Y-%m-%dT%H:%M:%S",
            ),
            "entryFee": 10,
            "rewardFirst": 200,
            "rewardSecond": 100,
            "rewardSemi": 50,
            "maxPlayers": 40,
        },
        {
            "categoryId": "a",
            "color": "#FFFF00",
            "minPoints": 800,
            "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime(
                "%Y-%m-%dT%H:%M:%S",
            ),
            "entryFee": 20,
            "rewardFirst": 200,
            "rewardSecond": 100,
            "rewardSemi": 50,
            "maxPlayers": 40,
        },
    ],
}

"""
For api_admin_make_payment
"""

correct_payment_pay_all = {"licenceNo": 4526124, "categoryIds": ["B", "F"]}
correct_payment_pay_all_response = {
    "actualPaidNow": 14,
    "actualRemaining": 0,
    "allEntries": {"amount": 14, "categoryIds": ["B", "F"]},
    "leftToPay": {"amount": 0, "categoryIds": []},
    "paymentDiff": 0,
    "settledNow": {"amount": 14, "categoryIds": ["B", "F"]},
    "settledPreviously": {"amount": 0, "categoryIds": []},
}

correct_payment_pay_all_by_name = {
    "firstName": "Wihelbl",
    "lastName": "EZWLKRWE",
    "categoryIds": ["B", "F"],
}

correct_payment_pay_all_by_name_response = {
    "actualPaidNow": 14,
    "actualRemaining": 0,
    "allEntries": {"amount": 14, "categoryIds": ["B", "F"]},
    "leftToPay": {"amount": 0, "categoryIds": []},
    "paymentDiff": 0,
    "settledNow": {"amount": 14, "categoryIds": ["B", "F"]},
    "settledPreviously": {"amount": 0, "categoryIds": []},
}

correct_payment_pay_partial = {"licenceNo": 4526124, "categoryIds": ["B"]}
correct_payment_pay_partial_response = {
    "actualPaidNow": 7,
    "actualRemaining": 7,
    "allEntries": {"amount": 14, "categoryIds": ["B", "F"]},
    "leftToPay": {"amount": 7, "categoryIds": ["F"]},
    "paymentDiff": 0,
    "settledNow": {"amount": 7, "categoryIds": ["B"]},
    "settledPreviously": {"amount": 0, "categoryIds": []},
}

correct_payment_previously_paid = {"licenceNo": 5326002, "categoryIds": ["B"]}
correct_payment_previously_paid_response = {
    "actualPaidNow": 7,
    "actualRemaining": 0,
    "allEntries": {"amount": 14, "categoryIds": ["B", "G"]},
    "leftToPay": {"amount": 0, "categoryIds": []},
    "paymentDiff": 0,
    "settledNow": {"amount": 7, "categoryIds": ["B"]},
    "settledPreviously": {"amount": 7, "categoryIds": ["G"]},
}

correct_payment_all_recap_positive = {"licenceNo": 722370, "categoryIds": ["7"]}
correct_payment_all_recap_positive_response = {
    "actualPaidNow": 7,
    "actualRemaining": 7,
    "allEntries": {"amount": 21, "categoryIds": ["A", "5", "7"]},
    "leftToPay": {"amount": 7, "categoryIds": ["5"]},
    "paymentDiff": 0,
    "settledNow": {"amount": 7, "categoryIds": ["7"]},
    "settledPreviously": {"amount": 7, "categoryIds": ["A"]},
}

correct_payment_default_actual = {
    "licenceNo": 722370,
    "categoryIds": ["7"],
    "actualPaid": 7,
}
correct_payment_default_actual_response = {
    "actualPaidNow": 7,
    "actualRemaining": 7,
    "allEntries": {"amount": 21, "categoryIds": ["A", "5", "7"]},
    "leftToPay": {"amount": 7, "categoryIds": ["5"]},
    "paymentDiff": 0,
    "settledNow": {"amount": 7, "categoryIds": ["7"]},
    "settledPreviously": {"amount": 7, "categoryIds": ["A"]},
}

correct_payment_nondefault_actual = {
    "licenceNo": 722370,
    "categoryIds": ["7"],
    "actualPaid": 8,
}
correct_payment_nondefault_actual_response = {
    "actualPaidNow": 8,
    "actualRemaining": 6,
    "allEntries": {"amount": 21, "categoryIds": ["A", "5", "7"]},
    "leftToPay": {"amount": 7, "categoryIds": ["5"]},
    "paymentDiff": 1,
    "settledNow": {"amount": 7, "categoryIds": ["7"]},
    "settledPreviously": {"amount": 7, "categoryIds": ["A"]},
}

correct_payment_nonzero_diff = {"licenceNo": 9426636, "categoryIds": ["2"]}
correct_payment_nonzero_diff_response = {
    "actualPaidNow": 6,
    "actualRemaining": 7,
    "allEntries": {"amount": 28, "categoryIds": ["D", "F", "2", "6"]},
    "leftToPay": {"amount": 7, "categoryIds": ["6"]},
    "paymentDiff": 0,
    "settledNow": {"amount": 7, "categoryIds": ["2"]},
    "settledPreviously": {"amount": 14, "categoryIds": ["D", "F"]},
}

correct_payment_nonzero_diff_nondefault_actual = {
    "licenceNo": 9426636,
    "categoryIds": ["2"],
    "actualPaid": 5,
}
correct_payment_nonzero_diff_nondefault_actual_response = {
    "actualPaidNow": 5,
    "actualRemaining": 8,
    "allEntries": {"amount": 28, "categoryIds": ["D", "F", "2", "6"]},
    "leftToPay": {"amount": 7, "categoryIds": ["6"]},
    "paymentDiff": -1,
    "settledNow": {"amount": 7, "categoryIds": ["2"]},
    "settledPreviously": {"amount": 14, "categoryIds": ["D", "F"]},
}

incorrect_payment_missing_player_identifier_json_field = {
    "firstName": "Dqdjfklm",
    "categoryIds": ["G"],
}

incorrect_payment_missing_categories_json_field = {"licenceNo": 5326002}

incorrect_payment_duplicate_payment = {"licenceNo": 5326002, "categoryIds": ["G"]}

incorrect_payment_without_registration = {"licenceNo": 5326002, "categoryIds": ["A"]}

"""
For api_admin_delete_entries
"""

correct_delete_entries_all = {"licenceNo": 722370, "categoryIds": ["A", "5", "7"]}
correct_delete_entries_all_response = []

correct_delete_entries_partial = {"licenceNo": 722370, "categoryIds": ["A", "5"]}
correct_delete_entries_partial_response = [
    {
        "categoryId": "7",
        "color": "00FFFF",
        "entryId": 320,
        "licenceNo": 722370,
        "markedAsPaid": False,
        "registrationTime": "2023-09-17T05:10:51",
        "showedUp": False,
    },
]

incorrect_delete_entries_missing_player_identifier_json_field = {
    "firstName": "Fjhgzg",
    "categoryIds": ["A", "5"],
}

incorrect_delete_entries_missing_categories_json_field = {
    "firstName": "Fjhgzg",
    "lastname": "DFJQKL",
}

incorrect_delete_entries_nonexisting_player = {
    "licenceNo": 55555,
    "categoryIds": ["A", "5"],
}

incorrect_delete_entries_nonexisting_categories = {
    "licenceNo": 722370,
    "categoryIds": ["P", "5"],
}

incorrect_delete_entries_nonexisting_entries = {
    "licenceNo": 722370,
    "categoryIds": ["B", "5"],
}

"""
For api_admin_delete_player
"""

correct_delete_player_by_licence = {"licenceNo": 722370}

correct_delete_player_by_name = {"firstName": "Wihelbl", "lastName": "EZWLKRWE"}

incorrect_delete_player_missing_json_field = {"firstName": "Wihelbl"}

incorrect_delete_player_nonexisting_player_by_name = {
    "firstName": "Wfdjklbl",
    "lastName": "IDODLJSDLWE",
}

incorrect_delete_player_nonexisting_player_by_licence = {"licenceNo": 55555}

"""
For api_get_categories
"""

correct_get_categories_response = [
    {
        "categoryId": "A",
        "color": "000000",
        "entryCount": 30,
        "entryFee": 7,
        "maxPlayers": 72,
        "maxPoints": 900,
        "minPoints": 0,
        "overbookingPercentage": 20,
        "rewardFirst": 70,
        "rewardQuarter": None,
        "rewardSecond": 35,
        "rewardSemi": 20,
        "startTime": "2024-01-06T09:00:00",
        "womenOnly": False,
    },
    {
        "categoryId": "B",
        "color": "000000",
        "entryCount": 46,
        "entryFee": 7,
        "maxPlayers": 72,
        "maxPoints": 1500,
        "minPoints": 0,
        "overbookingPercentage": 15,
        "rewardFirst": 140,
        "rewardQuarter": None,
        "rewardSecond": 70,
        "rewardSemi": 35,
        "startTime": "2024-01-06T10:15:00",
        "womenOnly": False,
    },
    {
        "categoryId": "C",
        "color": "00FF00",
        "entryCount": 8,
        "entryFee": 10,
        "maxPlayers": 36,
        "maxPoints": 4000,
        "minPoints": 1300,
        "overbookingPercentage": 10,
        "rewardFirst": 300,
        "rewardQuarter": None,
        "rewardSecond": 150,
        "rewardSemi": 75,
        "startTime": "2024-01-06T11:30:00",
        "womenOnly": True,
    },
    {
        "categoryId": "D",
        "color": "00FF00",
        "entryCount": 41,
        "entryFee": 7,
        "maxPlayers": 72,
        "maxPoints": 1100,
        "minPoints": 0,
        "overbookingPercentage": 20,
        "rewardFirst": 100,
        "rewardQuarter": None,
        "rewardSecond": 50,
        "rewardSemi": 25,
        "startTime": "2024-01-06T12:45:00",
        "womenOnly": False,
    },
    {
        "categoryId": "E",
        "color": "FF0000",
        "entryCount": 29,
        "entryFee": 10,
        "maxPlayers": 72,
        "maxPoints": 4000,
        "minPoints": 1500,
        "overbookingPercentage": 0,
        "rewardFirst": 300,
        "rewardQuarter": None,
        "rewardSecond": 150,
        "rewardSemi": 75,
        "startTime": "2024-01-06T14:00:00",
        "womenOnly": False,
    },
    {
        "categoryId": "F",
        "color": "FF0000",
        "entryCount": 36,
        "entryFee": 7,
        "maxPlayers": 72,
        "maxPoints": 1300,
        "minPoints": 0,
        "overbookingPercentage": 10,
        "rewardFirst": 120,
        "rewardQuarter": None,
        "rewardSecond": 60,
        "rewardSemi": 30,
        "startTime": "2024-01-06T15:00:00",
        "womenOnly": False,
    },
    {
        "categoryId": "G",
        "color": None,
        "entryCount": 48,
        "entryFee": 7,
        "maxPlayers": 72,
        "maxPoints": 1900,
        "minPoints": 0,
        "overbookingPercentage": 15,
        "rewardFirst": 180,
        "rewardQuarter": None,
        "rewardSecond": 90,
        "rewardSemi": 45,
        "startTime": "2024-01-06T16:00:00",
        "womenOnly": False,
    },
    {
        "categoryId": "1",
        "color": "0000FF",
        "entryCount": 28,
        "entryFee": 7,
        "maxPlayers": 72,
        "maxPoints": 1700,
        "minPoints": 0,
        "overbookingPercentage": 20,
        "rewardFirst": 170,
        "rewardQuarter": None,
        "rewardSecond": 85,
        "rewardSemi": 45,
        "startTime": "2024-01-07T09:00:00",
        "womenOnly": False,
    },
    {
        "categoryId": "2",
        "color": "0000FF",
        "entryCount": 20,
        "entryFee": 7,
        "maxPlayers": 72,
        "maxPoints": 1400,
        "minPoints": 0,
        "overbookingPercentage": 0,
        "rewardFirst": 130,
        "rewardQuarter": None,
        "rewardSecond": 65,
        "rewardSemi": 35,
        "startTime": "2024-01-07T10:15:00",
        "womenOnly": False,
    },
    {
        "categoryId": "3",
        "color": "FFFF00",
        "entryCount": 23,
        "entryFee": 7,
        "maxPlayers": 72,
        "maxPoints": 2100,
        "minPoints": 0,
        "overbookingPercentage": 30,
        "rewardFirst": 200,
        "rewardQuarter": None,
        "rewardSecond": 100,
        "rewardSemi": 50,
        "startTime": "2024-01-07T11:30:00",
        "womenOnly": False,
    },
    {
        "categoryId": "4",
        "color": "FFFF00",
        "entryCount": 13,
        "entryFee": 7,
        "maxPlayers": 72,
        "maxPoints": 1000,
        "minPoints": 0,
        "overbookingPercentage": 20,
        "rewardFirst": 90,
        "rewardQuarter": None,
        "rewardSecond": 45,
        "rewardSemi": 25,
        "startTime": "2024-01-07T12:45:00",
        "womenOnly": False,
    },
    {
        "categoryId": "5",
        "color": None,
        "entryCount": 5,
        "entryFee": 7,
        "maxPlayers": 36,
        "maxPoints": 1600,
        "minPoints": 0,
        "overbookingPercentage": 20,
        "rewardFirst": 150,
        "rewardQuarter": None,
        "rewardSecond": 75,
        "rewardSemi": 40,
        "startTime": "2024-01-07T14:00:00",
        "womenOnly": True,
    },
    {
        "categoryId": "6",
        "color": "00FFFF",
        "entryCount": 15,
        "entryFee": 7,
        "maxPlayers": 72,
        "maxPoints": 1200,
        "minPoints": 0,
        "overbookingPercentage": 15,
        "rewardFirst": 110,
        "rewardQuarter": None,
        "rewardSecond": 55,
        "rewardSemi": 30,
        "startTime": "2024-01-07T15:00:00",
        "womenOnly": False,
    },
    {
        "categoryId": "7",
        "color": "00FFFF",
        "entryCount": 10,
        "entryFee": 7,
        "maxPlayers": 72,
        "maxPoints": 800,
        "minPoints": 0,
        "overbookingPercentage": 10,
        "rewardFirst": 60,
        "rewardQuarter": None,
        "rewardSecond": 30,
        "rewardSemi": 15,
        "startTime": "2024-01-07T16:00:00",
        "womenOnly": False,
    },
]

"""
For api_add_player
"""

correct_player = {
    "player": {
        "licenceNo": 555555,
        "firstName": "Fjhgzg",
        "lastName": "MHIHOBB",
        "email": "dfqkjqpoe@aieop.com",
        "phone": "33489653754",
        "gender": "F",
        "nbPoints": 1500,
        "club": "USKB",
    },
}

correct_player_response = {
    "bibNo": None,
    "club": "USKB",
    "email": "dfqkjqpoe@aieop.com",
    "firstName": "Fjhgzg",
    "gender": "F",
    "lastName": "MHIHOBB",
    "licenceNo": 555555,
    "nbPoints": 1500,
    "phone": "33489653754",
    "paymentDiff": 0,
}

incorrect_player_missing_player_json_field = {}

incorrect_player_missing_badly_formatted_data = {
    "player": {
        "licenceNo": 55555,
        "lastName": "QSDJKFLQZ",
        "email": "layceline@gmail.com",
        "phone": "33688261003",
        "gender": "F",
        "nbPoints": 1500,
        "club": "USKB",
    },
}

incorrect_player_duplicate = {
    "player": {
        "licenceNo": 4526124,
        "firstName": "Wihelbl",
        "lastName": "EZWLKRWE",
        "email": "nvzhltrsqr@mochsf.com",
        "phone": "+336919756238",
        "gender": "F",
        "nbPoints": 1149,
        "club": "USM OLIVET TENNIS DE TABLE",
    },
}

"""
For api_get_player
"""

correct_get_player_existing = {"licenceNo": 4526124}
correct_get_player_existing_response = {
    "player": {
        "bibNo": 94,
        "club": "USM OLIVET TENNIS DE TABLE",
        "email": "nvzhltrsqr@mochsf.com",
        "firstName": "Wihelbl",
        "gender": "F",
        "lastName": "EZWLKRWE",
        "licenceNo": 4526124,
        "nbPoints": 1149,
        "phone": "+336919756238",
        "paymentDiff": 0,
    },
    "registeredEntries": [
        {
            "categoryId": "B",
            "color": "000000",
            "entryId": 59,
            "licenceNo": 4526124,
            "markedAsPaid": False,
            "registrationTime": "2023-11-17T18:01:20",
            "showedUp": False,
        },
        {
            "categoryId": "F",
            "color": "FF0000",
            "entryId": 64,
            "licenceNo": 4526124,
            "markedAsPaid": False,
            "registrationTime": "2023-11-25T21:56:50",
            "showedUp": False,
        },
    ],
}

correct_get_player_nonexisting = {"licenceNo": 555555}
correct_get_player_nonexisting_response = {"player": None, "registeredEntries": []}

incorrect_get_player_missing_licence_no_json_field = {}

"""
For api_register_entries
"""

correct_registration = {"licenceNo": 4526124, "categoryIds": ["1"]}
correct_registration_response = [
    {
        "categoryId": "1",
        "color": "0000FF",
        "entryId": 353,
        "licenceNo": 4526124,
        "markedAsPaid": False,
        "registrationTime": "2023-11-30T12:18:21",
        "showedUp": False,
    },
    {
        "categoryId": "B",
        "color": "000000",
        "entryId": 59,
        "licenceNo": 4526124,
        "markedAsPaid": False,
        "registrationTime": "2023-11-17T18:01:20",
        "showedUp": False,
    },
    {
        "categoryId": "F",
        "color": "FF0000",
        "entryId": 64,
        "licenceNo": 4526124,
        "markedAsPaid": False,
        "registrationTime": "2023-11-25T21:56:50",
        "showedUp": False,
    },
]

correct_registration_with_duplicates = {
    "licenceNo": 4526124,
    "categoryIds": ["1", "B", "F"],
}
correct_registration_with_duplicates_response = [
    {
        "categoryId": "1",
        "color": "0000FF",
        "entryId": 353,
        "licenceNo": 4526124,
        "markedAsPaid": False,
        "registrationTime": "2023-11-30T12:18:21",
        "showedUp": False,
    },
    {
        "categoryId": "B",
        "color": "000000",
        "entryId": 59,
        "licenceNo": 4526124,
        "markedAsPaid": False,
        "registrationTime": "2023-11-17T18:01:20",
        "showedUp": False,
    },
    {
        "categoryId": "F",
        "color": "FF0000",
        "entryId": 64,
        "licenceNo": 4526124,
        "markedAsPaid": False,
        "registrationTime": "2023-11-25T21:56:50",
        "showedUp": False,
    },
]

incorrect_registration_color_violation = {"licenceNo": 7886249, "categoryIds": ["1"]}
incorrect_registration_gender_points_violation = {
    "licenceNo": 4526124,
    "categoryIds": ["A"],
}
incorrect_registration_missing_player = {"licenceNo": 55555, "categoryIds": ["A"]}
incorrect_registrations_missing_json_fields = [
    {"categoryIds": ["A"]},
    {"licenceNo": 4526124},
]
incorrect_registration_empty_categories = {"licenceNo": 4526124, "categoryIds": []}
incorrect_registration_nonexisting_categories = {
    "licenceNo": 4526124,
    "categoryIds": ["A", "a", "b"],
}
