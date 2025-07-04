import json
import random


def generate_fixtures():
    # Default password for all users: password123
    fixtures = []
    user_id = 1
    profile_id = 1

    # Real Bangladeshi names
    male_first_names = [
        "Luis",
        "José",
        "Carlos",
        "Juan",
        "Jorge",
        "Andrés",
        "Diego",
        "Javier",
        "Daniel",
        "David",
        "Santiago",
        "Mateo",
        "Sebastián",
        "Alejandro",
        "Fernando",
    ]

    male_last_names = [
        "Zambrano",
        "Sánchez",
        "López",
        "Rodríguez",
        "García",
        "Martínez",
        "Torres",
        "Vera",
        "Cabrera",
        "Mora",
        "Suárez",
        "Reyes",
        "Mendoza",
        "Castro",
        "Andrade",
    ]

    female_first_names = [
        "María",
        "Ana",
        "Sofía",
        "Camila",
        "Daniela",
        "Andrea",
        "Paola",
        "Gabriela",
        "Valentina",
        "Isabella",
        "Luciana",
        "Alejandra",
        "Fernanda",
        "Carolina",
        "Verónica",
    ]

    female_last_names = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Garcia",
        "Miller",
        "Davis",
        "Rodriguez",
        "Martinez",
        "Hernandez",
        "Lopez",
        "Gonzalez",
        "Wilson",
        "Anderson",
    ]

    specializations = [
        "Cardiologist",
        "Dermatologist",
        "Neurologist",
        "Pediatrician",
        "Orthopedic Surgeon",
        "Psychiatrist",
        "Gynecologist",
        "Dentist",
        "Ophthalmologist",
        "ENT Specialist",
    ]

    cities = [
        "Quito",
        "Guayaquil",
        "Cuenca",
        "Ambato",
        "Loja",
        "Manta",
        "Santo Domingo",
        "Ibarra",
        "Riobamba",
        "Portoviejo",
        "Machala",
        "Esmeraldas",
    ]

    divisions = [
        "Pichincha",
        "Guayas",
        "Azuay",
        "Tungurahua",
        "Loja",
        "Manabí",
        "Santo Domingo de los Tsáchilas",
        "Imbabura",
        "Chimborazo",
    ]

    # Generate 15 doctors
    for i in range(1, 16):
        # Randomly choose gender for doctor
        gender = random.choice(["male", "female"])
        if gender == "male":
            first_name = random.choice(male_first_names)
            last_name = random.choice(male_last_names)
        else:
            first_name = random.choice(female_first_names)
            last_name = random.choice(female_last_names)

        doctor_username = f"doctor{i}"
        doctor = {
            "model": "accounts.user",
            "fields": {
                "password": "pbkdf2_sha256$260000$HQyGxzxfOxv6nLKI8zF$w9Nmz1Rxm1fPY1HzJ2MU7MgKBfTJ1RfF3q9M1wJvXvQ=",  # "password123"
                "username": doctor_username,
                "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
                "first_name": first_name,
                "last_name": last_name,
                "role": "doctor",
                "is_active": True,
                "date_joined": "2023-01-01T00:00:00Z",
            },
        }
        fixtures.append(doctor)

        # Doctor Profile
        doctor_profile = {
            "model": "accounts.profile",
            "pk": profile_id,
            "fields": {
                "user": user_id,
                "phone": f"+880175{i:07d}",
                "dob": f"{random.randint(1960, 1990)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "about": f"MBBS from {random.choice(['Quito Medical College', 'Guayaquil Medical College', 'Cuenca Medical College', 'Ambato Medical College'])}. {random.randint(5, 20)} years of experience in {random.choice(specializations)}.",
                "specialization": random.choice(specializations),
                "gender": gender,
                "address": f"House {random.randint(1, 99)}, Road {random.randint(1, 15)}, Block {random.choice(['A', 'B', 'C', 'D', 'E'])}, {random.choice(['del Valle', 'San jose', 'san pedro', 'santa rosa', 'del Río'])}",
                "city": random.choice(cities),
                "state": random.choice(divisions),
                "postal_code": f"{random.randint(1000, 9999)}",
                "country": "Ecuador",
                "price_per_consultation": random.randint(500, 2000),
                "is_available": True,
            },
        }
        fixtures.append(doctor_profile)
        user_id += 1
        profile_id += 1

    # Generate 15 patients
    for i in range(1, 16):
        # Randomly choose gender for patient
        gender = random.choice(["male", "female"])
        if gender == "male":
            first_name = random.choice(male_first_names)
            last_name = random.choice(male_last_names)
        else:
            first_name = random.choice(female_first_names)
            last_name = random.choice(female_last_names)

        patient_username = f"patient{i}"
        patient = {
            "model": "accounts.user",
            "pk": user_id,
            "fields": {
                "password": "pbkdf2_sha256$260000$HQyGxzxfOxv6nLKI8zF$w9Nmz1Rxm1fPY1HzJ2MU7MgKBfTJ1RfF3q9M1wJvXvQ=",  # "password123"
                "username": patient_username,
                "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
                "first_name": first_name,
                "last_name": last_name,
                "role": "patient",
                "is_active": True,
                "date_joined": "2023-01-01T00:00:00Z",
            },
        }
        fixtures.append(patient)

        # Patient Profile
        blood_groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
        areas = [
            "Mohammadpur",
            "Mirpur",
            "Uttara",
            "Dhanmondi",
            "Gulshan",
            "Banani",
            "Badda",
            "Khilgaon",
        ]

        patient_profile = {
            "model": "accounts.profile",
            "pk": profile_id,
            "fields": {
                "user": user_id,
                "phone": f"+880185{i:07d}",
                "dob": f"{random.randint(1970, 2000)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "gender": gender,
                "address": f"Flat {random.randint(1,20)}A, House {random.randint(1, 99)}, Road {random.randint(1, 15)}, {random.choice(areas)}",
                "city": random.choice(cities),
                "state": random.choice(divisions),
                "postal_code": f"{random.randint(1000, 9999)}",
                "country": "Bangladesh",
                "blood_group": random.choice(blood_groups),
                "allergies": random.choice(
                    ["None", "Dust Allergy", "Food Allergy", "Drug Allergy"]
                ),
                "medical_conditions": random.choice(
                    ["None", "High Blood Pressure", "Diabetes", "Asthma"]
                ),
            },
        }
        fixtures.append(patient_profile)
        user_id += 1
        profile_id += 1

    # Write fixtures to file
    with open("fixtures/initial_data.json", "w") as f:
        json.dump(fixtures, f, indent=2)


if __name__ == "__main__":
    generate_fixtures()
