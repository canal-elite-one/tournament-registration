from datetime import datetime

correct_categories = {'categories': [{
    "categoryID": "a",
    "color": "#FF0000",
    "maxPoints": 1500,
    "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime("%Y-%m-%dT%H:%M:%S"),
    "entryFee": 10,
    "rewardFirst": 200,
    "rewardSecond": 100,
    "rewardSemi": 50,
    "maxPlayers": 40, },
    {"categoryID": "b",
     "color": "#FFFF00",
     "minPoints": 800,
     "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime("%Y-%m-%dT%H:%M:%S"),
     "entryFee": 20,
     "rewardFirst": 200,
     "rewardSecond": 100,
     "rewardSemi": 50,
     "maxPlayers": 40, },
    {"categoryID": "c",
     "color": "#FFFFFF",
     "minPoints": 800,
     "maxPoints": 2000,
     "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime("%Y-%m-%dT%H:%M:%S"),
     "womenOnly": True,
     "entryFee": 20,
     "rewardFirst": 200,
     "rewardSecond": 100,
     "rewardSemi": 50,
     "maxPlayers": 40,
     "overbookingPercentage": 10},
    {
        "categoryID": "d",
        "maxPoints": 1500,
        "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime("%Y-%m-%dT%H:%M:%S"),
        "entryFee": 10,
        "rewardFirst": 200,
        "rewardSecond": 100,
        "rewardSemi": 50,
        "maxPlayers": 40, }
]}

correct_categories_response = [
    {'categoryID': 'a', 'color': '#FF0000', 'entryFee': 10, 'maxPlayers': 40, 'maxPoints': 1500, 'minPoints': 0,
     'overbookingPercentage': 0, 'rewardFirst': 200, 'rewardQuarter': None, 'rewardSecond': 100, 'rewardSemi': 50,
     'startTime': '2023-12-20T10:00:00', 'womenOnly': False},
    {'categoryID': 'b', 'color': '#FFFF00', 'entryFee': 20, 'maxPlayers': 40, 'maxPoints': 4000, 'minPoints': 800,
     'overbookingPercentage': 0, 'rewardFirst': 200, 'rewardQuarter': None, 'rewardSecond': 100, 'rewardSemi': 50,
     'startTime': '2023-12-20T10:00:00', 'womenOnly': False},
    {'categoryID': 'c', 'color': '#FFFFFF', 'entryFee': 20, 'maxPlayers': 40, 'maxPoints': 2000, 'minPoints': 800,
     'overbookingPercentage': 10, 'rewardFirst': 200, 'rewardQuarter': None, 'rewardSecond': 100, 'rewardSemi': 50,
     'startTime': '2023-12-20T10:00:00', 'womenOnly': True},
    {'categoryID': 'd', 'color': None, 'entryFee': 10, 'maxPlayers': 40, 'maxPoints': 1500, 'minPoints': 0,
     'overbookingPercentage': 0, 'rewardFirst': 200, 'rewardQuarter': None, 'rewardSecond': 100, 'rewardSemi': 50,
     'startTime': '2023-12-20T10:00:00', 'womenOnly': False}]

incorrect_categories_missing_categories_field = {}

incorrect_categories_missing_badly_formatted_data = {'categories': [{
    "categoryID": "a",
    "color": "#FF0000",
    "maxPoints": 1500,
    "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime("%Y-%m-%dT%H:%M:%S"),
    "rewardFirst": 200,
    "rewardSecond": 100,
    "rewardSemi": 50,
    "maxPlayers": 40, },
    {"categoryID": "b",
     "color": "#FFFF00",
     "minPoints": 800,
     "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime("%Y-%m-%dT%H:%M:%S"),
     "entryFee": 20,
     "rewardFirst": 200,
     "rewardSecond": 100,
     "rewardSemi": 50,
     "maxPlayers": "aa", }]}

incorrect_categories_duplicate = {'categories': [{
    "categoryID": "a",
    "color": "#FF0000",
    "maxPoints": 1500,
    "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime("%Y-%m-%dT%H:%M:%S"),
    "entryFee": 10,
    "rewardFirst": 200,
    "rewardSecond": 100,
    "rewardSemi": 50,
    "maxPlayers": 40, },
    {"categoryID": "a",
     "color": "#FFFF00",
     "minPoints": 800,
     "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime("%Y-%m-%dT%H:%M:%S"),
     "entryFee": 20,
     "rewardFirst": 200,
     "rewardSecond": 100,
     "rewardSemi": 50,
     "maxPlayers": 40, }]}

correct_payment_pay_all = {'licenceNo': 4526124, 'categoryIDs': ['B', 'F']}
correct_payment_pay_all_response = {'allEntries': {'amount': 14, 'categoryIDs': ['B', 'F']},
                                    'leftToPay': {'amount': 0, 'categoryIDs': []},
                                    'paidNow': {'amount': 14, 'categoryIDs': ['B', 'F']},
                                    'previouslyPaid': {'amount': 0, 'categoryIDs': []}}

correct_payment_pay_partial = {'licenceNo': 4526124, 'categoryIDs': ['B']}
correct_payment_pay_partial_response = {'allEntries': {'amount': 14, 'categoryIDs': ['B', 'F']},
                                        'leftToPay': {'amount': 7, 'categoryIDs': ['F']},
                                        'paidNow': {'amount': 7, 'categoryIDs': ['B']},
                                        'previouslyPaid': {'amount': 0, 'categoryIDs': []}}

correct_payment_previously_paid = {'licenceNo': 5326002, 'categoryIDs': ['B']}
correct_payment_previously_paid_response = {'allEntries': {'amount': 14, 'categoryIDs': ['B', 'G']},
                                            'leftToPay': {'amount': 0, 'categoryIDs': []},
                                            'paidNow': {'amount': 7, 'categoryIDs': ['B']},
                                            'previouslyPaid': {'amount': 7, 'categoryIDs': ['G']}}

correct_payment_all_recap_positive = {'licenceNo': 722370, 'categoryIDs': ['7']}
correct_payment_all_recap_positive_response = {'allEntries': {'amount': 21, 'categoryIDs': ['A', '5', '7']},
                                               'leftToPay': {'amount': 7, 'categoryIDs': ['5']},
                                               'paidNow': {'amount': 7, 'categoryIDs': ['7']},
                                               'previouslyPaid': {'amount': 7, 'categoryIDs': ['A']}}

incorrect_payment_missing_json_field = {}

incorrect_payment_duplicate_payment = {'licenceNo': 5326002, 'categoryIDs': ['G']}

incorrect_payment_without_registration = {'licenceNo': 5326002, 'categoryIDs': ['A']}

correct_get_categories_response = [{'categoryID': 'A', 'color': '000000', 'entryCount': 30, 'entryFee': 7, 'maxPlayers': 72, 'maxPoints': 900,
          'minPoints': 0, 'overbookingPercentage': 20, 'rewardFirst': 70, 'rewardQuarter': None, 'rewardSecond': 35,
          'rewardSemi': 20, 'startTime': '2024-01-06T09:00:00', 'womenOnly': False},
         {'categoryID': 'B', 'color': '000000', 'entryCount': 46, 'entryFee': 7, 'maxPlayers': 72, 'maxPoints': 1500,
          'minPoints': 0, 'overbookingPercentage': 15, 'rewardFirst': 140, 'rewardQuarter': None, 'rewardSecond': 70,
          'rewardSemi': 35, 'startTime': '2024-01-06T10:15:00', 'womenOnly': False},
         {'categoryID': 'C', 'color': '00FF00', 'entryCount': 8, 'entryFee': 10, 'maxPlayers': 36, 'maxPoints': 4000,
          'minPoints': 1300, 'overbookingPercentage': 10, 'rewardFirst': 300, 'rewardQuarter': None,
          'rewardSecond': 150, 'rewardSemi': 75, 'startTime': '2024-01-06T11:30:00', 'womenOnly': True},
         {'categoryID': 'D', 'color': '00FF00', 'entryCount': 41, 'entryFee': 7, 'maxPlayers': 72, 'maxPoints': 1100,
          'minPoints': 0, 'overbookingPercentage': 20, 'rewardFirst': 100, 'rewardQuarter': None, 'rewardSecond': 50,
          'rewardSemi': 25, 'startTime': '2024-01-06T12:45:00', 'womenOnly': False},
         {'categoryID': 'E', 'color': 'FF0000', 'entryCount': 29, 'entryFee': 10, 'maxPlayers': 72, 'maxPoints': 4000,
          'minPoints': 1500, 'overbookingPercentage': 0, 'rewardFirst': 300, 'rewardQuarter': None, 'rewardSecond': 150,
          'rewardSemi': 75, 'startTime': '2024-01-06T14:00:00', 'womenOnly': False},
         {'categoryID': 'F', 'color': 'FF0000', 'entryCount': 36, 'entryFee': 7, 'maxPlayers': 72, 'maxPoints': 1300,
          'minPoints': 0, 'overbookingPercentage': 10, 'rewardFirst': 120, 'rewardQuarter': None, 'rewardSecond': 60,
          'rewardSemi': 30, 'startTime': '2024-01-06T15:00:00', 'womenOnly': False},
         {'categoryID': 'G', 'color': None, 'entryCount': 48, 'entryFee': 7, 'maxPlayers': 72, 'maxPoints': 1900,
          'minPoints': 0, 'overbookingPercentage': 15, 'rewardFirst': 180, 'rewardQuarter': None, 'rewardSecond': 90,
          'rewardSemi': 45, 'startTime': '2024-01-06T16:00:00', 'womenOnly': False},
         {'categoryID': '1', 'color': '0000FF', 'entryCount': 28, 'entryFee': 7, 'maxPlayers': 72, 'maxPoints': 1700,
          'minPoints': 0, 'overbookingPercentage': 20, 'rewardFirst': 170, 'rewardQuarter': None, 'rewardSecond': 85,
          'rewardSemi': 45, 'startTime': '2024-01-07T09:00:00', 'womenOnly': False},
         {'categoryID': '2', 'color': '0000FF', 'entryCount': 20, 'entryFee': 7, 'maxPlayers': 72, 'maxPoints': 1400,
          'minPoints': 0, 'overbookingPercentage': 0, 'rewardFirst': 130, 'rewardQuarter': None, 'rewardSecond': 65,
          'rewardSemi': 35, 'startTime': '2024-01-07T10:15:00', 'womenOnly': False},
         {'categoryID': '3', 'color': 'FFFF00', 'entryCount': 23, 'entryFee': 7, 'maxPlayers': 72, 'maxPoints': 2100,
          'minPoints': 0, 'overbookingPercentage': 30, 'rewardFirst': 200, 'rewardQuarter': None, 'rewardSecond': 100,
          'rewardSemi': 50, 'startTime': '2024-01-07T11:30:00', 'womenOnly': False},
         {'categoryID': '4', 'color': 'FFFF00', 'entryCount': 13, 'entryFee': 7, 'maxPlayers': 72, 'maxPoints': 1000,
          'minPoints': 0, 'overbookingPercentage': 20, 'rewardFirst': 90, 'rewardQuarter': None, 'rewardSecond': 45,
          'rewardSemi': 25, 'startTime': '2024-01-07T12:45:00', 'womenOnly': False},
         {'categoryID': '5', 'color': None, 'entryCount': 5, 'entryFee': 7, 'maxPlayers': 36, 'maxPoints': 1600,
          'minPoints': 0, 'overbookingPercentage': 20, 'rewardFirst': 150, 'rewardQuarter': None, 'rewardSecond': 75,
          'rewardSemi': 40, 'startTime': '2024-01-07T14:00:00', 'womenOnly': True},
         {'categoryID': '6', 'color': '00FFFF', 'entryCount': 15, 'entryFee': 7, 'maxPlayers': 72, 'maxPoints': 1200,
          'minPoints': 0, 'overbookingPercentage': 15, 'rewardFirst': 110, 'rewardQuarter': None, 'rewardSecond': 55,
          'rewardSemi': 30, 'startTime': '2024-01-07T15:00:00', 'womenOnly': False},
         {'categoryID': '7', 'color': '00FFFF', 'entryCount': 10, 'entryFee': 7, 'maxPlayers': 72, 'maxPoints': 800,
          'minPoints': 0, 'overbookingPercentage': 10, 'rewardFirst': 60, 'rewardQuarter': None, 'rewardSecond': 30,
          'rewardSemi': 15, 'startTime': '2024-01-07T16:00:00', 'womenOnly': False}]

correct_player = {'player': {"licenceNo": 555555,
                             "firstName": "Fjhgzg",
                             "lastName": "MHIHOBB",
                             "email": "dfqkjqpoe@aieop.com",
                             "phone": "33489653754",
                             "gender": "F",
                             "nbPoints": 1500,
                             "club": "USKB", }}

correct_player_response = {'bibNo': 135, 'club': 'USKB', 'email': 'dfqkjqpoe@aieop.com', 'firstName': 'Fjhgzg',
                           'gender': 'F',
                           'lastName': 'MHIHOBB', 'licenceNo': 555555, 'nbPoints': 1500, 'phone': '33489653754'}

incorrect_player_missing_player_json_field = {}

incorrect_player_missing_badly_formatted_data = {'player': {"licenceNo": 55555,
                                                            "lastName": "QSDJKFLQZ",
                                                            "email": "layceline@gmail.com",
                                                            "phone": "33688261003",
                                                            "gender": "F",
                                                            "nbPoints": 1500,
                                                            "club": "USKB", }}

incorrect_player_duplicate = {'player': {"licenceNo": 4526124,
                                         "firstName": 'Wihelbl',
                                         "lastName": 'EZWLKRWE',
                                         "email": 'nvzhltrsqr@mochsf.com',
                                         "phone": '+336919756238',
                                         "gender": 'F',
                                         "nbPoints": 1149,
                                         "club": 'USM OLIVET TENNIS DE TABLE'}}

correct_get_player_existing = {'licenceNo': 4526124}
correct_get_player_existing_response = {
    'player': {'bibNo': 94, 'club': 'USM OLIVET TENNIS DE TABLE', 'email': 'nvzhltrsqr@mochsf.com',
               'firstName': 'Wihelbl', 'gender': 'F', 'lastName': 'EZWLKRWE', 'licenceNo': 4526124, 'nbPoints': 1149,
               'phone': '+336919756238'}, 'registeredCategories': [
        {'categoryID': 'B', 'color': '000000', 'entryID': 59, 'licenceNo': 4526124, 'paid': False,
         'registrationTime': '2023-11-17T18:01:20', 'showedUp': False},
        {'categoryID': 'F', 'color': 'FF0000', 'entryID': 64, 'licenceNo': 4526124, 'paid': False,
         'registrationTime': '2023-11-25T21:56:50', 'showedUp': False}]}

correct_get_player_nonexisting = {'licenceNo': 555555}
correct_get_player_nonexisting_response = {'player': None, 'registeredCategories': []}

incorrect_get_player_missing_licenceNo_json_field = {}

correct_registration = {'licenceNo': 4526124, 'categoryIDs': ['1']}
correct_registration_response = [
    {'categoryID': '1', 'color': '0000FF', 'entryID': 353, 'licenceNo': 4526124, 'paid': False,
     'registrationTime': '2023-11-30T12:18:21', 'showedUp': False},
    {'categoryID': 'B', 'color': '000000', 'entryID': 59, 'licenceNo': 4526124, 'paid': False,
     'registrationTime': '2023-11-17T18:01:20', 'showedUp': False},
    {'categoryID': 'F', 'color': 'FF0000', 'entryID': 64, 'licenceNo': 4526124, 'paid': False,
     'registrationTime': '2023-11-25T21:56:50', 'showedUp': False}]

correct_registration_with_duplicates = {'licenceNo': 4526124, 'categoryIDs': ['1', 'B', 'F']}
correct_registration_with_duplicates_response = [
    {'categoryID': '1', 'color': '0000FF', 'entryID': 353, 'licenceNo': 4526124, 'paid': False,
     'registrationTime': '2023-11-30T12:18:21', 'showedUp': False},
    {'categoryID': 'B', 'color': '000000', 'entryID': 59, 'licenceNo': 4526124, 'paid': False,
     'registrationTime': '2023-11-17T18:01:20', 'showedUp': False},
    {'categoryID': 'F', 'color': 'FF0000', 'entryID': 64, 'licenceNo': 4526124, 'paid': False,
     'registrationTime': '2023-11-25T21:56:50', 'showedUp': False}]

incorrect_registration_color_violation = {'licenceNo': 7886249, 'categoryIDs': ['1']}
incorrect_registration_gender_points_violation = {'licenceNo': 4526124, 'categoryIDs': ['A']}
incorrect_registration_missing_player = {'licenceNo': 55555, 'categoryIDs': ['A']}
incorrect_registrations_missing_json_fields = [{'categoryIDs': ['A']}, {'licenceNo': 4526124}]
incorrect_registration_empty_categories = {'licenceNo': 4526124, 'categoryIDs': []}
incorrect_registration_nonexisting_categories = {'licenceNo': 4526124, 'categoryIDs': ['A', 'a', 'b']}
