import secrets
import string
import time

# ✅ Paso 1: Genera una contraseña segura con alfabeto completo
def generar_contraseña(longitud):
    letras = string.ascii_letters
    digitos = string.digits
    especiales = string.punctuation
    alfabeto = letras + digitos + especiales

    while True:
        pwd = ''.join(secrets.choice(alfabeto) for _ in range(longitud))
        if any(c in especiales for c in pwd) and sum(c in digitos for c in pwd) >= 2:
            return pwd

# ✅ Paso 2: Pedir la longitud de la contraseña
def pedir_longitud():
    while True:
        try:
            n = int(input("🔢 ¿Cuántos caracteres quieres que tenga la contraseña?: "))
            if n < 4:
                print("🚫 Mínimo 4 caracteres.")
            else:
                return n
        except ValueError:
            print("⚠️ Eso no es un número válido.")

# ✅ Paso 3: Cifrado con visualización paso a paso
def cifrar_vigenere_visual(texto, clave):
    alfabeto = string.ascii_letters
    clave_expandida = (clave * (len(texto) // len(clave) + 1))[:len(texto)]
    cifrado = []

    print("\n🔒 PROCESO DE CIFRADO VIGENÈRE PASO A PASO\n")
    print("📘 Fórmula: (Letra_original + Letra_clave) % 26\n")

    for i, (t, k) in enumerate(zip(texto, clave_expandida)):
        if t in alfabeto:
            mayuscula = t.isupper()
            base = ord('A') if mayuscula else ord('a')

            t_val = ord(t) - base
            k_val = ord(k.lower()) - ord('a')
            cifrada_val = (t_val + k_val) % 26
            cifrada = chr(base + cifrada_val)

            print(f"[{i+1}] Letra original: {t}")
            print(f"     Clave        : {k}")
            print(f"     {t} ({t_val}) + {k.lower()} ({k_val}) = {cifrada_val} → {cifrada}\n")

            cifrado.append(cifrada)
        else:
            print(f"[{i+1}] '{t}' no es letra, se queda igual.")
            cifrado.append(t)

        time.sleep(0.4)

    resultado = ''.join(cifrado)
    print(f"\n🔐 Resultado final cifrado: {resultado}")
    return resultado

# ✅ Paso 4: Juego para descifrar tú mismo
def descifrado_manual_juego(cifrado, clave):
    alfabeto = string.ascii_letters
    clave_expandida = (clave * (len(cifrado) // len(clave) + 1))[:len(cifrado)]
    resultado = ""

    print("\n🎮 JUEGO DE DESCIFRADO MANUAL: Tú eres el agente secreto\n")
    print("📘 Fórmula: (Letra_cifrada - Letra_clave) % 26\n")

    for i, (c, k) in enumerate(zip(cifrado, clave_expandida)):
        if c in alfabeto:
            mayuscula = c.isupper()
            base = ord('A') if mayuscula else ord('a')

            c_val = ord(c) - base
            k_val = ord(k.lower()) - ord('a')
            correcta_val = (c_val - k_val) % 26
            correcta = chr(base + correcta_val)

            print(f"[{i+1}] Letra cifrada: {c}")
            print(f"     Clave       : {k}")
            print(f"     {c} ({c_val}) - {k.lower()} ({k_val}) = {correcta_val} → ???")
            intento = input("🎯 Tu intento: ").strip()

            if intento == correcta:
                print("✅ ¡Correcto!\n")
                resultado += intento
            else:
                print(f"❌ Incorrecto. La respuesta correcta era: {correcta}\n")
                resultado += correcta
        else:
            print(f"[{i+1}] '{c}' no se cifra. Se mantiene igual.\n")
            resultado += c
        time.sleep(0.4)

    print(f"\n🔓 Resultado final descifrado: {resultado}")
    return resultado

# 🧠 MAIN: Ejecución completa
if __name__ == "__main__":
    longitud = pedir_longitud()
    contraseña = generar_contraseña(longitud)
    clave = input("\n🔑 Ingresa una clave para cifrar con Vigenère (¡guárdala bien!): ")

    # 🔒 Mostrar proceso de cifrado visual
    contraseña_cifrada = cifrar_vigenere_visual(contraseña, clave)
    
    print("\n🎯 ¡Ahora es tu turno de descifrarla sin ver la original!")

    respuesta_usuario = descifrado_manual_juego(contraseña_cifrada, clave)

    if respuesta_usuario == contraseña:
        print("\n🏆 ¡Perfecto, Osito! Has descifrado la contraseña como todo un maestro.")
    else:
        print("\n🤖 Fallaste en algunas letras. ¡No te rindas, sigue entrenando!")

