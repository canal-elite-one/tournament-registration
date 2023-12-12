from datetime import datetime
from http import HTTPStatus
from tests.testing_data import get_players_by_categories_data, get_all_players_data

overall_correct_licence = 722370
overall_incorrect_licence = 555555

missing_licence_error = "No player with licence number"

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

correct_categories_response = {
    "categories": [
        {
            "alternateName": None,
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
            "alternateName": None,
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
            "alternateName": None,
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
            "alternateName": None,
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
    ],
}

correct_admin_set_categories = [(correct_categories, correct_categories_response)]

incorrect_categories_missing_categories_field = {}
incorrect_categories_missing_categories_field_error = (
    "json was missing 'categories' field. Categories were not set"
)

incorrect_categories_missing_badly_formatted_data = {
    "categories": [
        {
            "categoryId": "aa",
            "color": "#FF00000",
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
        {},
    ],
}

incorrect_categories_missing_badly_formatted_data_error = (
    "Some category data was missing or wrongly "
    "formatted. Categories were not set. {0: {"
    "'categoryId': ['Length must be 1.'], "
    "'color': ['Length must be 7.'], 'entryFee': ["
    "'Missing data for required field.']}, "
    "1: {'maxPlayers': ['Not a valid integer.']}, "
    "2: {'startTime': ['Missing data for required "
    "field.'], 'entryFee': ['Missing data for "
    "required field.'], 'rewardFirst': ['Missing data "
    "for required field.'], 'rewardSecond': ['Missing "
    "data for required field.'], 'rewardSemi': ["
    "'Missing data for required field.'], "
    "'maxPlayers': ['Missing data for required "
    "field.']}}"
)

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
incorrect_categories_duplicate_error = (
    "At least two categories have the same name. Categories were not set."
)

incorrect_admin_set_categories = [
    (
        incorrect_categories_missing_categories_field,
        incorrect_categories_missing_categories_field_error,
    ),
    (
        incorrect_categories_missing_badly_formatted_data,
        incorrect_categories_missing_badly_formatted_data_error,
    ),
    (incorrect_categories_duplicate, incorrect_categories_duplicate_error),
]

"""
For api_admin_make_payment
"""

correct_payment_pay_all = (
    4526124,
    {"categoryIds": ["B", "F"]},
    {
        "actualPaidNow": 14,
        "actualRemaining": 0,
        "allEntries": {"amount": 14, "categoryIds": ["B", "F"]},
        "leftToPay": {"amount": 0, "categoryIds": []},
        "paymentDiff": 0,
        "settledNow": {"amount": 14, "categoryIds": ["B", "F"]},
        "settledPreviously": {"amount": 0, "categoryIds": []},
    },
)

correct_payment_pay_partial = (
    4526124,
    {"categoryIds": ["B"]},
    {
        "actualPaidNow": 7,
        "actualRemaining": 7,
        "allEntries": {"amount": 14, "categoryIds": ["B", "F"]},
        "leftToPay": {"amount": 7, "categoryIds": ["F"]},
        "paymentDiff": 0,
        "settledNow": {"amount": 7, "categoryIds": ["B"]},
        "settledPreviously": {"amount": 0, "categoryIds": []},
    },
)

correct_payment_previously_paid = (
    5326002,
    {"categoryIds": ["B"]},
    {
        "actualPaidNow": 7,
        "actualRemaining": 0,
        "allEntries": {"amount": 14, "categoryIds": ["B", "G"]},
        "leftToPay": {"amount": 0, "categoryIds": []},
        "paymentDiff": 0,
        "settledNow": {"amount": 7, "categoryIds": ["B"]},
        "settledPreviously": {"amount": 7, "categoryIds": ["G"]},
    },
)

correct_payment_all_recap_positive = (
    722370,
    {"categoryIds": ["7"]},
    {
        "actualPaidNow": 7,
        "actualRemaining": 7,
        "allEntries": {"amount": 21, "categoryIds": ["A", "5", "7"]},
        "leftToPay": {"amount": 7, "categoryIds": ["5"]},
        "paymentDiff": 0,
        "settledNow": {"amount": 7, "categoryIds": ["7"]},
        "settledPreviously": {"amount": 7, "categoryIds": ["A"]},
    },
)

correct_payment_default_actual = (
    722370,
    {
        "categoryIds": ["7"],
        "actualPaid": 7,
    },
    {
        "actualPaidNow": 7,
        "actualRemaining": 7,
        "allEntries": {"amount": 21, "categoryIds": ["A", "5", "7"]},
        "leftToPay": {"amount": 7, "categoryIds": ["5"]},
        "paymentDiff": 0,
        "settledNow": {"amount": 7, "categoryIds": ["7"]},
        "settledPreviously": {"amount": 7, "categoryIds": ["A"]},
    },
)

correct_payment_nondefault_actual = (
    722370,
    {
        "categoryIds": ["7"],
        "actualPaid": 8,
    },
    {
        "actualPaidNow": 8,
        "actualRemaining": 6,
        "allEntries": {"amount": 21, "categoryIds": ["A", "5", "7"]},
        "leftToPay": {"amount": 7, "categoryIds": ["5"]},
        "paymentDiff": 1,
        "settledNow": {"amount": 7, "categoryIds": ["7"]},
        "settledPreviously": {"amount": 7, "categoryIds": ["A"]},
    },
)

correct_payment_nonzero_diff = (
    9426636,
    {"categoryIds": ["2"]},
    {
        "actualPaidNow": 6,
        "actualRemaining": 7,
        "allEntries": {"amount": 28, "categoryIds": ["D", "F", "2", "6"]},
        "leftToPay": {"amount": 7, "categoryIds": ["6"]},
        "paymentDiff": 0,
        "settledNow": {"amount": 7, "categoryIds": ["2"]},
        "settledPreviously": {"amount": 14, "categoryIds": ["D", "F"]},
    },
)

correct_payment_nonzero_diff_nondefault_actual = (
    9426636,
    {
        "categoryIds": ["2"],
        "actualPaid": 5,
    },
    {
        "actualPaidNow": 5,
        "actualRemaining": 8,
        "allEntries": {"amount": 28, "categoryIds": ["D", "F", "2", "6"]},
        "leftToPay": {"amount": 7, "categoryIds": ["6"]},
        "paymentDiff": -1,
        "settledNow": {"amount": 7, "categoryIds": ["2"]},
        "settledPreviously": {"amount": 14, "categoryIds": ["D", "F"]},
    },
)

correct_admin_make_payment = [
    correct_payment_pay_all,
    correct_payment_pay_partial,
    correct_payment_previously_paid,
    correct_payment_all_recap_positive,
    correct_payment_default_actual,
    correct_payment_nondefault_actual,
    correct_payment_nonzero_diff,
    correct_payment_nonzero_diff_nondefault_actual,
]

incorrect_payment_missing_categories_json_field = (
    5326002,
    {},
    "Missing 'categoryIds' field in json.",
)

incorrect_payment_duplicate_payment = (
    5326002,
    {"categoryIds": ["G"]},
    "Tried to make payment for some entries which were already paid for",
)

incorrect_payment_without_registration = (
    5326002,
    {"categoryIds": ["A"]},
    "Tried to pay the fee for some categories which did not exist,",
)

incorrect_admin_make_payment = [
    incorrect_payment_missing_categories_json_field,
    incorrect_payment_duplicate_payment,
    incorrect_payment_without_registration,
]

"""
For api_admin_delete_entries
"""

correct_delete_entries_all = (
    722370,
    {"categoryIds": ["A", "5", "7"]},
    {
        "bibNo": None,
        "club": "LE MANS SARTHE TENNIS DE TABLE",
        "email": "gzzduckcnh@kmgdxv.com",
        "firstName": "Dpwsaob",
        "gender": "F",
        "lastName": "ORHCWRNU",
        "licenceNo": 722370,
        "nbPoints": 689,
        "paymentDiff": 0,
        "phone": "+336769763133",
        "registeredEntries": [],
    },
)

correct_delete_entries_partial = (
    722370,
    {"categoryIds": ["A", "5"]},
    {
        "bibNo": None,
        "club": "LE MANS SARTHE TENNIS DE TABLE",
        "email": "gzzduckcnh@kmgdxv.com",
        "firstName": "Dpwsaob",
        "gender": "F",
        "lastName": "ORHCWRNU",
        "licenceNo": 722370,
        "nbPoints": 689,
        "paymentDiff": 0,
        "phone": "+336769763133",
        "registeredEntries": [
            {
                "categoryId": "7",
                "licenceNo": 722370,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "registrationTime": "2023-09-17T05:10:51",
            },
        ],
    },
)

correct_admin_delete_entries = [
    correct_delete_entries_all,
    correct_delete_entries_partial,
]

incorrect_delete_entries_missing_categories_json_field = (
    722370,
    {},
    "Missing 'categoryIds' field in json.",
)

incorrect_delete_entries_nonexisting_player = (
    overall_incorrect_licence,
    {"categoryIds": ["A", "5"]},
    missing_licence_error,
)

incorrect_delete_entries_nonexisting_categories = (
    722370,
    {"categoryIds": ["P", "5"]},
    "Tried to delete some entries which were not registered",
)

incorrect_delete_entries_nonexisting_entries = (
    722370,
    {"categoryIds": ["B", "5"]},
    "Tried to delete some entries which were not registered",
)

incorrect_admin_delete_entries = [
    incorrect_delete_entries_missing_categories_json_field,
    incorrect_delete_entries_nonexisting_player,
    incorrect_delete_entries_nonexisting_categories,
    incorrect_delete_entries_nonexisting_entries,
]

"""
For api_admin_delete_player
"""

# See at top

"""
For api_admin_mark_present
"""

correct_mark_present_default = (
    4526124,
    {},
    {
        "bibNo": None,
        "club": "USM OLIVET TENNIS DE TABLE",
        "email": "nvzhltrsqr@mochsf.com",
        "firstName": "Wihelbl",
        "gender": "F",
        "lastName": "EZWLKRWE",
        "licenceNo": 4526124,
        "nbPoints": 1149,
        "paymentDiff": 0,
        "phone": "+336919756238",
        "registeredEntries": [
            {
                "categoryId": "B",
                "licenceNo": 4526124,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "registrationTime": "2023-11-17T18:01:20",
            },
            {
                "categoryId": "F",
                "licenceNo": 4526124,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "registrationTime": "2023-11-25T21:56:50",
            },
        ],
    },
)

correct_mark_present_nondefault = (
    4526124,
    {"categoryIdsToMark": ["B"]},
    {
        "bibNo": None,
        "club": "USM OLIVET TENNIS DE TABLE",
        "email": "nvzhltrsqr@mochsf.com",
        "firstName": "Wihelbl",
        "gender": "F",
        "lastName": "EZWLKRWE",
        "licenceNo": 4526124,
        "nbPoints": 1149,
        "paymentDiff": 0,
        "phone": "+336919756238",
        "registeredEntries": [
            {
                "categoryId": "B",
                "licenceNo": 4526124,
                "markedAsPaid": False,
                "markedAsPresent": True,
                "registrationTime": "2023-11-17T18:01:20",
            },
            {
                "categoryId": "F",
                "licenceNo": 4526124,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "registrationTime": "2023-11-25T21:56:50",
            },
        ],
    },
)

correct_unmark_present = (
    608834,
    {"categoryIdsToUnmark": ["E"]},
    {
        "bibNo": None,
        "club": "U S ETREPAGNY T T",
        "email": "wihnpztoim@tjbnck.com",
        "firstName": "Nxovesf",
        "gender": "F",
        "lastName": "GZLDPNEH",
        "licenceNo": 608834,
        "nbPoints": 1721,
        "paymentDiff": 0,
        "phone": "+336044431914",
        "registeredEntries": [
            {
                "categoryId": "E",
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "registrationTime": "2023-11-02T18:50:24",
            },
            {
                "categoryId": "G",
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "registrationTime": "2023-08-23T06:56:51",
            },
            {
                "categoryId": "3",
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "registrationTime": "2023-03-20T00:24:12",
            },
        ],
    },
)

correct_mark_unmark_present = (
    608834,
    {
        "categoryIdsToMark": ["3"],
        "categoryIdsToUnmark": ["E"],
    },
    {
        "bibNo": None,
        "club": "U S ETREPAGNY T T",
        "email": "wihnpztoim@tjbnck.com",
        "firstName": "Nxovesf",
        "gender": "F",
        "lastName": "GZLDPNEH",
        "licenceNo": 608834,
        "nbPoints": 1721,
        "paymentDiff": 0,
        "phone": "+336044431914",
        "registeredEntries": [
            {
                "categoryId": "E",
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "registrationTime": "2023-11-02T18:50:24",
            },
            {
                "categoryId": "G",
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "registrationTime": "2023-08-23T06:56:51",
            },
            {
                "categoryId": "3",
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": True,
                "registrationTime": "2023-03-20T00:24:12",
            },
        ],
    },
)

correct_mark_present_idempotent = (
    608834,
    {
        "categoryIdsToMark": ["3", "E"],
    },
    {
        "bibNo": None,
        "club": "U S ETREPAGNY T T",
        "email": "wihnpztoim@tjbnck.com",
        "firstName": "Nxovesf",
        "gender": "F",
        "lastName": "GZLDPNEH",
        "licenceNo": 608834,
        "nbPoints": 1721,
        "paymentDiff": 0,
        "phone": "+336044431914",
        "registeredEntries": [
            {
                "categoryId": "E",
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": True,
                "registrationTime": "2023-11-02T18:50:24",
            },
            {
                "categoryId": "G",
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "registrationTime": "2023-08-23T06:56:51",
            },
            {
                "categoryId": "3",
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": True,
                "registrationTime": "2023-03-20T00:24:12",
            },
        ],
    },
)

correct_admin_mark_present = [
    correct_mark_present_default,
    correct_mark_present_nondefault,
    correct_unmark_present,
    correct_mark_unmark_present,
    correct_mark_present_idempotent,
]

incorrect_mark_present_nonexisting_player = (
    overall_incorrect_licence,
    {},
    missing_licence_error,
)

incorrect_mark_present_nonexisting_category = (
    overall_correct_licence,
    {
        "categoryIdsToMark": ["FF"],
    },
    "Tried to mark/unmark player for categories which he was not ",
)

incorrect_mark_present_unregistered_category = (
    overall_correct_licence,
    {
        "categoryIdsToMark": ["B"],
    },
    "Tried to mark/unmark player for categories which he was not ",
)

incorrect_mark_present_mark_unmark_same_id = (
    608834,
    {
        "categoryIdsToMark": ["E"],
        "categoryIdsToUnmark": ["E"],
    },
    "Tried to mark and unmark player as present for same categories:",
)

incorrect_admin_mark_present = [
    incorrect_mark_present_nonexisting_player,
    incorrect_mark_present_nonexisting_category,
    incorrect_mark_present_unregistered_category,
    incorrect_mark_present_mark_unmark_same_id,
]

"""
For api_admin_assign_all_bibs
"""

correct_admin_assign_all_response = [
    {"bib_no": 1, "licence_no": 722370},
    {"bib_no": 2, "licence_no": 4527982},
    {"bib_no": 3, "licence_no": 4529052},
    {"bib_no": 4, "licence_no": 4529894},
    {"bib_no": 5, "licence_no": 4530487},
    {"bib_no": 6, "licence_no": 4530898},
    {"bib_no": 7, "licence_no": 4531022},
    {"bib_no": 8, "licence_no": 5326610},
    {"bib_no": 9, "licence_no": 5327529},
    {"bib_no": 10, "licence_no": 5328103},
    {"bib_no": 11, "licence_no": 5328211},
    {"bib_no": 12, "licence_no": 7216286},
    {"bib_no": 13, "licence_no": 7216475},
    {"bib_no": 14, "licence_no": 7218408},
    {"bib_no": 15, "licence_no": 7219314},
    {"bib_no": 16, "licence_no": 7222777},
    {"bib_no": 17, "licence_no": 7223406},
    {"bib_no": 18, "licence_no": 7224166},
    {"bib_no": 19, "licence_no": 7225053},
    {"bib_no": 20, "licence_no": 7225133},
    {"bib_no": 21, "licence_no": 7225209},
    {"bib_no": 22, "licence_no": 9239990},
    {"bib_no": 23, "licence_no": 9240480},
    {"bib_no": 24, "licence_no": 9245676},
    {"bib_no": 25, "licence_no": 9256721},
    {"bib_no": 26, "licence_no": 9321954},
    {"bib_no": 27, "licence_no": 9322263},
    {"bib_no": 28, "licence_no": 9323439},
    {"bib_no": 29, "licence_no": 9324241},
    {"bib_no": 30, "licence_no": 9538603},
    {"bib_no": 31, "licence_no": 723342},
    {"bib_no": 32, "licence_no": 725492},
    {"bib_no": 33, "licence_no": 2814398},
    {"bib_no": 34, "licence_no": 3525635},
    {"bib_no": 35, "licence_no": 3712439},
    {"bib_no": 36, "licence_no": 3714960},
    {"bib_no": 37, "licence_no": 3726270},
    {"bib_no": 38, "licence_no": 3727700},
    {"bib_no": 39, "licence_no": 3727799},
    {"bib_no": 40, "licence_no": 3731597},
    {"bib_no": 41, "licence_no": 3731932},
    {"bib_no": 42, "licence_no": 4111546},
    {"bib_no": 43, "licence_no": 4422906},
    {"bib_no": 44, "licence_no": 4435747},
    {"bib_no": 45, "licence_no": 4451551},
    {"bib_no": 46, "licence_no": 4462320},
    {"bib_no": 47, "licence_no": 4519318},
    {"bib_no": 48, "licence_no": 4526124},
    {"bib_no": 49, "licence_no": 4527177},
    {"bib_no": 50, "licence_no": 4527511},
    {"bib_no": 51, "licence_no": 4529851},
    {"bib_no": 52, "licence_no": 4532589},
    {"bib_no": 53, "licence_no": 4935234},
    {"bib_no": 54, "licence_no": 4939159},
    {"bib_no": 55, "licence_no": 5324235},
    {"bib_no": 56, "licence_no": 5324871},
    {"bib_no": 57, "licence_no": 5325321},
    {"bib_no": 58, "licence_no": 5326002},
    {"bib_no": 59, "licence_no": 5326543},
    {"bib_no": 60, "licence_no": 5327528},
    {"bib_no": 61, "licence_no": 5327901},
    {"bib_no": 62, "licence_no": 7213526},
    {"bib_no": 63, "licence_no": 7217048},
    {"bib_no": 64, "licence_no": 7217573},
    {"bib_no": 65, "licence_no": 7219370},
    {"bib_no": 66, "licence_no": 7219491},
    {"bib_no": 67, "licence_no": 7512693},
    {"bib_no": 68, "licence_no": 7874062},
    {"bib_no": 69, "licence_no": 7884741},
    {"bib_no": 70, "licence_no": 9137160},
    {"bib_no": 71, "licence_no": 9145837},
    {"bib_no": 72, "licence_no": 9221871},
    {"bib_no": 73, "licence_no": 9241901},
    {"bib_no": 74, "licence_no": 9247952},
    {"bib_no": 75, "licence_no": 9256846},
    {"bib_no": 76, "licence_no": 9311764},
    {"bib_no": 77, "licence_no": 798720},
    {"bib_no": 78, "licence_no": 1425307},
    {"bib_no": 79, "licence_no": 4529838},
    {"bib_no": 80, "licence_no": 7216648},
    {"bib_no": 81, "licence_no": 7527624},
    {"bib_no": 82, "licence_no": 9536504},
    {"bib_no": 83, "licence_no": 1420954},
    {"bib_no": 84, "licence_no": 4528713},
    {"bib_no": 85, "licence_no": 4529053},
    {"bib_no": 86, "licence_no": 4530477},
    {"bib_no": 87, "licence_no": 5327437},
    {"bib_no": 88, "licence_no": 7218763},
    {"bib_no": 89, "licence_no": 7223032},
    {"bib_no": 90, "licence_no": 7224029},
    {"bib_no": 91, "licence_no": 7525173},
    {"bib_no": 92, "licence_no": 7886249},
    {"bib_no": 93, "licence_no": 7887928},
    {"bib_no": 94, "licence_no": 9242977},
    {"bib_no": 95, "licence_no": 9252435},
    {"bib_no": 96, "licence_no": 9257964},
    {"bib_no": 97, "licence_no": 9321828},
    {"bib_no": 98, "licence_no": 9321971},
    {"bib_no": 99, "licence_no": 9426636},
    {"bib_no": 100, "licence_no": 61624},
    {"bib_no": 101, "licence_no": 608834},
    {"bib_no": 102, "licence_no": 3537537},
    {"bib_no": 103, "licence_no": 4427928},
    {"bib_no": 104, "licence_no": 4455748},
    {"bib_no": 105, "licence_no": 4526611},
    {"bib_no": 106, "licence_no": 5318378},
    {"bib_no": 107, "licence_no": 5324922},
    {"bib_no": 108, "licence_no": 5325044},
    {"bib_no": 109, "licence_no": 5325506},
    {"bib_no": 110, "licence_no": 5325784},
    {"bib_no": 111, "licence_no": 5325867},
    {"bib_no": 112, "licence_no": 5327556},
    {"bib_no": 113, "licence_no": 5615415},
    {"bib_no": 114, "licence_no": 5953737},
    {"bib_no": 115, "licence_no": 6021038},
    {"bib_no": 116, "licence_no": 6021265},
    {"bib_no": 117, "licence_no": 7214582},
    {"bib_no": 118, "licence_no": 7218004},
    {"bib_no": 119, "licence_no": 7221154},
    {"bib_no": 120, "licence_no": 7221254},
    {"bib_no": 121, "licence_no": 7222110},
    {"bib_no": 122, "licence_no": 9143724},
    {"bib_no": 123, "licence_no": 9457149},
    {"bib_no": 124, "licence_no": 9532616},
    {"bib_no": 125, "licence_no": 914291},
    {"bib_no": 126, "licence_no": 7220549},
    {"bib_no": 127, "licence_no": 7731399},
    {"bib_no": 128, "licence_no": 9410780},
    {"bib_no": 129, "licence_no": 3524722},
    {"bib_no": 130, "licence_no": 7219456},
    {"bib_no": 131, "licence_no": 7221275},
    {"bib_no": 132, "licence_no": 7210055},
    {"bib_no": 133, "licence_no": 7214813},
    {"bib_no": 134, "licence_no": 7221748},
]

incorrect_admin_assign_all_already_assigned_error = (
    "Some bib numbers are already assigned. Either assign"
)

"""
For api_admin_assign_one_bib
"""

correct_admin_assign_one = 9311764
correct_assign_one_response = {
    "bibNo": 3,
    "club": "BOURGETIN CTT",
    "email": "jfwxtzrmij@wnspze.com",
    "firstName": "Feitzmx",
    "gender": "F",
    "lastName": "ABJNNQES",
    "licenceNo": 9311764,
    "nbPoints": 1287,
    "paymentDiff": 0,
    "phone": "+336983296275",
}

incorrect_admin_assign_one_without_any_assigned_error = (
    "Cannot assign bib numbers manually before having assigned them in bulk"
)

incorrect_admin_assign_one_already_assigned = (
    722370,
    "This player already has a bib assigned.",
    HTTPStatus.CONFLICT,
)

incorrect_admin_assign_one = [
    incorrect_admin_assign_one_already_assigned,
]

"""
For api_admin_reset_all_bibs
"""

correct_admin_reset_all_bibs = {"confirmation": "Je suis sur! J'ai appelé Céline!"}

"""
For api_admin_get_players_by_category
"""

correct_admin_get_by_cat_response = get_players_by_categories_data.data
correct_admin_get_by_cat_present_only_response = {
    "1": [],
    "2": [],
    "3": [],
    "4": [],
    "5": [],
    "6": [
        {
            "bibNo": None,
            "club": "CABOURG TT",
            "email": "stbznywcnu@orabso.com",
            "firstName": "Smbhrdm",
            "gender": "F",
            "lastName": "KIGTDPBH",
            "licenceNo": 1420954,
            "nbPoints": 1019,
            "paymentDiff": 0,
            "phone": "+336318836582",
        },
    ],
    "7": [],
    "A": [],
    "B": [],
    "C": [],
    "D": [
        {
            "bibNo": None,
            "club": "CABOURG TT",
            "email": "stbznywcnu@orabso.com",
            "firstName": "Smbhrdm",
            "gender": "F",
            "lastName": "KIGTDPBH",
            "licenceNo": 1420954,
            "nbPoints": 1019,
            "paymentDiff": 0,
            "phone": "+336318836582",
        },
    ],
    "E": [
        {
            "bibNo": None,
            "club": "U S ETREPAGNY T T",
            "email": "wihnpztoim@tjbnck.com",
            "firstName": "Nxovesf",
            "gender": "F",
            "lastName": "GZLDPNEH",
            "licenceNo": 608834,
            "nbPoints": 1721,
            "paymentDiff": 0,
            "phone": "+336044431914",
        },
    ],
    "F": [
        {
            "bibNo": None,
            "club": "CABOURG TT",
            "email": "stbznywcnu@orabso.com",
            "firstName": "Smbhrdm",
            "gender": "F",
            "lastName": "KIGTDPBH",
            "licenceNo": 1420954,
            "nbPoints": 1019,
            "paymentDiff": 0,
            "phone": "+336318836582",
        },
    ],
    "G": [],
}

"""
For api_admin_get_all_players
"""

correct_admin_get_all_players_response = get_all_players_data.data

correct_admin_get_all_players_present_only_response = {
    "players": [
        {
            "bibNo": None,
            "club": "CABOURG TT",
            "email": "stbznywcnu@orabso.com",
            "firstName": "Smbhrdm",
            "gender": "F",
            "lastName": "KIGTDPBH",
            "licenceNo": 1420954,
            "nbPoints": 1019,
            "paymentDiff": 0,
            "phone": "+336318836582",
            "registeredEntries": [
                {
                    "categoryId": "D",
                    "licenceNo": 1420954,
                    "markedAsPaid": True,
                    "markedAsPresent": True,
                    "registrationTime": "2023-04-05T02:14:15",
                },
                {
                    "categoryId": "F",
                    "licenceNo": 1420954,
                    "markedAsPaid": False,
                    "markedAsPresent": True,
                    "registrationTime": "2023-09-05T10:40:48",
                },
                {
                    "categoryId": "2",
                    "licenceNo": 1420954,
                    "markedAsPaid": False,
                    "markedAsPresent": False,
                    "registrationTime": "2023-10-14T10:17:16",
                },
                {
                    "categoryId": "6",
                    "licenceNo": 1420954,
                    "markedAsPaid": True,
                    "markedAsPresent": True,
                    "registrationTime": "2023-11-24T05:36:23",
                },
            ],
        },
        {
            "bibNo": None,
            "club": "U S ETREPAGNY T T",
            "email": "wihnpztoim@tjbnck.com",
            "firstName": "Nxovesf",
            "gender": "F",
            "lastName": "GZLDPNEH",
            "licenceNo": 608834,
            "nbPoints": 1721,
            "paymentDiff": 0,
            "phone": "+336044431914",
            "registeredEntries": [
                {
                    "categoryId": "E",
                    "licenceNo": 608834,
                    "markedAsPaid": False,
                    "markedAsPresent": True,
                    "registrationTime": "2023-11-02T18:50:24",
                },
                {
                    "categoryId": "G",
                    "licenceNo": 608834,
                    "markedAsPaid": False,
                    "markedAsPresent": False,
                    "registrationTime": "2023-08-23T06:56:51",
                },
                {
                    "categoryId": "3",
                    "licenceNo": 608834,
                    "markedAsPaid": False,
                    "markedAsPresent": False,
                    "registrationTime": "2023-03-20T00:24:12",
                },
            ],
        },
    ],
}

"""
For api_get_categories
"""

correct_get_categories_response = {
    "categories": [
        {
            "alternateName": None,
            "categoryId": "A",
            "color": "#000000",
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
            "alternateName": None,
            "categoryId": "B",
            "color": "#000000",
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
            "alternateName": None,
            "categoryId": "C",
            "color": "#00FF00",
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
            "alternateName": None,
            "categoryId": "D",
            "color": "#00FF00",
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
            "alternateName": None,
            "categoryId": "E",
            "color": "#FF0000",
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
            "alternateName": None,
            "categoryId": "F",
            "color": "#FF0000",
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
            "alternateName": None,
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
            "alternateName": None,
            "categoryId": "1",
            "color": "#0000FF",
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
            "alternateName": None,
            "categoryId": "2",
            "color": "#0000FF",
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
            "alternateName": None,
            "categoryId": "3",
            "color": "#FFFF00",
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
            "alternateName": None,
            "categoryId": "4",
            "color": "#FFFF00",
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
            "alternateName": None,
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
            "alternateName": None,
            "categoryId": "6",
            "color": "#00FFFF",
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
            "alternateName": None,
            "categoryId": "7",
            "color": "#00FFFF",
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
    ],
}

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

correct_add_player = [(correct_player, correct_player_response)]

incorrect_player_missing_player_json_field = {}
incorrect_player_missing_player_json_field_error = (
    "json was missing 'player' field. Player was not added."
)

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
incorrect_player_missing_badly_formatted_data_error = (
    "Some player data was missing or wrongly formatted. Player was not added."
)

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
incorrect_player_duplicate_error = (
    "A player with this licence already exists in the database. Player "
)

incorrect_add_player = [
    (
        incorrect_player_missing_player_json_field,
        incorrect_player_missing_player_json_field_error,
    ),
    (
        incorrect_player_missing_badly_formatted_data,
        incorrect_player_missing_badly_formatted_data_error,
    ),
    (incorrect_player_duplicate, incorrect_player_duplicate_error),
]

"""
For api_get_player
"""

correct_get_player_existing = (
    4526124,
    {
        "bibNo": None,
        "club": "USM OLIVET TENNIS DE TABLE",
        "email": "nvzhltrsqr@mochsf.com",
        "firstName": "Wihelbl",
        "gender": "F",
        "lastName": "EZWLKRWE",
        "licenceNo": 4526124,
        "nbPoints": 1149,
        "paymentDiff": 0,
        "phone": "+336919756238",
        "registeredEntries": [
            {
                "categoryId": "B",
                "licenceNo": 4526124,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "registrationTime": "2023-11-17T18:01:20",
            },
            {
                "categoryId": "F",
                "licenceNo": 4526124,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "registrationTime": "2023-11-25T21:56:50",
            },
        ],
    },
)

correct_get_player_nonexisting = (
    overall_incorrect_licence,
    {"player": None, "registeredEntries": []},
)

correct_get_player = [
    correct_get_player_existing,
    correct_get_player_nonexisting,
]

incorrect_get_player = []

"""
For api_register_entries
"""

correct_registration = (
    4526124,
    {"categoryIds": ["1"]},
    [
        {
            "categoryId": "B",
            "color": "#000000",
            "entryId": 59,
            "licenceNo": 4526124,
            "markedAsPaid": False,
            "registrationTime": "2023-11-17T18:01:20",
            "markedAsPresent": False,
        },
        {
            "categoryId": "F",
            "color": "#FF0000",
            "entryId": 64,
            "licenceNo": 4526124,
            "markedAsPaid": False,
            "registrationTime": "2023-11-25T21:56:50",
            "markedAsPresent": False,
        },
        {
            "categoryId": "1",
            "color": "#0000FF",
            "entryId": 353,
            "licenceNo": 4526124,
            "markedAsPaid": False,
            "registrationTime": "2023-11-30T12:18:21",
            "markedAsPresent": False,
        },
    ],
)

correct_registration_with_duplicates = (
    4526124,
    {
        "categoryIds": ["1", "B", "F"],
    },
    [
        {
            "categoryId": "B",
            "color": "#000000",
            "entryId": 59,
            "licenceNo": 4526124,
            "markedAsPaid": False,
            "registrationTime": "2023-11-17T18:01:20",
            "markedAsPresent": False,
        },
        {
            "categoryId": "F",
            "color": "#FF0000",
            "entryId": 64,
            "licenceNo": 4526124,
            "markedAsPaid": False,
            "registrationTime": "2023-11-25T21:56:50",
            "markedAsPresent": False,
        },
        {
            "categoryId": "1",
            "color": "#0000FF",
            "entryId": 353,
            "licenceNo": 4526124,
            "markedAsPaid": False,
            "registrationTime": "2023-11-30T12:18:21",
            "markedAsPresent": False,
        },
    ],
)

correct_register_entries = [
    correct_registration,
    correct_registration_with_duplicates,
]

incorrect_registration_color_violation = (
    7886249,
    {"categoryIds": ["1"]},
    "One or several potential entries violate color constraint.",
)

incorrect_registration_gender_points_violation = (
    4526124,
    {
        "categoryIds": ["A"],
    },
    "Tried to register some entries violating either gender or ",
)

incorrect_registration_missing_player = (
    55555,
    {"categoryIds": ["A"]},
    "No player with licence number",
)

incorrect_registrations_missing_categoryids_json_fields = (
    4526124,
    {},
    "Missing 'categoryIds' field in json.",
)

incorrect_registration_empty_categories = (
    4526124,
    {"categoryIds": []},
    "No categories to register entries in were sent.",
)

incorrect_registration_nonexisting_categories = (
    4526124,
    {
        "categoryIds": ["A", "a", "b"],
    },
    "No categories with the following categoryIds",
)

incorrect_register_entries = [
    incorrect_registration_color_violation,
    incorrect_registration_gender_points_violation,
    incorrect_registration_missing_player,
    incorrect_registrations_missing_categoryids_json_fields,
    incorrect_registration_empty_categories,
    incorrect_registration_nonexisting_categories,
]
