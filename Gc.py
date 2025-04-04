import secrets
import string

# Definir el alfabeto
letras = string.ascii_letters
digitos = string.digits
caracteres_especiales = string.punctuation

alfabeto = letras + digitos + caracteres_especiales

# Fijar longitud de la contraseña
print("Ingresa la cantidad de caracteres que deseas que tenga la contraseña")
n = int(input())  # Se obtiene la entrada del usuario y se convierte en entero
longitud_contraseña = n

# Generar una cadena de contraseña aleatoria
pwd = ''.join(secrets.choice(alfabeto) for _ in range(longitud_contraseña))
print("Contraseña aleatoria:", pwd)

# Generar contraseña que cumpla las restricciones
while True:
    pwd = ''.join(secrets.choice(alfabeto) for _ in range(longitud_contraseña))
    
    # Verificar restricciones
    if (any(char in caracteres_especiales for char in pwd) and 
        sum(char in digitos for char in pwd) >= 2):
        break

print("Contraseña con restricciones:", pwd)
