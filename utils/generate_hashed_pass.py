from argon2 import PasswordHasher

ph = PasswordHasher()

def hash_password(password):
    return ph.hash(password)

def verify_password(stored_hash, provided_password):
    try:
        ph.verify(stored_hash, provided_password)
        return True
    except:
        return False

original_password = input("Enter a password to hash: ")
hashed_password = hash_password(original_password)
print(hashed_password)
print(verify_password(hashed_password, original_password))

# alexeydandy aliosa778
# sandubujor cabanos007
# ghenabujor bateasandu
# saneamagla skodasuperb
# nasteatiganescu test123
# nataliapavlovskaia volvoxc60
# viorelbostan utmbomba
# dimaciorba fcim123
# victoriasecret toyotachr
# alexis77 aliosastudent
# danacojocari daniela
# janetagrigoras janeta