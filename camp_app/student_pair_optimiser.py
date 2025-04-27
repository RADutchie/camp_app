import re

import pulp
from rapidfuzz import fuzz, process


def clean_text(text):
    """
    Converts text to lowercase, strips leading/trailing whitespace,
    and replaces multiple whitespaces with a single space.
    """
    text = text.title().strip()
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    return text


def correct_names(preferences, main_students):
    # Dictionary to store corrected preferences
    corrected_preferences = {}

    # Iterate through each student and their preferences
    for student, prefs in preferences.items():
        corrected_prefs = []
        for pref in prefs:
            # Find the best match for the misspelt name in the main_students list
            best_match = process.extractOne(pref, main_students, scorer=fuzz.WRatio)
            if best_match and best_match[1] > 80:  # You can adjust the threshold score
                corrected_prefs.append(best_match[0])
            else:
                corrected_prefs.append(pref)  # If no good match, keep the original
        corrected_preferences[student] = corrected_prefs

    return corrected_preferences


def get_student_preferences(student_data):
    student_preferences = {}
    for index, row in student_data.iterrows():
        # Combine the first name and surname into a full name key
        full_name = f"{row['Your First Name']} {row['Your Surname']}".title().strip()
        # Collect all group choices into a list
        preferences = [
            clean_text(row['Choice 1 (First and Surname)']),
            clean_text(row['Choice 2 (First and Surname)']),
            clean_text(row['Choice 3 (First and Surname)']),
            clean_text(row['Choice 4 (First and Surname)']),
            clean_text(row['Choice 5 (First and Surname)'])
        ]
        preferences = [pref for pref in preferences if pref not in ('nan', '', 'Nan')]
        # Assign the list of preferences to the dictionary under the full name key
        student_preferences[full_name] = preferences

    main_students = set(student_preferences.keys())

    corrected_preferences = correct_names(student_preferences, main_students)

    return corrected_preferences, main_students


def check_for_missing_or_absent(corrected_preferences, main_students, not_attending):
    # Check if there are any students who are in preferences but not in the main student list
    # Gather all preferences into a single set
    all_preferences = set()
    for preferences in corrected_preferences.values():
        all_preferences.update(preferences)

    # Students who are in preferences but not in the main student list
    students_only_in_preferences = all_preferences - main_students

    students_only_in_preferences = [student for student in students_only_in_preferences if student not in not_attending]
    return students_only_in_preferences


def final_preferenceses_for_optimisation(corrected_preferences, students_only_in_preferences, not_attending, exclude=False):
    """
    Prepares the final preferences for optimisation by optionally excluding students only in preferences
    and removing students who are not attending. Also removes excluded students from the preference lists
    of other students.
    """
    final_preferences = {}

    # Combine all students to exclude
    excluded_students = set(not_attending)
    if exclude:
        excluded_students.update(students_only_in_preferences)

    # Iterate through corrected preferences
    for student, prefs in corrected_preferences.items():
        # Skip students who are excluded
        if student in excluded_students:
            continue

        # Remove excluded students from the preference list
        filtered_prefs = [pref for pref in prefs if pref not in excluded_students]
        final_preferences[student] = filtered_prefs

    # If exclude is False, add students only in preferences with empty preferences
    if not exclude:
        for student in students_only_in_preferences:
            if student not in final_preferences:
                final_preferences[student] = []

    return final_preferences


def solve_pairing(preferences):
    # Create a problem variable:
    prob = pulp.LpProblem("Student_Pairing", pulp.LpMaximize)

    # Create variables for each possible pair
    pairs = {}
    all_students = set(preferences.keys()) | set(pref for prefs in preferences.values() for pref in prefs)
    for student in all_students:
        for preferred in all_students:
            if student != preferred:  # Avoid pairing students with themselves
                pair_name = f"pair_{student}|{preferred}"
                pairs[(student, preferred)] = pulp.LpVariable(pair_name, 0, 1, pulp.LpBinary)

    # Objective function: maximize sum of mutual preferences
    prob += pulp.lpSum(pairs[(s, p)] * ((len(preferences[s]) +1 - preferences[s].index(p) if p in preferences[s] else 0.5) +
                                        (len(preferences[s]) +1 - preferences[p].index(s) if s in preferences[p] else 0.5))
                       for s in preferences for p in all_students if (s, p) in pairs)

    # Constraint: Each student can be in at most one pair
    for s in all_students:
        prob += pulp.lpSum(pairs[(s, p)] for p in all_students if (s, p) in pairs) + \
                pulp.lpSum(pairs[(p, s)] for p in all_students if (p, s) in pairs) <= 1

    # Solve the problem
    prob.solve()

    # Extract the pairs
    results = []
    seen = set()
    for (s, p), var in pairs.items():
        if pulp.value(var) == 1 and s not in seen and p not in seen:
            results.append((s, p))
            seen.update([s, p])

    return results


def students_not_paired(preferences, pairs):
    all_students = set(preferences.keys())

    paired = set()
    for first_name, second_name in pairs:
        paired.add(first_name)
        paired.add(second_name)

    not_paired = all_students - paired
    return not_paired