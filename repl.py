from scanner import Scanner
from parser import Parser

def repl():
    print("REPL iniciado. Escribe 'salir' para terminar con el programa.\n")

    while True: 
        try:
            #aqui el prompt
            entrada= input(">>>").strip()

            #si escribe 'salir'
            if entrada.lower() == 'salir':
                print("Terminando ejecucion...")
                break

            #aquí se ejecuta el scanner
            scanner = Scanner(entrada)
            tokens, error = scanner.scan()

            #mostramos los tokens obtenidos
            print("TOKENS: ", tokens)

            #y si hubo algún error lexico se muestra y continua la ejecución del programa
            if error:
                print(f"Error Lexico: {error}")
                continue

            #aquí se ejecuta el analizador sintáctico
            parser=Parser(tokens)
            try:
                parser.parse()
            except SyntaxError as e:
                print(f"Error sintáctico: {e}")
        
        except KeyboardInterrupt:
            print("\nSaliendo...")
            break
        except EOFError:
            print("\nSaliendo...")
            break

if __name__ == "__main__":
    repl()