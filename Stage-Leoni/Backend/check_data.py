from pymongo import MongoClient

client = MongoClient('mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp')
db = client['LeoniApp']

print('=== UTILISATEURS ===')
users = list(db['users'].find({}, {'firstName': 1, 'lastName': 1, 'adresse1': 1, 'department': 1, 'location': 1}).limit(10))
for user in users:
    name = f"{user.get('firstName', '')} {user.get('lastName', '')}"
    email = user.get('adresse1', 'N/A') 
    dept = user.get('department', 'N/A')
    loc = user.get('location', 'N/A')
    print(f"  - {name} ({email}) - {dept}/{loc}")

print(f'\nTotal: {db["users"].count_documents({})} utilisateurs')

print('\n=== DEPARTEMENTS ===')
depts = list(db['departments'].find({}, {'name': 1, 'location': 1}).limit(10))
for dept in depts:
    print(f"  - {dept.get('name', 'N/A')} @ {dept.get('location', 'N/A')}")

print('\n=== LOCATIONS ===')
locs = list(db['locations'].find({}, {'name': 1}).limit(10))
for loc in locs:
    print(f"  - {loc.get('name', 'N/A')}")

client.close()
