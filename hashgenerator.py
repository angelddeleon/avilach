from werkzeug.security import generate_password_hash

# Al crear/actualizar contraseñas:
hashed_pw = generate_password_hash("123456")
print(hashed_pw)

