import ast
import resource
from flask import Flask, render_template, request, jsonify
from sympy import symbols, count_ops
from sympy.parsing.sympy_parser import parse_expr

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        code = request.json['code']
        return analyze_code(code)

def analyze_code(code):
    try:
        linhas_de_codigo = count_lines_of_code(code)
        num_funcoes = count_functions(code)
        num_classes = count_classes(code)
        num_metodos = count_methods(code)
        complexidade_ciclomatica = calculate_cyclomatic_complexity(code)
        num_imports = count_imports(code)
        contagem_palavras_chave = count_keywords(code)
        ops_aritmeticas, ops_logicas, ops_comparacao = count_operations(code)
        num_dependencias = count_dependencies(code)
        big_o = calculate_big_o(code)
        uso_memoria_gb = measure_memory_usage() / (1024.0 ** 2) # Convertendo bytes para gigabytes
        uso_cpu_sec = measure_cpu_usage()

        return jsonify({
            'success': True,
            'metrics': {
                'Linhas de codigo': linhas_de_codigo,
                'Funções': num_funcoes,
                'Metodos': num_metodos,
                'Complexidade ciclomatica': complexidade_ciclomatica,
                'Imports': num_imports,
                'Operações aritméticas': ops_aritmeticas,
                'Operações logicas': ops_logicas,
                'Operações comparação': ops_comparacao,
                'Dependencias': num_dependencias,
                'Big O': big_o,
                'Memoria (bytes)': uso_memoria_gb,
                'cpu': uso_cpu_sec
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

def count_lines_of_code(code):
    return len(code.split('\n'))

def count_functions(code):
    tree = ast.parse(code)
    return sum(isinstance(node, ast.FunctionDef) for node in tree.body)

def count_classes(code):
    tree = ast.parse(code)
    return sum(isinstance(node, ast.ClassDef) for node in tree.body)

def count_methods(code):
    tree = ast.parse(code)
    method_count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name != '__init__':
            method_count += 1
    return method_count

def calculate_cyclomatic_complexity(code):
    tree = ast.parse(code)
    return sum(1 for node in ast.walk(tree) if isinstance(node, (ast.For, ast.While, ast.If, ast.With, ast.Try))) + 1

def count_imports(code):
    tree = ast.parse(code)
    return sum(isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom) for node in tree.body)

def count_keywords(code):
    tree = ast.parse(code)
    keywords = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword):
            keyword = node.arg
            if keyword not in keywords:
                keywords[keyword] = 1
            else:
                keywords[keyword] += 1
    return keywords

def count_operations(code):
    tree = ast.parse(code)
    ops_aritmeticas = 0
    ops_logicas = 0
    ops_comparacao = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp):
            ops_aritmeticas += 1
        elif isinstance(node, ast.BoolOp):
            ops_logicas += 1
        elif isinstance(node, ast.Compare):
            ops_comparacao += 1
    return ops_aritmeticas, ops_logicas, ops_comparacao

def count_dependencies(code):
    tree = ast.parse(code)
    dependencias = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            dependencias.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            dependencias.add(node.module)
    return len(dependencias)

def calculate_big_o(code):
    tree = ast.parse(code)
    num_loops = 0
    num_conditionals = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.While)):
            num_loops += 1
        elif isinstance(node, ast.If):
            num_conditionals += 1
    return f"O(n^{num_loops})" if num_loops > 0 else "O(n)"

def measure_memory_usage():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

def measure_cpu_usage():
    return resource.getrusage(resource.RUSAGE_SELF).ru_utime + resource.getrusage(resource.RUSAGE_SELF).ru_stime

if __name__ == '__main__':
    app.run(debug=True)
