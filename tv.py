truthTable = []
faultyTable = []

def read():
    archive = input('Digite o nome do arquivo do circuito: ')
    try:
        with open(archive, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        print('Arquivo não encontrado')
    except Exception as e:
        print(f'Erro ao ler o arquivo: {e}')

def generate_truth_table(expression, defects=None):
    table = []
    var = sorted(set([char for char in expression if char.isalpha() and char.isupper()]))
    bits = 2 ** len(var)

    for i in range(bits):
        values = [(i >> bit) & 1 for bit in reversed(range(len(var)))]
        context = dict(zip(var, values))
        
        if defects:
            for gate, value in defects.items():
                if gate in context:
                    context[gate] = value

        try:
            result = int(bool(eval(expression, {}, context)))
        except Exception as e:
            print(f'Erro ao avaliar: {e}')
            result = 0

        line = values + [result]
        table.append(line)
    
    return var, table

def print_table(variables, table, title):
    print(f"\n{title}:")
    print(" | ".join(variables + ["Saída"]))
    print("-" * (8 * len(variables)))
    for line in table:
        print(" | ".join(str(v) for v in line))

def find_defects(correct, faulty, variables, gates):
    from itertools import combinations, product
    
    possible = []
    max_defects = len(gates)
    
    for num in range(1, max_defects + 1):
        for gates_combo in combinations(gates, num):
            for values in product([0, 1], repeat=num):
                defects = dict(zip(gates_combo, values))
                _, test_table = generate_truth_table(expression, defects)
                if test_table == faulty:
                    possible.append(defects)
    
    return possible

def main():
    global expression
    expression = read()
    if not expression:
        return

    var, correct = generate_truth_table(expression)
    print_table(var, correct, "Circuito")

    while True:
        defect_input = input("\nDefeitos (ex: A=1,B=0 ou Enter para todos): ").strip()
        defects = {}
        
        if not defect_input:
            break
            
        try:
            items = defect_input.split(',')
            for item in items:
                gate, value = item.split('=')
                gate = gate.strip().upper()
                defects[gate] = int(value.strip())
            break
        except:
            print("Formato inválido. Use GATE=VALOR (ex: A=1)")

    _, faulty = generate_truth_table(expression, defects if defects else None)
    print_table(var, faulty, "Circuito Defeituoso")

    gates = sorted(set([char for char in expression if char.isalpha() and char.isupper()]))
    diagnoses = find_defects(correct, faulty, var, gates)

    output_file = input("\nArquivo de saída: ").strip()
    with open(output_file, 'w') as f:
        f.write("Diagnóstico de Defeitos\n")
        f.write("="*30 + "\n\n")
        f.write("Circuito: " + expression + "\n\n")
        
        f.write("Tabela:\n")
        f.write(" | ".join(var + ["Saída"]) + "\n")
        for line in correct:
            f.write(" | ".join(str(v) for v in line) + "\n")
        
        f.write("\nTabela Defeituosa:\n")
        f.write(" | ".join(var + ["Saída"]) + "\n")
        for line in faulty:
            f.write(" | ".join(str(v) for v in line) + "\n")
        
        f.write("\nPossíveis defeitos:\n")
        if not diagnoses:
            f.write("Nenhum defeito encontrado\n")
        else:
            for d in diagnoses:
                f.write(str(d) + "\n")

    print(f"\nDiagnóstico salvo em {output_file}")

if __name__ == "__main__":
    main()