def read_expression():
    try:
        name = input("Digite o nome do arquivo do circuito: ")
        with open(name, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                print("O arquivo está vazio!")
                return None
            return content
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        return None

# Substituição dos operadores textuais por funções válidas
def replace_operators(expr):
    expr = expr.upper().replace("(", " ( ").replace(")", " ) ")
    tokens = expr.split()

    output = []

    binary_ops = {"AND": "and_", "OR": "or_", "NAND": "nand", "NOR": "nor", "XOR": "xor", "XNOR": "xnor"}
    unary_ops = {"NOT": "not_"}

    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token in unary_ops:
            if i + 1 < len(tokens):
                output.append(f"{unary_ops[token]}({tokens[i+1]})")
                i += 2
            else:
                output.append(f"{unary_ops[token]}(0)")
                i += 1

        elif token in binary_ops:
            if output and i + 1 < len(tokens):
                b = tokens[i+1]
                a = output.pop()
                output.append(f"{binary_ops[token]}({a},{b})")
                i += 2
            else:
                output.append("0")
                i += 1

        else:
            output.append(token)
            i += 1

    return " ".join(output)

# Funções equivalentes aos operadores lógicos
def safe_eval(expr, context):
    def and_(a, b): return int(a and b)
    def or_(a, b): return int(a or b)
    def not_(a): return int(not a)
    def nand(a, b): return int(not (a and b))
    def nor(a, b): return int(not (a or b))
    def xor(a, b): return int(a != b)
    def xnor(a, b): return int(a == b)

    local_ctx = {
        "and_": and_,
        "or_": or_,
        "not_": not_,
        "nand": nand,
        "nor": nor,
        "xor": xor,
        "xnor": xnor,
        **context
    }

    try: 
        compiled = compile(expr, '<string>', 'eval')
        return eval(compiled, {}, local_ctx)
    except Exception as e:
        print(f"Erro ao avaliar a expressão: {e}")
        return 0

# Geração da tabela verdade
def generate_table(expr, defects=None):
    expr = replace_operators(expr)
    vars = sorted(set(c for c in expr if c.isalpha() and c.isupper()))
    table = []

    for i in range(2 ** len(vars)):
        values = [(i >> bit) & 1 for bit in reversed(range(len(vars)))]
        context = dict(zip(vars, values))
        if defects:
            context.update(defects)

        try:
            result = safe_eval(expr, context)
        except Exception as e:
            print(f"Erro ao avaliar: {e}")
            result = 0

        table.append(values + [result])

    return vars, table

# Impressão da tabela
def print_table(vars, table, title):
    print(f"\n{title}:")
    print(" | ".join(vars + ["Saída"]))
    print("-" * (6 * len(vars)))
    for row in table:
        print(" | ".join(map(str, row)))

# Diagnóstico de defeitos
def find_defects(expr, expected, faulty, vars):
    possibilities = []
    
    for var in vars:
        defects = {var: 0}
        _, test_table = generate_table(expr, defects)
        if test_table == faulty:
            possibilities.append(defects)
        
        defects = {var: 1}
        _, test_table = generate_table(expr, defects)
        if test_table == faulty:
            possibilities.append(defects)
    
    if not possibilities:
        for i in range(len(vars)):
            for j in range(i+1, len(vars)):
                for val1 in [0, 1]:
                    for val2 in [0, 1]:
                        defects = {vars[i]: val1, vars[j]: val2}
                        _, test_table = generate_table(expr, defects)
                        if test_table == faulty:
                            possibilities.append(defects)
    
    return possibilities

# Exportação
def export_report(expr, vars, original, faulty, diagnoses, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Diagnóstico de Circuito\n")
        f.write("="*30 + "\n\n")
        f.write("Expressão: " + expr + "\n\n")

        f.write("Tabela Correta:\n")
        f.write(" | ".join(vars + ["Saída"]) + "\n")
        for row in original:
            f.write(" | ".join(str(v) for v in row) + "\n")

        f.write("\nTabela Defeituosa:\n")
        f.write(" | ".join(vars + ["Saída"]) + "\n")
        for row in faulty:
            f.write(" | ".join(str(v) for v in row) + "\n")

        f.write("\nPossíveis Defeitos:\n")
        if diagnoses:
            for d in diagnoses:
                f.write(str(d) + "\n")
        else:
            f.write("Nenhum defeito encontrado\n")

    print(f"\nRelatório salvo em: {output_file}")

# Execução principal
def main():
    expr = read_expression()
    if expr is None:
        print("Não foi possível ler a expressão.")
        return

    vars, original = generate_table(expr)
    print_table(vars, original, "Tabela Verdade Correta")

    defect_input = input("\nDefeitos simulados (ex: A=1,B=0 ou Enter): ").strip()
    defects = {}

    if defect_input:
        try:
            for item in defect_input.split(","):
                k, v = item.strip().split("=")
                defects[k.strip().upper()] = int(v.strip())
        except:
            print("Erro no formato dos defeitos.")

    _, faulty = generate_table(expr, defects if defects else None)
    print_table(vars, faulty, "Tabela Defeituosa")

    diagnoses = find_defects(expr, original, faulty, vars)

    output_file = input("\nNome do arquivo para salvar o relatório (.txt): ").strip()
    export_report(expr, vars, original, faulty, diagnoses, output_file)

if __name__ == "__main__": 
    main()